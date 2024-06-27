# Generated by Django 5.0.4 on 2024-06-27 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Inspection2_0', '0019_user_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='name',
            field=models.TextField(default='Безымянный', verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.TextField(verbose_name='Username'),
        ),
    ]