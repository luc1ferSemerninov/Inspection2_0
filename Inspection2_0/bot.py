
import telebot
from django.http.response import HttpResponse
import json
import threading

from .models import Start

all_objects = Start.objects.values()

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

def start_bot():
    t = threading.Thread(target=bot.polling, daemon=True)
    t.start()

