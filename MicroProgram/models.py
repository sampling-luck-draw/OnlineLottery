import datetime

from django.db import models
from django.contrib.auth.models import User


class Organizer(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.PROTECT)
    balance = models.IntegerField(default=0)
    level = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


class Participant(models.Model):
    openid = models.CharField(primary_key=True, max_length=32)
    nickName = models.CharField(max_length=64, null=True)
    avatarUrl = models.URLField(null=True)
    gender = models.SmallIntegerField(null=True)
    country = models.CharField(max_length=64, null=True)
    province = models.CharField(max_length=64, null=True)
    city = models.CharField(max_length=64, null=True)
    language = models.CharField(max_length=16, null=True)
    activate_in = models.IntegerField(null=True)

    def __str__(self):
        return "{} {}".format(self.openid, self.nickName)




class Activity(models.Model):
    name = models.CharField(max_length=64)
    belong = models.ForeignKey(to=Organizer, on_delete=models.PROTECT)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    participants = models.ManyToManyField(to=Participant, blank=True)
    qrcode = models.ImageField(null=True)

    def __str__(self):
        return self.name

    @property
    def during(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        else:
            return datetime.timedelta()

    @property
    def status(self):
        if self.start_time is None or self.start_time < datetime.datetime.now(datetime.timezone.utc):
            return "Pending"
        if self.end_time and self.end_time < datetime.datetime.now(datetime.timezone.utc):
            return "Finished"
        return "Running"


class Danmu(models.Model):
    sender = models.ForeignKey(to=Participant, on_delete=models.PROTECT)
    activity = models.ForeignKey(to=Activity, on_delete=models.PROTECT)
    text = models.TextField()
    time = models.DateTimeField()

    def __str__(self):
        return "{}: {} @ {} {}".format(self.sender.nickName, self.text, self.activity, self.time)


class Award(models.Model):
    award_name = models.CharField(max_length=64)
    prize_name = models.CharField(max_length=64)
    amount = models.IntegerField()
    activity = models.ForeignKey(to=Activity, on_delete=models.PROTECT)
    lucky_dogs = models.ManyToManyField(to=Participant, blank=True)
