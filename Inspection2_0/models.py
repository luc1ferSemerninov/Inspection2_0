from django.db import models
 
class Start(models.Model):
    time_start = models.TimeField("Время начала")
    group_id = models.BigIntegerField("Айди группы")
    zone = models.TextField("Зона",max_length=50)
    task = models.TextField("Задача",max_length=200)
    department = models.TextField("Отдел",max_length=50)
    H = models.IntegerField("Номер обхода", default='1')

    def __str__(self):
        return f"{self.department} - {self.H}"