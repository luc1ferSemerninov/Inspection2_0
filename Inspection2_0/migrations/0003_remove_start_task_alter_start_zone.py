# Generated by Django 5.0.4 on 2024-05-13 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Inspection2_0', '0002_start_h_alter_start_department_alter_start_group_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='start',
            name='task',
        ),
        migrations.AlterField(
            model_name='start',
            name='zone',
            field=models.TextField(max_length=100, verbose_name='Название обхода'),
        ),
    ]
