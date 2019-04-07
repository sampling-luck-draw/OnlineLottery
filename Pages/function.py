import datetime
import json

import pytz
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.views.decorators.http import require_GET

from Lottery import settings
from MicroProgram import models


def _get_activities(request):
    user = request.user
    organizer = models.Organizer.objects.get(user=user)
    return models.Activity.objects.filter(belong=organizer).all()


def _get_activity(request):
    user = request.user
    organizer = models.Organizer.objects.get(user=user)

    activity_id = request.GET.get('activity', None)
    if not activity_id:
        activity_id = request.session.get('activity', None)
    else:
        request.session['activity'] = activity_id

    if not activity_id:
        return HttpResponseNotFound('no activity id')

    activity = models.Activity.objects.get(id=activity_id)
    if activity.belong != organizer:
        return HttpResponseNotFound('unauthorized')

    return activity


def utc_to_local(utc_dt):
    # return utc_dt.astimezone(tz=pytz.timezone(settings.TIME_ZONE))
    return utc_dt + datetime.timedelta(hours=8)


@require_GET
@login_required(login_url='/signin')
def get_danmu(request):
    activity = _get_activity(request)
    if isinstance(activity, HttpResponse):
        return activity

    start = int(request.GET.get('start', 0))
    danmus = models.Danmu.objects.filter(activity=activity)
    danmus_count = danmus.count()
    length = int(request.GET.get('length', danmus_count))
    end = min(start + length, danmus_count)
    danmus = danmus.order_by("-id")[start: end]
    participants_dict = dict([(k['openid'], k['nickName']) for k in activity.participants.values('openid', 'nickName')])

    danmu_list = [{
        'id': d.id,
        'openid': d.sender.openid,
        'nickName': participants_dict[d.sender.openid],
        'text': d.text,
        'time': d.time.strftime("%Y-%m-%d %H:%M:%S")
    } for d in danmus]

    return HttpResponse(json.dumps({
        'draw': request.GET.get('draw', 0),
        'recordsTotal': danmus_count,
        'recordsFiltered': danmus_count,
        'data': danmu_list
    }), content_type='application/json')


@require_GET
@login_required(login_url='/signin')
def get_participants(request):
    organizer = models.Organizer.objects.get(user=request.user)
    activity_id = request.GET.get('activity', None)
    if not activity_id:
        return HttpResponseNotFound('no activity id')

    try:
        activity = models.Activity.objects.get(id=activity_id)
        if activity.belong != organizer:
            return HttpResponseNotFound('unauthenticated')
    except models.Activity.DoesNotExist:
        return HttpResponseNotFound('no this activity')

    participants = activity.participants.all()
    json_str = [{
        'id': i.pk,
        'nickName': i.nickName,
        'avatarUrl': i.avatarUrl,
        'gender': i.gender,
        'country': i.country,
        'province': i.province,
        'city': i.city,
        'language': i.language
    } for i in participants]
    return HttpResponse(json.dumps(json_str), content_type='application/json')


@require_GET
@login_required(login_url='/signin')
def get_activities(request):
    activities = _get_activities(request)
    json_str = [{
        'id': i.id,
        'name': i.name,
        'start_time': utc_to_local(i.start_time).strftime("%Y-%m-%d %H:%M:%S"),
        'end_time': utc_to_local(i.end_time).strftime("%Y-%m-%d %H:%M:%S")
    } for i in activities]
    return HttpResponse(json.dumps(json_str), content_type='application/json')
