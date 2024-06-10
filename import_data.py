import os
import django
import pandas as pd

# Установка переменной окружения для Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Inspection2_0.settings')
django.setup()

# Импорт модели
from Inspection2_0.models import Admin

# Путь к вашему Excel файлу
excel_file_path = r'C:\Users\Maksim\Desktop\Обходы.xlsx'

# Загрузка данных из Excel
df = pd.read_excel(excel_file_path, sheet_name='Админ центра')

# Преобразование данных и сохранение их в базу данных
for index, row in df.iterrows():
    Admin.objects.create(
        idPunkt=row['Чек номер'],
        Zone=row['Зона'],
        ToDo=row['Название задачи'],
        link=row['Ссылка на изображения'],
        department=row['Номер отдела'],
        H=row['Номер обхода']
    )

print("Данные успешно импортированы!")
