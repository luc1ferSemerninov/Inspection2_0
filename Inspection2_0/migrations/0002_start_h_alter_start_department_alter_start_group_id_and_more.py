# Generated by Django 5.0.4 on 2024-05-13 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Inspection2_0', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='start',
            name='H',
            field=models.IntegerField(default='1', verbose_name='Номер обхода'),
        ),
        migrations.AlterField(
            model_name='start',
            name='department',
            field=models.TextField(max_length=50, verbose_name='Отдел'),
        ),
        migrations.AlterField(
            model_name='start',
            name='group_id',
            field=models.BigIntegerField(verbose_name='Айди группы'),
        ),
        migrations.AlterField(
            model_name='start',
            name='task',
            field=models.TextField(max_length=200, verbose_name='Задача'),
        ),
        migrations.AlterField(
            model_name='start',
            name='time_start',
            field=models.TimeField(verbose_name='Время начала'),
        ),
        migrations.AlterField(
            model_name='start',
            name='zone',
            field=models.TextField(max_length=50, verbose_name='Зона'),
        ),
    ]
