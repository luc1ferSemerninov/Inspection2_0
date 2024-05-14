from django.db import models

class Start(models.Model):
    time_start = models.TimeField("Время начала")
    group_id = models.BigIntegerField("Айди группы")
    zone = models.TextField("Название обхода",max_length=100)
    department = models.TextField("Отдел",max_length=50)
    H = models.IntegerField("Номер обхода", default='1')

    def __str__(self):
        return f"{self.department} - {self.H}"
    
    
class Operators(models.Model):
    idPunkt = models.IntegerField("Пункт")
    Zone = models.TextField("Зона",max_length=100)
    ToDo = models.TextField("Задача", max_length=200)
    link = models.TextField("Картинка", max_length=200)
    H = models.IntegerField("Номер обхода")



class log(models.Model):
    date = models.DateField()
    time = models.TimeField()
    who = models.TextField(max_length=50)
    teleid = models.TextField(max_length=50)
    zone = models.TextField(max_length=50)
    result = models.BooleanField()
    comment = models.TextField(max_length=200)
    punkt = models.IntegerField()
    message_id = models.BigIntegerField()
    department = models.TextField(max_length=100)
    H = models.IntegerField()
    
    def __str__(self):
        return f"{self.date} - {self.time} - {self.who} - {self.teleid} - {self.zone} - {self.result} - {self.comment} - {self.punkt} - {self.message_id} - {self.department} - {self.H}"