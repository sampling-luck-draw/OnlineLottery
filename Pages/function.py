import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_GET, require_POST

from MicroProgram import models
from Pages.utils import utc_to_local


def _get_activities(request):
    user = request.user
    organizer = models.Organizer.objects.get(user=user)
    return models.Activity.objects.filter(belong=organizer).all()


def _get_activity(request, default=False):
    user = request.user
    organizer = models.Organizer.objects.get(user=user)

    activity_id = request.GET.get('activity', None)
    if not activity_id:
        activity_id = request.session.get('activity', None)
    else:
        request.session['activity'] = activity_id

    if not activity_id:
        if default:
            if models.Activity.objects.filter(belong=organizer).count() > 0:
                return models.Activity.objects.filter(belong=organizer).order_by('-id')[0]
            else:
                return HttpResponseRedirect('/usercenter')
        else:
            return HttpResponseNotFound('no activity id')

    activity = models.Activity.objects.get(id=activity_id)
    if activity.belong != organizer:
        return HttpResponseRedirect('/signin')

    return activity


def exempt_cross_region(response):
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST,GET,OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response


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
    activity = _get_activity(request, True)

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


@require_POST
@login_required(login_url='/signin')
def append_activity(request):
    user = request.user
    organizer = models.Organizer.objects.get(user=user)
    activity = models.Activity()
    activity.belong = organizer
    activity.save()
    return JsonResponse({'activity_id': activity.id})
