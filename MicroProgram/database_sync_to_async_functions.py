from channels.db import database_sync_to_async
import datetime

from MicroProgram import models
from Pages.utils import *


@database_sync_to_async
def get_organizer(user):
    return models.Organizer.objects.get(user=user)


@database_sync_to_async
def get_latest_activity(organizer):
    if models.Activity.objects.filter(belong=organizer).count() > 0:
        return models.Activity.objects.filter(belong=organizer).order_by('-id')[0]
    return None


@database_sync_to_async
def get_activity_by_id(activity_id):
    return models.Activity.objects.get(id=activity_id)


@database_sync_to_async
def get_participants_by_activity(activity):
    return models.Participant.objects.filter(activity=activity)


@database_sync_to_async
def get_awards_by_activity(activity):
    return models.Award.objects.filter(activity=activity)


@database_sync_to_async
def add_lucky_dog(activity, participant_id, award_name):
    try:
        participant = models.Participant.objects.get(openid=participant_id)
        award = models.Award.objects.get(activity=activity, award_name=award_name)
    except models.Participant.DoesNotExist:
        return "no such user"
    except models.Award.DoesNotExist:
        return "no such award"
    award.lucky_dogs.add(participant)
    award.save()
    return None


@database_sync_to_async
def add_award(activity, award_name, prize_name, amount):
    award = models.Award()
    award.activity = activity
    award.award_name = award_name
    award.prize_name = prize_name
    award.amount = amount
    award.save()


@database_sync_to_async
def delete_award(activity, name):
    models.Award.objects.get(activity=activity, award_name=name).delete()


@database_sync_to_async
def modify_activity(activity, content):
    if 'name' in content:
        activity.name = content['name']
    if 'start_time' in content:
        activity.start_time = local_to_utc(datetime.datetime.strptime(content['start_time'], "%Y-%m-%d %H:%M:%S"))

    if 'end_time' in content:
        activity.end_time = local_to_utc(datetime.datetime.strptime(content['end_time'], "%Y-%m-%d %H:%M:%S"))

    # for k, v in content.items():
    #     if hasattr(activity, k):
    #         setattr(activity, k, v)
    activity.save()


@database_sync_to_async
def get_lucky_dogs_by_activity(activity):
    return list(models.Award.objects.filter(activity=activity).values_list('award_name', 'lucky_dogs'))


@database_sync_to_async
def add_participant(content, activity):
    try:
        participant = models.Participant.objects.get(openid=content['uid'])
    except models.Participant.DoesNotExist:
        participant = models.Participant()
        participant.openid = content['uid']

    participant.nickName = content.get('nickname', 'Anonymous.')
    participant.avatarUrl = content.get('avatar', 'default_avatar')
    participant.gender = content.get('gender', 0)
    participant.country = content.get('country', 'Solar System')
    participant.province = content.get('province', 'Alpha Centauri')
    participant.city = content.get('city', 'Proxima Centauri')
    participant.activate_in = activity.id
    participant.save()
    activity.participants.add(participant)
    activity.save()

    return participant

