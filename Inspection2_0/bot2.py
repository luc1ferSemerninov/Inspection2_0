import telebot
from telebot import types
from telebot.types import Message
from colorama import Fore, Style
import requests
from .send_to_b24 import createRequest, edit_deal,delete_deal,switch
from django.core.files import File
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import base64
import os



# import os
# import django
# from django.conf import settings
# from django.db import models

# # Установка переменной окружения, указывающей на settings.py проекта Django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_other_project.settings')
# django.setup()

# # Импорт моделей, с которыми нужно взаимодействовать
# from your_other_app.models import YourModel

# # Пример работы с моделью
# def process_data():
#     # Пример получения объектов из базы данных
#     queryset = YourModel.objects.all()
#     for obj in queryset:
#         print(obj)

# if __name__ == '__main__':
#     process_data()






group_id = -1002003805171
token = "7156367176:AAHWf4T-36vtV8UjHjDDowYlRY--Myq1OFM"
bot = telebot.TeleBot(token)

def start(message):
    if message.chat.id == message.from_user.id:
        text="""
Выберите направление.
C чем связана проблема.

Хоз или тех часть?

Кнопки ниже 👇
            """
        markup = types.ReplyKeyboardMarkup()
        markup.add("IT наряд 💻", "Хоз наряд 🛠🧹")

        bot.send_message(message.chat.id, text, reply_markup=markup)

        bot.register_next_step_handler(message, get_request_type)
def get_request_type(message):
    if message.text == "IT наряд 💻":
        data = Request(type="it")
    elif message.text == "Хоз наряд 🛠🧹":
        data = Request(type="hoz")
    else:
        start(message)
        return

    if data.type == 'it':
        text = "Выберите зону. Нажмите /start чтобы начать сначала"

        markup = types.ReplyKeyboardMarkup()
        [markup.add(str(i)) for i in Place.objects.all()]


        bot.send_message(message.chat.id, text, reply_markup=markup)
        bot.register_next_step_handler(message, get_zone, data)
    else:
        text = "Прикрепите фото/видео/aудио проблемы (можно кружочек или голосовое)\n/skip чтобы пропустить"
        bot.send_message(message.chat.id, text, reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_document, data)


def get_zone(message, data):
    if data.type == "it":
        if message.text == "/start":
            start(message)
            return
        else:
            data.zone = message.text
            data.description = f'{message.text}'
    else:
        pass


    text = "Выберите тип проблемы. Нажмите /start чтобы начать сначала"

    markup = types.ReplyKeyboardMarkup()
    [markup.add(str(i)) for i in Problem.objects.all()]


    bot.send_message(message.chat.id, text, reply_markup=markup)
    bot.register_next_step_handler(message, get_problem, data)

def get_problem(message, data):
    if data.type == "it":
        if message.text == "/start":
            start(message)
            return
        else:
            problem = Problem.objects.get(name=message.text)
            data.problem = problem
            data.description += f'\n{message.text}'

    else:
        pass

    text = "Прикрепите фото/видео/aудио проблемы (можно кружочек или голосовое)\n/skip чтобы пропустить"
    bot.send_message(message.chat.id, text, reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_document, data)



def get_document(message, data):
    if message.document:
        doc = message.document
    elif message.audio:
        doc = message.audio
        data.file_type = "audio"
    elif message.voice:
        doc = message.voice
        data.file_type = "voice"
    elif message.photo:
        doc = message.photo
        data.file_type = "photo"
    elif message.video_note:
        doc = message.video_note
        data.file_type = "videonote"
    elif message.video:
        doc = message.video
        data.file_type = "video"
    elif message.text == "/start":
        start(message)
        return
    else:
        if message.text == "/skip":
            text = "Опишите проблему текстом (/start чтобы начать сначала)"
            bot.send_message(message.chat.id, text)
            bot.register_next_step_handler(message, get_desc, data)
            return

        text = "Прикрепите фото/видео/aудио проблемы (можно кружочек или голосовое)\nИспользуйте /start чтобы начать сначала\n/skip чтобы пропустить"
        bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(message, get_document, data)
        return
    
    try:
        file_id = doc[-1].file_id
    except:
        file_id = doc.file_id
    
    file_id_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_id_info.file_path)
    file_name = file_id_info.file_path.split('/')[-1]
    
    data.file = [downloaded_file, file_name]
    data.file_id = file_id
    
    text = "Опишите проблему текстом (/start чтобы начать сначала)"

    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, get_desc, data)

