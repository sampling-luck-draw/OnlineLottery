import collections
import json
from functools import reduce

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

import MicroProgram.models as models
from Pages.function import _get_activity, _get_activities
from Pages.province import province_dict
from Pages.utils import utc_to_local, id_to_invite_code


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


@require_GET
@login_required(login_url='/signin')
def usercenter(request):
    user = request.user
    organizer = models.Organizer.objects.get(user=user)
    # request.session['activity'] = 4
    activities = models.Activity.objects.filter(belong=organizer).order_by('-id')

    cnt = activities.count()
    if cnt > 0:
        overall = {
            'activity_count': cnt,
            'participant_count': activities.values('participants').exclude(participants=None).count(),
            'time_count': reduce(lambda a, b: a + b,
                                 map(lambda a: a.during, activities)).seconds // 3600,
            'prize_draw_count': models.Award.objects.filter(activity__in=activities).count(),
            'danmu_count': activities.values('danmu').exclude(danmu=None).count(),
            'last_time': activities[0].start_time
        }
        overall['average_participant'] = overall['participant_count'] / overall['activity_count']
        overall['average_time'] = overall['time_count'] / overall['activity_count']
        overall['average_prize'] = overall['prize_draw_count'] / overall['activity_count']
        overall['average_danmu'] = overall['danmu_count'] / overall['activity_count']
    else:
        overall = {
            'activity_count': 0, 'participant_count': 0, 'prize_draw_count': 0,
            'danmu_count': 0, 'last_time': 0, 'time_count': 0
        }

    return render(request, 'pages/usercenter/usercenter.html',
                  {'activities': activities, 'overall': overall})


@require_GET
@login_required(login_url='/signin')
def danmu_manage(request):
    activity = _get_activity(request, True)
    if isinstance(activity, HttpResponse):
        return activity

    activities = _get_activities(request)

    danmu_times = models.Danmu.objects.filter(activity=activity).only('time')
    danmu_time_range = {}
    for danmu_time in danmu_times:
        minute = danmu_time.time.minute
        minute = minute // 10
        key = utc_to_local(danmu_time.time).strftime("%Y-%m-%d %H:") + str(minute) + '0'
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
    activity = _get_activity(request, True)
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
    province_statistics = [{"name": province_dict.get(k, k), "value": v} for k, v in province_statistics.items()]

    return render(request, 'pages/usercenter/participants_list.html',
                  {'participants': participant, 'activity': activity, 'gender_statistics': gender_statistics,
                   'province_statistics': json.dumps(province_statistics), 'activities': activities})


@login_required(login_url='/signin')
def activity_manage(request):
    activity = _get_activity(request, True)
    if isinstance(activity, HttpResponse):
        return activity

    activities = _get_activities(request)
    awards = models.Award.objects.filter(activity=activity)

    return render(request, 'pages/usercenter/activity_page.html',
                  {'activity': activity, 'activities': activities,
                   'awards': awards, 'invite_code': id_to_invite_code(activity.id)})
