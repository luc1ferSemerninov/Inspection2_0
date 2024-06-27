from django.http.response import HttpResponse
from datetime import datetime, time
import telebot
import json
import threading
import pytz
import time
import os
import datetime
from telebot import types
from .models import Start, log, Operator, User, Admin, Cashier
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, Message, InlineKeyboardMarkup, InlineKeyboardButton
import re
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont, TTFError

chat_id = -1002003805171
token = "7156367176:AAHWf4T-36vtV8UjHjDDowYlRY--Myq1OFM"
webhook_url = "ТВОЙ IP"

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    a = User.objects.values()
    for i in a:
        if message.from_user.id == i["userid"]:
            bot.send_message(message.from_user.id, "Вы уже зарегестрированы")
            return
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    start_button = types.KeyboardButton('Регистрация')
    keyboard.add(start_button)
    bot.send_message(message.chat.id, 'Пройдите регистрацию', reply_markup=keyboard)
    bot.register_next_step_handler(message, handle_reg)


@bot.message_handler(commands=['admin'])
def adminpanel(message):
    a = User.objects.filter(userid = message.from_user.id).first()
    print(a)
    if a.admin:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Отправить обход", callback_data=f"send"))
        markup.add(types.InlineKeyboardButton("Изменить время начала обхода", callback_data=f"time"))
        markup.add(types.InlineKeyboardButton("Поменять человеку отдел", callback_data=f"switch"))
        bot.send_message(message.from_user.id, "Првиет админ, выбери действие", reply_markup=markup)
    

def handle_reg(message: Message):
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if message.from_user.username:
        username = message.from_user.username
    else:
        username = "-"
    entry = User.objects.create(datetime=current_datetime,
                                 userid=message.from_user.id,
                                 username=username,
                                 name = message.from_user.full_name,
                                 number="123",
                                 department="o")

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
            
        User.objects.filter(userid=message.from_user.id).update(number = cleaned_phone_number)
        handle_registration(message)
        # print(f"Занёс в БД {phone_number}")


# Выбор должности
def handle_registration(message):
    markup = types.InlineKeyboardMarkup()
    start_objects = Start.objects.all()
    unique_names = set()
    for start in start_objects:
        unique_names.add(start.department)
    for name in unique_names:
        markup.add(types.InlineKeyboardButton(name, callback_data=f"dep:{name}"))
    
    
    # Send the message with the inline keyboard
    bot.send_message(message.chat.id, 'Выберите должность', reply_markup=markup)





