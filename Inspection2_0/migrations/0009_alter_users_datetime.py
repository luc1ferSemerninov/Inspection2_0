# Generated by Django 5.0.6 on 2024-05-25 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Inspection2_0', '0008_remove_operators_userid_alter_users_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='datetime',
            field=models.TextField(verbose_name='Дата'),
        ),
    ]
