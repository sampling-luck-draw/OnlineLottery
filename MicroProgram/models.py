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
    nickName = models.CharField(max_length=64)
    avatarUrl = models.URLField()
    gender = models.SmallIntegerField()
    country = models.CharField(max_length=64)
    province = models.CharField(max_length=64)
    city = models.CharField(max_length=64)
    language = models.CharField(max_length=16)
    activate_in = models.IntegerField(null=True)

    def __str__(self):
        return "{} {}".format(self.openid, self.nickName)


class Activity(models.Model):
    name = models.CharField(max_length=64)
    belong = models.ForeignKey(to=Organizer, on_delete=models.PROTECT)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    participants = models.ManyToManyField(to=Participant, blank=True)

    def __str__(self):
        return self.name


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
