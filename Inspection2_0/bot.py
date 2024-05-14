
import telebot
from django.http.response import HttpResponse
import json
import threading

from datetime import datetime
from django.utils import timezone
import pytz
import datetime
from .models import Start
from .models import log
from .models import Operators #добавил еще таблицу операторов

all_objects = Start.objects.values()

chat_id = -1002003805171

token = "7156367176:AAHWf4T-36vtV8UjHjDDowYlRY--Myq1OFM"
webhook_url = "ТВОЙ IP"
bot = telebot.TeleBot(token)

print(bot.get_me().username)

print(all_objects)

for i in all_objects:
    time = i["time_start"]
    group = i["group_id"]
    zone = i["zone"]
    department = i["department"]
    H = i["H"]
    send_photo_button = telebot.types.InlineKeyboardButton("Принять", callback_data=f'claim{H}')
    keyboard = telebot.types.InlineKeyboardMarkup().add(send_photo_button)

    bot.send_message(chat_id = chat_id, message_thread_id= group, text = f'{department} Вам пришел: {zone}', reply_markup=keyboard)

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
    bot.reply_to(message, "Привет")
    return 200


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    userid = call.from_user.id
    username = call.from_user.username



    if call.data.startswith('claim'):
        H = call.data.replace('claim', '')  # Получаем значение H из callback_data
        # Отправляем личное сообщение пользователю
        bot.send_message(call.from_user.id, "Вы приняли обход")
        bot.edit_message_text(f"@{call.from_user.username} Принял обход", chat_id=chat_id, message_id=call.message.id)

        current_datetime = datetime.datetime.now()#тут было datetime.now(), вот он ругался
        current_date_iso = current_datetime.date().isoformat()
        time_now = current_datetime.time().strftime("%H:%M:%S")#вот так правильнее будет записывать время
        # Создаем объект модели log
        log_entry = log.objects.create(
            date = current_date_iso,
            time = time_now,
            who = username,
            teleid = userid,
            zone = zone,
            result = 1,
            comment = "Принял обход",#тут было Test, но правильнее будет записывать что человек принял обход
            department = department,
            H = H,
            punkt = 1,
            message_id = (call.message.id)
        )
        log_entry.save()
        #человек принял обход и дальше мы запускаем функцию, которая будет проверять на каком пункте человек, и отправлять следующий пункт
        Next(userid, H)


    if call.data.startswith("accept"):
        #тут у тебя будет обработка нажатия accept
        pass
    if call.data.startswith("deny"):
        #тут у тебя будет обработка нажатия deny
        pass
        


#вот эта функция
def Next(userid, H):
    all = Operators.objects.values()#это таблица с обходом, откуда мы берем все значения
    last_punkt = len(all)
    queryset = log.objects.filter(teleid=userid, date=datetime.date.today(), H=H).order_by('id')
    results = list(queryset)[0]
    if last_punkt == results.punkt-1:#если последний пункт и тот пункт на котором пользователь равны
        pass
    # for i in s:
    #     punkt = i["idPunkt"]#так же как в прошлый раз закидываем эти значения в переменные
    #     zone = i["Zone"]
    #     ToDo = i["ToDo"]
    #     link = i["link"]
    #     H = i["H"]
    #     acc = telebot.types.InlineKeyboardButton("Готово", callback_data=f'accept:{userid}:{H}')#это будет кнопка Готово, которая в себе будет содержать userid и H
    #     deny = telebot.types.InlineKeyboardButton("Не получается", callback_data=f'deny:{userid}:{H}')#а это кнока Не получается
    #     keyboard = telebot.types.InlineKeyboardMarkup().add(acc, deny)#таким образом мы закидываем кнопки в клавиатуру


    #     bot.send_photo(chat_id=chat_id, photo=link, caption=f'{punkt}. {zone}: {ToDo}', reply_markup=keyboard)#отправляем в чат
    #     pass



def start_bot():
    t = threading.Thread(target=bot.polling, daemon=True)
    t.start()

