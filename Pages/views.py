import collections
import datetime
import json
from functools import reduce

from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http import HttpResponseNotFound, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

import MicroProgram.models as models
from Pages.province import province_dict


def index(request):
    return render(request, 'pages/index-new.html')


def test_ws(request):
    return render(request, 'test_channel.html')


def get_csrf(request):
    return render(request, 'get_csrf.html')


def signin(request):
    return render(request, 'pages/signin.html')


def signup(request):
    return render(request, 'pages/signup.html')


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


@require_GET
@login_required(login_url='/signin')
def usercenter(request):
    user = request.user
    organizer = models.Organizer.objects.get(user=user)
    # request.session['activity'] = 4
    activities = models.Activity.objects.filter(belong=organizer).order_by('-id')

    overall = {
        'activity_count': activities.count(),
        'participant_count': activities.values('participants').exclude(participants=None).count(),
        'time_count': reduce(lambda a, b: a + b,
                             map(lambda a: a['end_time'] - a['start_time'],
                                 activities.values('start_time', 'end_time'))).seconds // 3600,
        'prize_draw_count': 130,
        'danmu_count': activities.values('danmu').exclude(danmu=None).count(),
        'least_time': activities[0].start_time
    }

    overall['average_participant'] = overall['participant_count'] / overall['activity_count']
    overall['average_time'] = overall['time_count'] / overall['activity_count']
    overall['average_prize'] = overall['prize_draw_count'] / overall['activity_count']
    overall['average_danmu'] = overall['danmu_count'] / overall['activity_count']

    return render(request, 'pages/usercenter/usercenter.html',
                  {'activities': activities, 'overall': overall})


@require_GET
@login_required(login_url='/signin')
def get_participants(request):

    activity = _get_activity(request)
    if isinstance(activity, HttpResponse):
        return activity

    participants = activity.participants.all()
    qs_json = serializers.serialize('json', participants)
    return HttpResponse(qs_json, content_type='application/json')


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
def danmu_manage(request):
    activity = _get_activity(request)
    if isinstance(activity, HttpResponse):
        return activity

    activities = _get_activities(request)

    danmu_times = models.Danmu.objects.filter(activity=activity).only('time')
    danmu_time_range = {}
    for danmu_time in danmu_times:
        minute = danmu_time.time.minute
        minute = 3 if minute > 30 else 0
        # TODO: **Important** Dynamic time zone
        danmu_time.time += datetime.timedelta(hours=8)
        key = danmu_time.time.strftime("%Y-%m-%d %H:") + str(minute)
        if key not in danmu_time_range:
            danmu_time_range[key] = 1
        else:
            danmu_time_range[key] += 1

    return render(request, 'pages/usercenter/danmu_list.html',
                  {'danmu_time_range': json.dumps(danmu_time_range),
                   'activity': activity, 'activities': activities})


@require_GET
@login_required(login_url='/signin')
def participant_manage(request):
    activity = _get_activity(request)
    if isinstance(activity, HttpResponse):
        return activity

    activities = _get_activities(request)

    participant = activity.participants.all()
    gender_statistics_male = participant.filter(gender=1).count()
    gender_statistics_female = participant.filter(gender=2).count()
    gender_statistics_other = participant.count() - gender_statistics_female - gender_statistics_male
    gender_statistics = {'male': gender_statistics_male,
                         'female': gender_statistics_female, 'other': gender_statistics_other}

    province_statistics = collections.Counter(participant.values_list('province', flat=True))
    province_statistics = [{"name": province_dict.get(k), "value": v} for k, v in province_statistics.items()]

    return render(request, 'pages/usercenter/participants_list.html',
                  {'participants': participant, 'activity': activity, 'gender_statistics': gender_statistics,
                   'province_statistics': json.dumps(province_statistics), 'activities': activities})


@login_required(login_url='/signin')
def activity_manage(request):
    activity = _get_activity(request)
    if isinstance(activity, HttpResponse):
        return activity

    activities = _get_activities(request)

    return render(request, 'pages/usercenter/activity_page.html',
                  {'activity': activity, 'activities': activities})
