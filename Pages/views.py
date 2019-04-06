import collections
import datetime
import json

from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max
from django.http import HttpResponseForbidden, HttpResponseNotFound, JsonResponse, HttpResponse
from django.shortcuts import render
import MicroProgram.models as models
from functools import reduce
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


@login_required(login_url='/signin')
def usercenter(request):
    user = request.user
    organizer = models.Organizer.objects.get(user=user)
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


@login_required(login_url='/signin')
def get_participants(request, activity_id):
    if request.method != 'GET':
        return HttpResponseForbidden()

    user = request.user
    organizer = models.Organizer.objects.get(user=user)
    activity = models.Activity.objects.get(id=activity_id)
    if activity.belong != organizer:
        return HttpResponseNotFound()
    participants = activity.participants.all()
    qs_json = serializers.serialize('json', participants)
    return HttpResponse(qs_json, content_type='application/json')


@login_required(login_url='/signin')
def get_danmu(request):
    if request.method != 'GET':
        return HttpResponseForbidden()

    user = request.user
    organizer = models.Organizer.objects.get(user=user)
    activity_id = request.GET.get('a', None)
    if not activity_id:
        return HttpResponseNotFound()
    activity_id = int(activity_id)
    start = int(request.GET.get('start'))
    length = int(request.GET.get('length'))
    activity = models.Activity.objects.get(id=activity_id)
    if activity.belong != organizer:
        return HttpResponseNotFound()

    danmus = models.Danmu.objects.filter(activity=activity)
    danmus_count = danmus.count()
    danmus = danmus.order_by("-id")[start: start + length]
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


@login_required(login_url='/signin')
def danmu_manage(request):
    return render(request, 'pages/usercenter/danmu_list.html')


@login_required(login_url='/signin')
def participant_manage(request):
    user = request.user
    organizer = models.Organizer.objects.get(user=user)
    activity_id = request.GET.get('a', None)
    try:
        activity = models.Activity.objects.get(id=activity_id)
    except ObjectDoesNotExist:
        activity = models.Activity.objects.filter(belong=organizer).order_by('-id')[0]

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
                   'province_statistics': json.dumps(province_statistics)})


@login_required(login_url='/signin')
def activity_manage(request):
    return render(request, 'pages/usercenter/activity_page.html')
