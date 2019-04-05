from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http import HttpResponseForbidden, HttpResponseNotFound, JsonResponse, HttpResponse
from django.shortcuts import render
import MicroProgram.models as models
from functools import reduce


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

    return render(request, 'Pages/usercenter/usercenter.html',
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
def danmu_manage(request):
    return render(request, 'pages/usercenter/danmu_list.html')


@login_required(login_url='/signin')
def participant_manage(request):
    return render(request, 'pages/usercenter/participants_list.html')