def create_and_send_pdf(user, H):
    date = datetime.datetime.now().date().isoformat()
    user_logs = log.objects.filter(teleid=user.userid, H=H, date=date, department=user.department)

    styles = getSampleStyleSheet()
    styles['Title'].fontName = 'FreeSans'
    styles['Title'].fontSize = 16
    styles['Title'].alignment = 'CENTER'
    # Получение пути к текущему скрипту
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Построение пути к файлу шрифта относительно пути к текущему скрипту
    font_path = os.path.join(script_dir, 'font', 'FreeSans.ttf')

    try:
        # Подключение шрифта для поддержки русских символов
        pdfmetrics.registerFont(TTFont('FreeSans', font_path))
    except TTFError as e:
        print(f"Error loading font: {e}")
        return


    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title = Paragraph(f"Отчет по обходу для пользователя: {user.username}", styles['Title'],encoding='utf-8')
    department = Paragraph(f"Отдел: {user.department}", styles['Title'])
    elements.append(title)
    elements.append(department)

    # Создание данных для таблицы
    data = [['Время', 'Зона', 'Результат']]
    for entry in user_logs:
        data.append([str(entry.time), entry.zone, str(entry.result)])

    # Создание таблицы
    table = Table(data, colWidths=[2*inch, 2.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'FreeSans'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'FreeSans'),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    # Отправка документа с расширением .pdf в имени файла
    try:
        bot.send_document(chat_id, (f'{user.department}-{date}.pdf', buffer), caption=f"{user.department} - отчет по обходу")
    except telebot.apihelper.ApiTelegramException as e:
        if e.result_json['description'] == "Bad Request: message is not modified":
            print("Message is not modified: the same content is being sent.")
        else:
            raise e

# Пример использования функций
@bot.message_handler(commands=['generate_report'])
def generate_report(userid, H):
    user = User.objects.get(userid=userid)
    create_and_send_pdf(user, H)





def logs(username, userid, department, message_id, H, zone, punkt, result):
    current_datetime = datetime.datetime.now()
    current_date_iso = current_datetime.date().isoformat()
    time_now = current_datetime.time().strftime("%H:%M:%S")
    log_entry = log.objects.create(
                date=current_date_iso,
                time=time_now,
                who=username,
                teleid=userid,
                zone=zone,
                result=result,
                comment="+",
                department=department,
                H=H,
                punkt=punkt,
                message_id=message_id
            )

    log_entry.save()

def start_time():
    all_objects = Start.objects.values()

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
    send_photo_button = telebot.types.InlineKeyboardButton("Принять", callback_data=f'claim:{department}:{H}')
    keyboard = telebot.types.InlineKeyboardMarkup().add(send_photo_button)

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



@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    userid = call.from_user.id
    username = call.from_user.username
    department1 = User.objects.filter(userid=userid).first()
    if department1.department.lower() == "оператор":
        dep = Operator
    elif department1.department.lower() == "администратор":
        dep = Admin
    elif department1.department.lower() == "кассир":
        dep = Cashier
    else:
        dep = Operator

    if call.data.startswith('claim'):
        parts = call.data.split(":")
        department = parts[1]  # [0] это слово "claim"
        print(department1.department, department)
        if department1.department == department:
            H = parts[2]
            bot.edit_message_text(f"@{call.from_user.username} Принял обход", chat_id=call.message.chat.id, message_id=call.message.id)

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

            Next(userid, H, 1, username, department)
        else:
            bot.answer_callback_query(call.id, "Ты сюда не подходишь")

    elif call.data.startswith("accept"):
        bot.delete_message(userid, call.message.id)
        parts = call.data.split(":")
        H = parts[1]
        punkt = int(parts[2])
        department = parts[3]
        zone = dep.objects.filter(idPunkt=punkt-1, H = H).first()
        logs(username=username, userid=userid, department=department, message_id=call.message.id, H=H, zone=zone.Zone, punkt=punkt, result = True)
        # bot.send_message(userid, "Отправь видео-отчет кружочком")
        # bot.register_next_step_handler(call.message, videonote_check, userid, H, punkt, username, department)
        Next(userid, H, punkt, username, department)

    elif call.data.startswith("deny"):
        bot.delete_message(userid, call.message.id)
        parts = call.data.split(":")
        H = parts[1]
        punkt = int(parts[2])
        department = parts[3]
        zone = dep.objects.filter(idPunkt=punkt-1, H=H).first()
        logs(username=username, userid=userid, department=department, message_id=call.message.id, H=H, zone=zone.Zone, punkt=punkt, result = False)
        Next(userid, H, punkt, username, department)

    elif call.data.startswith("dep"):
        parts = call.data.split(":")
        department = parts[1]

        user_id = call.from_user.id
        
        user, created = User.objects.get_or_create(userid=user_id)
        user.department = department
        user.save()
        
        bot.send_message(call.message.chat.id, f'Вы выбрали должность: {department}')
        
        hide_keyboard = types.ReplyKeyboardRemove()
        bot.send_message(call.from_user.id, "https://t.me/+Lofj5NaqOcdjOTgy", reply_markup=hide_keyboard)

        if call.message:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

            
    elif call.data.startswith("send"):
        a = User.objects.filter(userid = call.from_user.id).first()
        if a.admin:
            starts = Start.objects.values()
            st = 'Введите номер обхода, который Вы хотите повторно отправить:\n'
            l = 0
            for i in starts:
                l=l+1
                st += f'{l}. {i["department"]} - {i["zone"]} - {i["time_start"]}\n'
            bot.edit_message_text(st, call.from_user.id, message_id=call.message.id)
            bot.register_next_step_handler(message=call.message, callback=resend)

    elif call.data.startswith("time"):
        a = User.objects.filter(userid = call.from_user.id).first()
        if a.admin:
            starts = Start.objects.values()
            st = 'Введите номер обхода, который Вы изменить:\n'
            l = 0
            for i in starts:
                l=l+1
                st += f'{l}. {i["department"]} - {i["zone"]} - {i["time_start"]}\n'
            bot.edit_message_text(st, call.from_user.id, message_id=call.message.id)
            bot.register_next_step_handler(message=call.message, callback=change_time)

    elif call.data.startswith("switch"):
        a = User.objects.filter(userid = call.from_user.id).first()
        if a.admin:
            users = User.objects.values()
            st = 'Введите номер человека, которому хотите поменять отдел:\n'
            print(users)
            l = 0
            for i in users:
                l=l+1
                st += f'{l}. {i["username"]} - {i["name"]} - {i["department"]}\n'
            bot.edit_message_text(st, call.from_user.id, message_id=call.message.id)
            bot.register_next_step_handler(message=call.message, callback=change_dep)

def change_dep(message: Message):
    try:
        users = User.objects.values()
        nomber = int(message.text)
        if nomber > len(users):
            bot.send_message(message.from_user.id, "Введите корректное число")
            bot.register_next_step_handler(message, change_dep)
        else:
            ins = users[nomber-1]
            markup = types.ReplyKeyboardMarkup()
            start_objects = Start.objects.all()
            unique_names = set()
            for start in start_objects:
                unique_names.add(start.department)
            for name in unique_names:
                markup.add(types.KeyboardButton(f'd:{name}'))
            bot.send_message(message.from_user.id, "Выберите отдел для этого человека", reply_markup=markup)
            bot.register_next_step_handler(message, change_dep2, ins)
    except:
        bot.send_message(message.from_user.id, "Введите корректное число")
        bot.register_next_step_handler(message, change_dep)

def change_dep2(message: Message, ins):
    try:
        i, name = message.text.split(':')
        User.objects.filter(id=ins['id']).update(department = name)
        s = bot.send_message(message.from_user.id, "Готово", reply_markup=types.ReplyKeyboardRemove()).message_id
        bot.delete_message(message.from_user.id, s)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Отправить обход", callback_data=f"send"))
        markup.add(types.InlineKeyboardButton("Изменить время начала обхода", callback_data=f"time"))
        markup.add(types.InlineKeyboardButton("Поменять человеку отдел", callback_data=f"switch"))
        bot.send_message(message.from_user.id, "Готово, вот снова админская панель", reply_markup=markup)
    except:
        bot.send_message(message.from_user.id, "Выберите отдел из меню ниже")
        bot.register_next_step_handler(message, change_dep2)



@bot.message_handler(content_types=['video_note'])
def videonote_check(message: Message, userid, H, punkt, username, department):
    video_note = message.video_note
    file_id = video_note.file_id
     # Получение информации о файле
    file_info = bot.get_file(file_id)
    
    # Ссылка для скачивания файла
    file_path = file_info.file_path
    download_link = f"https://api.telegram.org/file/bot{token}/{file_path}"

    bot.send_message(7319662643, f"Ссылка на видеокружок: \n {download_link}")

    Next(userid, H, punkt, username, department)

@bot.message_handler(content_types=['photo', 'audio', 'video', 'document', 'voice'])
def videonote_check(message: Message, userid, H, punkt, username, department):
    bot.send_message(message.from_user.id, "Пожалуйста, отправьте видеокружок.")
    bot.register_next_step_handler(message, videonote_check, userid, H, punkt, username, department)




def change_time(message: Message):
    try:
        starts = Start.objects.values()
        nomber = int(message.text)
        if nomber > len(starts):
            bot.send_message(message.from_user.id, "Введите корректное число")
            bot.register_next_step_handler(message, resend)
        else:
            ins = starts[nomber-1]
            bot.send_message(message.from_user.id, "Введите время в формате 'чч:мм'")
            bot.register_next_step_handler(message, change_time2, ins)
    except:
        bot.send_message(message.from_user.id, "Введите корректное число")
        bot.register_next_step_handler(message, resend)

def change_time2(message: Message, ins):
    try:
        hours, minutes = message.text.split(':')
        print(hours, minutes)
        ti = datetime.time(int(hours), int(minutes))
        Start.objects.filter(id = ins['id']).update(time_start = ti)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Отправить обход", callback_data=f"send"))
        markup.add(types.InlineKeyboardButton("Изменить время начала обхода", callback_data=f"time"))
        markup.add(types.InlineKeyboardButton("Поменять человеку отдел", callback_data=f"switch"))
        bot.send_message(message.from_user.id, "Готово, вот снова админская панель", reply_markup=markup)
    except:
        bot.send_message(message.from_user.id, "Введите корректное число")
        bot.register_next_step_handler(message, change_time2, ins)


def resend(message: Message):
    try:
        starts = Start.objects.values()
        nomber = int(message.text)
        if nomber > len(starts):
            bot.send_message(message.from_user.id, "Введите корректное число")
            bot.register_next_step_handler(message, resend)
        else:
            ins = starts[nomber-1]
            send_inspection(ins['group_id'], ins["department"], ins['zone'], ins['H'])
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Отправить обход", callback_data=f"send"))
            markup.add(types.InlineKeyboardButton("Изменить время начала обхода", callback_data=f"time"))
            markup.add(types.InlineKeyboardButton("Поменять человеку отдел", callback_data=f"switch"))
            bot.send_message(message.from_user.id, "Готово, вот снова админская панель", reply_markup=markup)
    except:
        bot.send_message(message.from_user.id, "Введите корректное число")
        bot.register_next_step_handler(message, resend)




def Next(userid, H, punkt, username, department):
    print(f"Next function called with: userid={userid}, H={H}, punkt={punkt}, username={username}, department={department}")
    
    if department.lower() == "оператор":
        all_tasks = Operator.objects.filter(H=H).values()
    elif department.lower() == "администратор":
        all_tasks = Admin.objects.filter(H=H).values()
    elif department.lower() == "кассир":
        all_tasks = Cashier.objects.filter(H=H).values()
    else:
        all_tasks = []
    
    


    print(f"Filtered all_tasks length: {len(all_tasks)}")

    queryset = log.objects.filter(teleid=userid, date=datetime.datetime.today(), H=H).order_by('id')
    results = queryset.first()
    print(f"Punkt: {punkt}, all_tasks length: {len(all_tasks)}")

    task_found = False
    if punkt < len(all_tasks)+1:
        for task in all_tasks:
            print(f"Checking task: {task['idPunkt']} against punkt: {punkt}")
            if punkt == task["idPunkt"]:
                zone = task["Zone"]
                ToDo = task["ToDo"]
                link = task["link"]
                H = task["H"]
                
                acc = telebot.types.InlineKeyboardButton("Готово", callback_data=f'accept:{H}:{punkt+1}:{department}')
                deny = telebot.types.InlineKeyboardButton("Не получается", callback_data=f'deny:{H}:{punkt+1}:{department}')
                keyboard = telebot.types.InlineKeyboardMarkup().add(acc, deny)

                bot.send_photo(chat_id=userid, photo=link, caption=f'{punkt}. {zone}: {ToDo}', reply_markup=keyboard)
               
                task_found = True
                break
        
        if not task_found:
            finish(userid, username,H, results)
    else:
        finish(userid, username,H, results)


def finish(userid, username, H, results):
    bot.send_message(chat_id=userid, text="Вы прошли обход")

    generate_report(userid, H)
    
    user = User.objects.get(userid=userid)
    department = user.department.lower()
    
    
    print(f"Department: {department}")

    if department == "оператор":
        bot.send_message(chat_id=chat_id, message_thread_id=67, text=f"@{username} Прошел обход")
        # print(thread_id)
    elif department == "администратор":
        bot.send_message(chat_id=chat_id, message_thread_id=70, text=f"@{username} Прошел обход")
        # print(thread_id)
    elif department == "кассир":
        bot.send_message(chat_id=chat_id, message_thread_id=1622, text=f"@{username} Прошел обход")
        # print(thread_id)
    else:
        bot.send_message(chat_id=userid, text="Не удалось отправить сообщение в тему.")


def start_bot():
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=bot.polling, daemon=True)
    bot_thread1 = threading.Thread(target=start_time, daemon=True)
    bot_thread.start()
    bot_thread1.start()