from channels.db import database_sync_to_async
from MicroProgram import models


@database_sync_to_async
def get_organizer(user):
    return models.Organizer.objects.get(user=user)


@database_sync_to_async
def get_latest_activity(organizer):
    return models.Activity.objects.filter(belong=organizer).order_by('-id')[0]


@database_sync_to_async
def get_activity_by_id(activity_id):
    return models.Activity.objects.get(id=activity_id)


@database_sync_to_async
def get_participants_by_activity(activity):
    return models.Participant.objects.filter(activity=activity)


@database_sync_to_async
def add_lucky_dog(activity, participant_id, award_name):
    participant = models.Participant.objects.get(id=participant_id)
    award = models.Award.objects.get(activity=activity, award_name=award_name)
    award.lucky_dogs.add(participant)
    award.save()


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


