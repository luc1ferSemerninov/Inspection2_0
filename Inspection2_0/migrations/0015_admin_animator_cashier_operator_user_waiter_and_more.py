# Generated by Django 5.0.6 on 2024-06-07 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Inspection2_0', '0014_adminhbd'),
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idPunkt', models.IntegerField(verbose_name='Чек номер')),
                ('Zone', models.TextField(max_length=100, verbose_name='Зона')),
                ('ToDo', models.TextField(max_length=200, verbose_name='Название задачи')),
                ('link', models.TextField(max_length=200, verbose_name='Ссылка на изображение')),
                ('department', models.IntegerField(default=0, verbose_name='Номер отдела')),
                ('H', models.IntegerField(verbose_name='Номер обхода')),
            ],
        ),
        migrations.CreateModel(
            name='Animator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idPunkt', models.IntegerField(verbose_name='Чек номер')),
                ('Zone', models.TextField(max_length=100, verbose_name='Зона')),
                ('ToDo', models.TextField(max_length=200, verbose_name='Название задачи')),
                ('link', models.TextField(max_length=200, verbose_name='Ссылка на изображение')),
                ('department', models.IntegerField(default=0, verbose_name='Номер отдела')),
                ('H', models.IntegerField(verbose_name='Номер обхода')),
            ],
        ),
        migrations.CreateModel(
            name='Cashier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idPunkt', models.IntegerField(verbose_name='Чек номер')),
                ('Zone', models.TextField(max_length=100, verbose_name='Зона')),
                ('ToDo', models.TextField(max_length=200, verbose_name='Название задачи')),
                ('link', models.TextField(max_length=200, verbose_name='Ссылка на изображение')),
                ('department', models.IntegerField(default=0, verbose_name='Номер отдела')),
                ('H', models.IntegerField(verbose_name='Номер обхода')),
            ],
        ),
        migrations.CreateModel(
            name='Operator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idPunkt', models.IntegerField(verbose_name='Пункт')),
                ('Zone', models.TextField(max_length=100, verbose_name='Зона')),
                ('ToDo', models.TextField(max_length=200, verbose_name='Задача')),
                ('link', models.TextField(max_length=200, verbose_name='Картинка')),
                ('H', models.IntegerField(verbose_name='Номер обхода')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.TextField(verbose_name='Дата')),
                ('userid', models.IntegerField(verbose_name='Айди')),
                ('username', models.TextField(verbose_name='Имя')),
                ('number', models.TextField(verbose_name='Номер телефона')),
                ('department', models.TextField(verbose_name='Отдел')),
            ],
        ),
        migrations.CreateModel(
            name='Waiter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idPunkt', models.IntegerField(verbose_name='Чек номер')),
                ('Zone', models.TextField(max_length=100, verbose_name='Зона')),
                ('ToDo', models.TextField(max_length=200, verbose_name='Название задачи')),
                ('link', models.TextField(max_length=200, verbose_name='Ссылка на изображение')),
                ('department', models.IntegerField(default=0, verbose_name='Номер отдела')),
                ('H', models.IntegerField(verbose_name='Номер обхода')),
            ],
        ),
        migrations.DeleteModel(
            name='Admins',
        ),
        migrations.DeleteModel(
            name='Animators',
        ),
        migrations.DeleteModel(
            name='Cashiers',
        ),
        migrations.DeleteModel(
            name='Operators',
        ),
        migrations.DeleteModel(
            name='Users',
        ),
    ]
