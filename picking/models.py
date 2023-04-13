from django.db import models


class Task(models.Model):
    number = models.CharField(max_length=250, unique=True)
    name = models.CharField(max_length=250)
    difficulty = models.IntegerField()
    topic = models.CharField(max_length=250)
    solution = models.IntegerField()
    text_task = models.URLField(max_length=200)








