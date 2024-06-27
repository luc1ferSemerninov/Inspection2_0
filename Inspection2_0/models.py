from django.db import models

class Start(models.Model):
    time_start = models.TimeField("Время начала")
    group_id = models.BigIntegerField("Айди группы")
    zone = models.TextField("Название обхода",max_length=100)
    department = models.TextField("Отдел",max_length=50)
    H = models.IntegerField("Номер обхода", default='1')

    def __str__(self):
        return f"{self.department} - {self.zone}"
    
    
class Operator(models.Model):
    idPunkt = models.IntegerField("Чек номер")
    Zone = models.TextField("Зона",max_length=100)
    ToDo = models.TextField("Название задачи", max_length=200)
    link = models.TextField("Ссылка на изображение", max_length=200)
    H = models.IntegerField("Номер обхода")
    department = models.CharField(max_length=50, default="operator")

class Admin(models.Model):
    idPunkt = models.IntegerField("Чек номер")
    Zone = models.TextField("Зона",max_length=100)
    ToDo = models.TextField("Название задачи", max_length=200)
    link = models.TextField("Ссылка на изображение", max_length=200)
    department = models.CharField(max_length=50, default="admin")
    H = models.IntegerField("Номер обхода")


class Animator(models.Model):
    idPunkt = models.IntegerField("Чек номер")
    Zone = models.TextField("Зона",max_length=100)
    ToDo = models.TextField("Название задачи", max_length=200)
    link = models.TextField("Ссылка на изображение", max_length=200)
    department = models.IntegerField("Номер отдела", default=0)
    H = models.IntegerField("Номер обхода")


class Cashier(models.Model):
    idPunkt = models.IntegerField("Чек номер")
    Zone = models.TextField("Зона",max_length=100)
    ToDo = models.TextField("Название задачи", max_length=200)
    link = models.TextField("Ссылка на изображение", max_length=200)
    department = models.IntegerField("Номер отдела", default=0)
    H = models.IntegerField("Номер обхода")


class AdminHBD(models.Model):
    idPunkt = models.IntegerField("Чек номер")
    Zone = models.TextField("Зона",max_length=100)
    ToDo = models.TextField("Название задачи", max_length=200)
    link = models.TextField("Ссылка на изображение", max_length=200)
    department = models.IntegerField("Номер отдела", default=0)
    H = models.IntegerField("Номер обхода")


class Waiter(models.Model):
    idPunkt = models.IntegerField("Чек номер")
    Zone = models.TextField("Зона",max_length=100)
    ToDo = models.TextField("Название задачи", max_length=200)
    link = models.TextField("Ссылка на изображение", max_length=200)
    department = models.IntegerField("Номер отдела", default=0)
    H = models.IntegerField("Номер обхода")


class User(models.Model):
    datetime = models.TextField("Дата")
    userid = models.IntegerField("Айди")
    username = models.TextField("Имя")
    number = models.TextField("Номер телефона")
    department = models.TextField("Отдел")
    admin = models.BooleanField("Администратор", default=False)
    
    def __str__(self):
        return f"{self.datetime} - {self.userid} - {self.username} - {self.number} - {self.department}"

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