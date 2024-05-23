from django.http.response import HttpResponse
from datetime import datetime
import telebot
import json
import threading
import pytz
import time
import datetime
from telebot import types
from .models import Start, log, Operators, Users
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, Message, InlineKeyboardMarkup, InlineKeyboardButton
import re

chat_id = -1002003805171
token = "7156367176:AAHWf4T-36vtV8UjHjDDowYlRY--Myq1OFM"
webhook_url = "ТВОЙ IP"

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    a = Users.objects.values()
    for i in a:
        if message.from_user.id == i["userid"]:
            bot.send_message(message.from_user.id, "Вы уже зарегестрированы")
            return
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    start_button = types.KeyboardButton('Регистрация')
    keyboard.add(start_button)
    bot.send_message(message.chat.id, 'Пройдите регистрацию', reply_markup=keyboard)
    bot.register_next_step_handler(message, handle_reg)


def handle_reg(message):
    entry = Users.objects.create(datetime = str(datetime.datetime.now(pytz.utc)),
                                 userid = message.from_user.id,
                                 username = message.from_user.username,
                                 number = "123",
                                 department = "o")

    entry.save()

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button_phone = KeyboardButton(text="Отправить мой номер телефона", request_contact=True)
    markup.add(button_phone)
    bot.send_message(message.chat.id, "Пожалуйста, отправьте свой номер телефона или введите его с клавиатуры.", reply_markup=markup)
    bot.register_next_step_handler(message, handle_phone_number)



def handle_phone_number(message: Message):
    try:
        bot.delete_message(message.from_user.id, message.message_id-1)
        bot.delete_message(message.from_user.id, message.message_id)
    except:
        pass
    if message.contact:
        phone_number = message.contact.phone_number
    else:
        phone_number = message.text

    if phone_number:
        standardized_phone_number = phone_number
        if phone_number.startswith("+7"):
            standardized_phone_number = re.sub(r'^\+7', '7', phone_number)  # Заменяем "+7" на "8"
        elif phone_number.startswith("8"):
            standardized_phone_number = re.sub(r'^8', '7', phone_number)  # Заменяем "8" на "7"
        
        cleaned_phone_number = re.sub(r'[()\s-]', '', standardized_phone_number)
        Operators.objects.filter(userid=message.from_user.id).update(number = cleaned_phone_number)


# Выбор должности
def handle_registration(message):
    markup = types.InlineKeyboardMarkup()
    admin_button = types.InlineKeyboardButton("Админ", callback_data="admin")
    operator_button = types.InlineKeyboardButton("Опер", callback_data="operator")
    markup.add(admin_button, operator_button)
    
    bot.send_message(message.chat.id, 'Выберите должность', reply_markup=markup)
    
    # Удаление сообщения с кнопкой "Регистрация"
    # bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


# Отправка ссылки на группу в зависимости от должности, пока что без сохранения в БД
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    hide_keyboard = types.ReplyKeyboardRemove()
    bot.send_message(call.from_user.id, "Ссылка на инвайт для админов: https://t.me/+Lofj5NaqOcdjOTgy", reply_markup=hide_keyboard)
    
    # Удаление сообщения с инлайн-кнопками
    # bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)




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


# @bot.message_handler()
# def test_message(message):
#     if message.from_user.id == message.chat.id:
#         bot.reply_to(message, "Привет")
#     return 200


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    userid = call.from_user.id
    username = call.from_user.username

    if call.data.startswith('claim'):
        parts = call.data.split(":")
        department = parts[1]  # [0] это слово "claim"
        H = parts[2]
        bot.edit_message_text(f"@{call.from_user.username} Принял обход", chat_id=chat_id, message_id=call.message.id)

        # Отправляем личное сообщение пользователю
        bot.send_message(call.from_user.id, "Вы приняли обход")

        current_datetime = datetime.datetime.now()
        current_date_iso = current_datetime.date().isoformat()
        time_now = current_datetime.time().strftime("%H:%M:%S")

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

        Next(userid, H, 1, username)

    elif call.data.startswith("accept"):
        bot.delete_message(userid, call.message.id)
        parts = call.data.split(":")
        H = parts[1]
        punkt = int(parts[2])
        all_operators = Operators.objects.values()

        for operator in all_operators:
            if punkt == operator["idPunkt"]:
                zone = operator["Zone"]
                ToDo = operator["ToDo"]
                link = operator["link"]
                H = operator["H"]

                logs(username=username, userid=userid, department="Оператор", message_id=call.message.id, H=H, zone=zone, punkt=punkt)
                Next(userid, H, punkt, username)
                break

    elif call.data.startswith("deny"):
        parts = call.data.split(":")
        H = parts[1]
        punkt = int(parts[2])
        logs(username=username, userid=userid, department=department, message_id=call.message.id, H=H)
        Next(userid, H, punkt, username)

def Next(userid, H, punkt, username):
    all_operators = Operators.objects.values()
    
    queryset = log.objects.filter(teleid=userid, date=datetime.datetime.today(), H=H).order_by('id')
    results = queryset.first()
    print(punkt)

    if punkt < len(all_operators):
        for operator in all_operators:
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

def finish(userid, username, results):
    bot.send_message(chat_id=userid, text="Вы прошли обход")
    # bot.delete_message(chat_id=chat_id, message_id=results.message_id)
    # bot.send_message(chat_id=userid, text=f"@{username} прошел обход")

    # bot.edit_message_text(chat_id = chat_id, text=f"@{username} прошел обход", message_id=results.message_id)

    






def start_bot():
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=bot.polling, daemon=True)
    bot_thread1 = threading.Thread(target=start_time, daemon=True)
    bot_thread.start()
    bot_thread1.start()
