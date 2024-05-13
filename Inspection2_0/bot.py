
import telebot
from django.http.response import HttpResponse
import json
import threading

from .models import Start

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
    if call.data.startswith('claim'):
        H = call.data.replace('claim', '')  # Получаем значение H из callback_data
        # Отправляем личное сообщение пользователю
        bot.send_message(call.from_user.id, "Вы приняли обход")
        bot.edit_message_text(f"@{call.from_user.username} Принял обход", chat_id=chat_id, message_id=call.message.id)

def start_bot():
    t = threading.Thread(target=bot.polling, daemon=True)
    t.start()
