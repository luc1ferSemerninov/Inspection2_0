# Generated by Django 5.0.6 on 2024-06-07 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Inspection2_0', '0009_alter_users_datetime'),
    ]

    operations = [
        migrations.CreateModel(
            name='Admins',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idPunkt', models.IntegerField(verbose_name='Чек номер')),
                ('Zone', models.TextField(max_length=100, verbose_name='Зона')),
                ('ToDo', models.TextField(max_length=200, verbose_name='Название задачи')),
                ('link', models.TextField(max_length=200, verbose_name='Ссылка на изображение')),
                ('H', models.IntegerField(verbose_name='Номер обхода')),
            ],
        ),
    ]