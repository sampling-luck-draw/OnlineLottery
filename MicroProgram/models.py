from django.db import models
from django.contrib.auth.models import User


class Organizer(models):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)
    level = models.IntegerField(default=0)


class Activity(models):
    name = models.CharField(max_length=64)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class Participant(models):
    nick_name = models.CharField(max_length=64)
    avatar = models.URLField()
    gender = models.SmallIntegerField()
    country = models.CharField(max_length=64)
    province = models.CharField(max_length=64)
    city = models.CharField(max_length=64)
    language = models.CharField(max_length=16)

