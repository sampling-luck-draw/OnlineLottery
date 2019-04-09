import datetime
import json
import time
import requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from .models import Participant, Danmu, Activity

from Lottery.secret import xcx_appid, xcx_appsecret


@require_POST
@csrf_exempt
def send_danmu(request):
    post_data = json.loads(request.body.decode('utf-8'))
    openid = post_data.get('openid', '')
    if not openid:
        return HttpResponse('{"result":"error", "msg":"no openid"}')
    text = post_data.get('danmu', '')
    if not text:
        return HttpResponse('{"result":"error", "msg":"no danmu"}')

    danmu = Danmu()
    try:
        danmu.sender = Participant.objects.get(openid=openid)
    except Participant.DoesNotExist:
        return HttpResponse('{"result":"error", "msg":"no such user"}')
    danmu.text = text
    danmu.time = datetime.datetime.now()
    try:
        danmu.activity = Activity.objects.get(id=danmu.sender.activate_in)
    except Activity.DoesNotExist:
        return HttpResponse('{"result":"error", "msg":"no such activity"}')
    danmu.save()

    channel_layer = get_channel_layer()

    post_data['uid'] = post_data['openid']
    del post_data['openid']
    async_to_sync(channel_layer.send)(
        'console_' + str(danmu.sender.activate_in),
        {
            'type': 'chat_message',
            'text': json.dumps(
            {'action': 'send-danmu', 'content': post_data})
        }
    )

    return HttpResponse('{"result": "ok"}')


xcx_token_expire_time = 0
xcx_token = ''


def get_token(request):
    if request.method != 'GET':
        return HttpResponse('Hello')
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(
        xcx_appid, xcx_appsecret)
    global xcx_token_expire_time, xcx_token
    if xcx_token_expire_time - time.time() <= 0:
        r = requests.get(url).content.decode()
        o = json.loads(r)
        if 'access_token' in o:
            xcx_token_expire_time = time.time() + o['expires_in']
            xcx_token = o['access_token']
        else:
            return HttpResponse(r)  # 返回错误代码
    return HttpResponse(xcx_token)


@require_POST
@csrf_exempt
def login(request):
    """
    用于小程序的“登陆”功能，获得用户openid和session_key
    """
    post_data = json.loads(request.body.decode('utf-8'))
    code = post_data.get('code', '')
    if not code:
        return HttpResponse('{"result":"error", "msg":"no code"}')
    response = requests.get('https://api.weixin.qq.com/sns/jscode2session?'
                            'appid={}&secret={}&js_code={}&grant_type=authorization_code'
                            .format(xcx_appid, xcx_appsecret, code))
    decode = json.loads(response.content.decode())
    openid = decode.get('openid', '')

    if not openid:
        return HttpResponse(response.content)

    try:
        xcx_user = Participant.objects.get(openid=openid)
    except Participant.DoesNotExist:
        xcx_user = Participant(openid=openid)

    xcx_user.nickName = post_data.get('nickName', 'Anonymous.')
    xcx_user.avatarUrl = post_data.get('avatarUrl', 'default_avatar')
    xcx_user.gender = post_data.get('gender', 0)
    xcx_user.country = post_data.get('country', 'Solar System')
    xcx_user.province = post_data.get('province', 'Alpha Centauri')
    xcx_user.city = post_data.get('city', 'Proxima Centauri')
    xcx_user.language = post_data.get('language', 'Xenolinguistics')
    activity_id = post_data.get('activity_id', None)
    xcx_user.activate_in = activity_id
    xcx_user.save()
    decode['result'] = 'ok'
    post_data['uid'] = openid
    post_data['avatar'] = post_data['avatarUrl']
    post_data['nickname'] = post_data['nickName']
    del post_data['avatarUrl']
    del post_data['code']
    del post_data['nickName']

    try:
        a = Activity.objects.get(id=activity_id)
        a.participants.add(xcx_user)
        a.save()
        decode['activity_name'] = a.name
        decode['activity_status'] = 'Running'  # TODO: status
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.send)(
            "console_" + str(activity_id), {'type': 'chat.message', 'text': json.dumps(
                {'action': 'append-user', 'content': post_data})})
    except Activity.DoesNotExist:
        decode['activity_name'] = 'cmy'
        decode['activity_status'] = 'no such activity'
    return HttpResponse(json.dumps(decode))


@require_POST
@csrf_exempt
def join(request):
    try:
        post_data = json.loads(request.body.decode('utf-8'))
        openid = post_data.get('openid', None)
        user = Participant.objects.get(openid=openid)
        activity_id = post_data.get('activity_id')
        activity = Activity.objects.get(id=activity_id)
        activity.participants.add(user)
        user.activate_in = activity_id
        activity.save()
        user.save()
    except json.JSONDecodeError:
        return HttpResponse('{"result": "json decode error"}')
    except KeyError:
        return HttpResponse('{"result": "no open id or activity"}')
    except Participant.DoesNotExist:
        return HttpResponse('{"result": "no such user"}')
    except Activity.DoesNotExist:
        return HttpResponse('{"result": "no such activity"}')

    return JsonResponse({'result': 'ok',
                         'activity_name': activity.name,
                         'activity_status': 'Running'})