def get_desc(message, data):
    if message.text == "/start":
        start(message)
        return
    elif message.text == "/skip":
        if not data.file:
            text = "Опишите проблему текстом (/start чтобы начать сначала)\n *Зона*\n*Проблема*"
            bot.send_message(message.chat.id, text)
            bot.register_next_step_handler(message, get_desc, data)
            return
        data.description = ""
    else:
        data.description += f'\n{message.text}'
        text = "Это срочная задача?"
        markup = types.ReplyKeyboardMarkup()
        markup.add("Срочно", "Не срочно")
        bot.send_message(message.chat.id, text, reply_markup=markup)
        bot.register_next_step_handler(message, get_important, data)

def get_important(message, data):
    if message.text == "/start":
        start(message)
        return
    elif message.text == "Срочно":
        data.description += f'\n!!!!!СРОЧНО!!!!!'

    username = ""
    if message.from_user.username:
        username += '@' + message.from_user.username
    if message.from_user.first_name:
        username += f"\n{message.from_user.first_name}"
    if message.from_user.last_name:
        username += f" {message.from_user.last_name}"

    data.username = '@' + message.from_user.username
    
    keyboard = InlineKeyboardMarkup()
    listt = Important.objects.all()
    for list in listt:
        keyboard.add(InlineKeyboardButton(text=f"{list}", callback_data=f"{data.type}:{list}"))
    # keyboard.add(InlineKeyboardButton(text="Сменить направление", callback_data=f"{data.type}:Сменить направление"))
    keyboard.add(InlineKeyboardButton(text="Ложная заявка", callback_data=f"{data.type}:Ложная заявка"))

        
    
    deal_id = createRequest(data)
    url = f"https://next.bitrix24.kz/crm/deal/details/{deal_id}/"
    if data.type == "it":
        thread = 242
        text = f"""{username}

🔴{data.get_type_display()}
{data.description}

Заявка №{deal_id}
Сылка на сделку: {url}
"""
    else:
        thread = 244
        text = f"""{username}

🔴{data.get_type_display()}
{data.description}

Заявка №{deal_id}
Сылка на сделку: {url}
"""

        
    # Создаем инлайн-кнопки]
    if data.file_type == "video":
        mes_id = bot.send_video(group_id, message_thread_id=thread, video=data.file_id, caption=text, reply_markup=keyboard)
    elif data.file_type == "videonote":
        video_note_path = f'video_note_{deal_id}.mp4'  # Путь, по которому будет сохранен видео
        file_info = bot.get_file(data.file_id)  # Получаем информацию о файле
        file_path = file_info.file_path  # Получаем путь к файлу
        file_url = f'https://api.telegram.org/file/bot{API}/{file_path}'  # Формируем URL для скачивания
        response = requests.get(file_url)  # Отправляем запрос на скачивание
        with open(video_note_path, 'wb') as f:
            f.write(response.content)  # Записываем содержимое файла
        # Отправка видео
        mes_id = bot.send_video(group_id, caption=text,message_thread_id=thread, video=open(video_note_path, 'rb'), reply_markup=keyboard)
        # Удаление файла с диска
        os.remove(video_note_path)
    elif data.file_type == "photo":
        mes_id = bot.send_photo(group_id, photo=data.file_id,message_thread_id=thread, caption=text, reply_markup=keyboard)
    elif data.file_type == "audio":
        mes_id = bot.send_audio(group_id, audio=data.file_id, caption=text,message_thread_id=thread, reply_markup=keyboard)
    elif data.file_type == "voice":
        mes_id = bot.send_voice(group_id, voice=data.file_id, caption=text,message_thread_id=thread, reply_markup=keyboard)
    else:
        mes_id = bot.send_message(group_id, text,message_thread_id=thread, reply_markup=keyboard)

    data.message_id = mes_id.message_id
    # send(userid=message.from_user.id, username=username, deal_to=data.type, important='Новая', file_type=data.file_type, message=data.description, message_id=data.message_id, deal_id=deal_id)
    entry = Case.objects.create(userid = message.from_user.id, username = username, type = data.type, important = "Новая", message = data.description, message_id1 = data.message_id, deal_id = deal_id)
    entry.save()
    print("\n\n\n\n\n\n\n\n\n\nСделал\n\n\n\n\n\n\n\n\n\n")
    
    #Send a mes into the group
    bot.send_message(message.chat.id, f"Ваша заявка №{deal_id} отправленна! Используйте /start чтобы создать ещё одну заявку", reply_markup=types.ReplyKeyboardRemove())