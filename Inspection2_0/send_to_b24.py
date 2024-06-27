import base64  # Импортируем модуль base64
from fast_bitrix24 import Bitrix
import json
import requests

# def read_file_as_base64(file_path):
#     with open(file_path, 'rb') as file:  # Открываем файл в режиме чтения бинарных данных ('rb')
#         file_data = file.read()  # Считываем содержимое файла
#         if file_data:  # Проверяем, что файл не пустой
#             # Кодируем содержимое файла в формате base64 и декодируем в строку
#             file_base64 = base64.b64encode(file_data).decode('utf-8')
#             return file_base64  # Возвращаем содержимое файла в формате base64
#         else:
#             print("Файл пуст.")
#             return None  # Возвращаем None, если файл пустой

def createRequest(data):
    if data.type == "hoz":
        type_id = 12
    elif data.type == 'it':
        type_id = 4

    if not data.file:
        file_data = {}
    else:
        file_data = {"fileData":[data.file[1], base64.b64encode(data.file[0]).decode('utf-8')] }

    if data.description:
        title = f"{data.get_type_display()}"
        print(title)
    else:
        title = data.get_type_display()

    webhook = "https://next.bitrix24.kz/rest/6/zrpvyiesoh43mn1n"
    
    b = Bitrix(webhook)
    f = b.call('crm.deal.add', 
        {
        'fields': 
            {
            "TITLE": title,
            "UF_CRM_1644911873": data.username,
            "CATEGORY_ID" : type_id,
            "STAGE_ID": f"C{type_id}:NEW",
            "COMMENTS":data.description,
            "UF_CRM_1644905384": file_data
            }
        }
    )

    print(f)  # Выводим результат выполнения запроса
    return f





def edit_deal(id, type, important):
    if type == "hoz":
        type_id = 12
    else:
        type_id = 4
    webhook = "https://next.bitrix24.kz/rest/6/zrpvyiesoh43mn1n"
    b = Bitrix(webhook)
    print(id)
    f = b.call('crm.deal.update', 
        {
        'id': id,
        'fields': 
            {
            "CATEGORY_ID" : type_id,
            "STAGE_ID": f"C{type_id}:{important}",
            }
        }
    )

def delete_deal(id):
    webhook = "https://next.bitrix24.kz/rest/6/zrpvyiesoh43mn1n"
    b = Bitrix(webhook)
    print(id)
    f = b.call('crm.deal.delete', 
        {
        'id': id
        }
    )

def switch(type, id):
    if type == "it":
        type_id = 12
    else:
        type_id = 4
    
    webhook = "https://next.bitrix24.kz/rest/6/zrpvyiesoh43mn1n"
    b = Bitrix(webhook)
    print(id)
    
    # Получение данных с сервера Bitrix24
    resp = requests.get(f"https://next.bitrix24.kz/rest/6/zrpvyiesoh43mn1n/crm.deal.get?id={id}")
    
    # Проверка успешности запроса
    if resp.status_code == 200:
        # Преобразование JSON-данных в словарь Python
        data = resp.json()
        
        # Получение значения поля "TITLE"
        title = data["result"]["TITLE"]
        
        # Замена "IT Наряд" на "Хоз наряд" в заголовке
        if title == "IT наряд":
            new_title = title.replace("IT Наряд", "Заявка хоз.наряд")
        else:
            new_title = title.replace("Заявка хоз.наряд", "IT Наряд")
        
        # Обновление данных на сервере Bitrix24
        response = b.call('crm.deal.update', 
            {
                'id': id,
                'fields': 
                {
                    "CATEGORY_ID": type_id,
                    "STAGE_ID": f"C{type_id}:NEW",
                    "TITLE": new_title
                }
            }
        )
        
        print(response)  # Вывод результата обновления
        
    else:
        print("Ошибка при выполнении запроса:", resp.json())