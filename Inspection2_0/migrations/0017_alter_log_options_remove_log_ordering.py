# Generated by Django 5.0.6 on 2024-06-10 11:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Inspection2_0', '0016_alter_log_options_log_ordering_alter_operator_todo_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='log',
            options={},
        ),
        migrations.RemoveField(
            model_name='log',
            name='ordering',
        ),
    ]
