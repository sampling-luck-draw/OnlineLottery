from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http import HttpResponseForbidden, HttpResponseNotFound, JsonResponse, HttpResponse
from django.shortcuts import render
import MicroProgram.models as models


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
    activities = models.Activity.objects.filter(belong=organizer)
    return render(request, 'Pages/usercenter/usercenter.html',
                  {'activities': activities})


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
