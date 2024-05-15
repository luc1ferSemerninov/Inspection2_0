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


def start_time():
    all_objects = Start.objects.values()
    # Цикл, который проходится по созданным переменным и отправляет кнопку "Принять"
    for i in all_objects:
        time_start = i["time_start"]
        group = i["group_id"]
        zone = i["zone"]  # название обхода
        department = i["department"]
        H = i["H"]
        time_now = datetime.datetime.now().time().strftime("%H:%M:%S")
        if time_now == time_start:  # Сравниваем текущее время с временем начала
            send_inspection(group, department, zone, H)
            time.sleep(60)  # Подождать 60 секунд перед следующим запуском


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
        department = parts[0]
        H = parts[1]
        bot.edit_message_text(f"@{call.from_user.username} Принял обход", chat_id=chat_id, message_id=call.message.id)

        # Отправляем личное сообщение пользователю
        bot.send_message(call.from_user.id, "Вы приняли обход")

        current_datetime = datetime.datetime.now()
        current_date_iso = current_datetime.date().isoformat()
        time_now = current_datetime.time().strftime("%H:%M:%S")
        # Создаем объект модели log
        log_entry = log.objects.create(
            date=current_date_iso,
            time=time_now,
            who=username,
            teleid=userid,
            zone="Принял обход",
            result=1,
            comment="+",
            department=department,
            H=H,
            punkt=1,
            message_id=call.message.id
        )
        log_entry.save()
        # Человек принял обход и дальше мы запускаем функцию, которая будет проверять на каком пункте человек, и отправлять следующий пункт
        Next(userid, H)

    if call.data.startswith("accept"):
        parts = call.data.split(":")
        userid = parts[0]
        H = parts[1]
        bot.edit_message_text(f"@{call.from_user.username} Принял обход", chat_id=chat_id, message_id=call.message.id)
        Next(userid, H)

    if call.data.startswith("deny"):
        parts = call.data.split(":")
        userid = parts[0]
        H = parts[1]
        bot.edit_message_text(f"@{call.from_user.username} Отклонил обход", chat_id=chat_id, message_id=call.message.id)

        bot.send_message(call.from_user.id, "Вы отклонили обход")
        Next(userid, H)


async def Next(userid, H):
    all = Operators.objects.values()  # это таблица с обходом, откуда мы берем все значения
    last_punkt = len(all)
    queryset = log.objects.filter(teleid=userid, date=datetime.date.today(), H=H).order_by('id')
    results = list(queryset)[0]
    if last_punkt == results.punkt - 1:  # если последний пункт и тот пункт на котором пользователь равны
        pass
    for i in all:
        punkt = i["idPunkt"]  # так же как в прошлый раз закидываем эти значения в переменные
        zone = i["Zone"]
        ToDo = i["ToDo"]
        link = i["link"]
        H = i["H"]
        acc = telebot.types.InlineKeyboardButton("Готово", callback_data=f'accept:{H}')  # это будет кнопка Готово, которая в себе будет содержать userid и H
        deny = telebot.types.InlineKeyboardButton("Не получается", callback_data=f'deny:{H}')  # а это кнопка Не получается
        keyboard = telebot.types.InlineKeyboardMarkup().add(acc, deny)  # таким образом мы закидываем кнопки в клавиатуру

        bot.send_photo(chat_id=chat_id, photo=link, caption=f'{punkt}. {zone}: {ToDo}', reply_markup=keyboard)  # отправляем в чат


def start_bot():
    t = threading.Thread(target=bot.polling, daemon=True)
    t.start()


start_bot()  # Запуск бота в отдельном потоке
start_time()  # Запуск функции проверки времени каждую минуту
