from django.http.response import HttpResponse
from datetime import datetime
import telebot
import json
import threading
import time
import datetime
from .models import Start, log, Operators

chat_id = -1002003805171
token = "7156367176:AAHWf4T-36vtV8UjHjDDowYlRY--Myq1OFM"
webhook_url = "ТВОЙ IP"

bot = telebot.TeleBot(token)

def logs(username, userid, department, message_id, H, zone, punkt):
    current_datetime = datetime.datetime.now()
    current_date_iso = current_datetime.date().isoformat()
    time_now = current_datetime.time().strftime("%H:%M:%S")
    log_entry = log.objects.create(
                date=current_date_iso,
                time=time_now,
                who=username,
                teleid=userid,
                zone=zone,
                result=1,
                comment="+",
                department=department,
                H=H,
                punkt=punkt,
                message_id=message_id
            )

    log_entry.save()

def start_time():
    all_objects = Start.objects.values()
    # Цикл, который проходится по созданным переменным и отправляет кнопку "Принять"
    for i in all_objects:
        time_start = i["time_start"]
        time_start = time_start.strftime("%H:%M")
        group = i["group_id"]
        zone = i["zone"]  # название обхода
        department = i["department"]
        H = i["H"]
        time_now = datetime.datetime.now().time().strftime("%H:%M")
        print(time_now, time_start)
        # if time_now == time_start:  # Сравниваем текущее время с временем начала
        send_inspection(group, department, zone, H)
    time.sleep(60)


def send_inspection(group, department, zone, H):
    send_photo_button = telebot.types.InlineKeyboardButton("Принять", callback_data=f'claim:{department}:{H}')  # Создаёт кнопку "Принять"
    keyboard = telebot.types.InlineKeyboardMarkup().add(send_photo_button)  # Создаёт объект InlineKeyboardMarkup, встроенная клавиатура

    # Отправляет сообщение с кнопкой "Принять"
    bot.send_message(chat_id=chat_id, message_thread_id=group, text=f'{department} Вам пришел: {zone}', reply_markup=keyboard)


def set_webhook(request):
    s = bot.set_webhook(webhook_url + '/webhook/')
    if s:
        return HttpResponse("Ok")
    else:
        return HttpResponse("Error")


def webhook(request):
    if request.method == "POST":
        update = json.loads(request.body)
        bot.process_update(update)
        return HttpResponse(status=200)


@bot.message_handler()
def test_message(message):
    if message.from_user.id == message.chat.id:
        bot.reply_to(message, "Привет")
    return 200


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    userid = call.from_user.id
    username = call.from_user.username

    if call.data.startswith('claim'):
        parts = call.data.split(":")
        department = parts[1]#[0] это слово "claim"
        H = parts[2]
        bot.edit_message_text(f"@{call.from_user.username} Принял обход", chat_id=chat_id, message_id=call.message.id)
        logs(username=username, userid=userid, department=department, message_id=call.message.id, H=H, zone="Принял обход", punkt=1)
        # Человек принял обход и дальше мы запускаем функцию, которая будет проверять на каком пункте человек, и отправлять следующий пункт
        Next(userid, H, 1, username)

    elif call.data.startswith("accept"):
        bot.delete_message(userid, call.message.id)
        parts = call.data.split(":")
        # Ensure that call.data has the required parts
        H = parts[1]
        punkt = int(parts[2])
        all_operators = Operators.objects.values()  # This should fetch all relevant operator data

        for operator in all_operators:
            if punkt == operator["idPunkt"]:  # Check if the current operator matches the specified punkt
                zone = operator["Zone"]
                ToDo = operator["ToDo"]
                link = operator["link"]
                H = operator["H"]  # Overwriting H might not be necessary; depends on your logic
                
                # Assuming logs and Next functions are defined elsewhere
                logs(username=username, userid=userid, department="Оператор", message_id=call.message.id, H=H, zone=zone, punkt=punkt)
                Next(userid, H, punkt, username)
                break  # Exit the loop once the matching operator is found and processed


    elif call.data.startswith("deny"):
        parts = call.data.split(":")
        H = parts[1]
        punkt = int(parts[2])
        logs(username=username, userid=userid, department=department, message_id=call.message.id, H=H)
        Next(userid, H, punkt, username)


def Next(userid, H, punkt, username):
    all_operators = Operators.objects.values()  # Fetch all relevant operator data
    
    queryset = log.objects.filter(teleid=userid, date=datetime.datetime.today(), H=H).order_by('id')
    results = queryset.first()
    print(punkt)

    for operator in all_operators:
        if len(all_operators) < punkt:  # If last punkt and current punkt match
                if punkt == operator["idPunkt"]:
                    zone = operator["Zone"]
                    ToDo = operator["ToDo"]
                    link = operator["link"]
                    H = operator["H"]
                    
                    acc = telebot.types.InlineKeyboardButton("Готово", callback_data=f'accept:{H}:{punkt+1}')
                    deny = telebot.types.InlineKeyboardButton("Не получается", callback_data=f'deny:{H}:{punkt+1}')
                    keyboard = telebot.types.InlineKeyboardMarkup().add(acc, deny)

                    bot.send_photo(chat_id=userid, photo=link, caption=f'{punkt}. {zone}: {ToDo}', reply_markup=keyboard)
                    break
        else:
            finish(userid, username, results)
            break
def finish(userid, username, results):
    bot.send_message(chat_id=userid, text="Вы прошли обход")
    bot.edit_message_text(chat_id = chat_id, text=f"@{username} прошел обход", message_id=results.message_id)


def start_bot():
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=bot.polling, daemon=True)
    bot_thread1 = threading.Thread(target=start_time, daemon=True)
    bot_thread.start()
    bot_thread1.start()
