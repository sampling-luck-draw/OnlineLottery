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
