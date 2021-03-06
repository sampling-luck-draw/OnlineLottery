import datetime
import json
import time

import requests
from io import BytesIO
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.files.images import ImageFile
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from Lottery.secret import xcx_appid, xcx_appsecret
from MicroProgram.functions import send_danmu
from .models import Participant, Danmu, Activity


@require_POST
@csrf_exempt
def xcx_send_danmu(request):
    post_data = json.loads(request.body.decode('utf-8'))
    openid = post_data.get('openid', '')
    if not openid:
        return HttpResponse('{"result":"error", "msg":"no openid"}')
    text = post_data.get('danmu', '')
    if not text:
        return HttpResponse('{"result":"error", "msg":"no danmu"}')

    try:
        participant = Participant.objects.get(openid=openid)
    except Participant.DoesNotExist:
        return HttpResponse('{"result":"error", "msg":"no such user"}')
    send_danmu(participant, text)

    return HttpResponse('{"result": "ok"}')


xcx_token_expire_time = 0
xcx_token = ''


def get_token():
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(
        xcx_appid, xcx_appsecret)
    global xcx_token_expire_time, xcx_token
    if xcx_token_expire_time - time.time() <= 0:
        r = requests.get(url).content.decode()
        o = json.loads(r)
        if 'access_token' in o:
            xcx_token_expire_time = time.time() + o['expires_in']
            xcx_token = o['access_token']
            return o['access_token']
        else:
            return r  # 返回错误代码
    return xcx_token


def get_token_http(request):
    if request.method != 'GET':
        return HttpResponse('Hello')
    return HttpResponse(get_token())


@require_POST
@csrf_exempt
def login(request):
    """
    用于小程序的“登陆”功能，获得用户openid和session_key
    """
    post_data = json.loads(request.body.decode('utf-8'))
    print(request.body.decode('utf-8'))
    code = post_data.get('code', '')
    if not code:
        return HttpResponse('{"result":"error", "msg":"no code"}')
    response = requests.get('https://api.weixin.qq.com/sns/jscode2session?'
                            'appid={}&secret={}&js_code={}&grant_type=authorization_code'
                            .format(xcx_appid, xcx_appsecret, code))
    decode = json.loads(response.content.decode())
    openid = decode.get('openid', '')

    if not openid:
        print(response.content)
        parse_response = json.loads(response.content)
        decode['errcode'] = parse_response.get('errcode')
        decode['errmsg'] = parse_response.get('errmsg')
        avatar = post_data.get('avatarUrl', None)
        if avatar is None:
            return HttpResponse(response.content)
        openid = Participant.objects.get(avatar=avatar).openid
        decode['openid'] = openid

    try:
        xcx_user = Participant.objects.get(openid=openid)
    except Participant.DoesNotExist:
        xcx_user = Participant(openid=openid)

    xcx_user.nickname = post_data.get('nickName', 'Anonymous.')
    xcx_user.avatar = post_data.get('avatarUrl', 'default_avatar')
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
        activity = Activity.objects.get(id=activity_id)
        activity.participants.add(xcx_user)
        activity.save()
        decode['activity_name'] = activity.name
        decode['activity_status'] = activity.status
        del post_data['activity_id']
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "console_" + str(activity_id), {'type': 'chat.message', 'text': json.dumps(
                {'action': 'append-user', 'content': post_data})})
    except Activity.DoesNotExist:
        decode['activity_name'] = '<ERROR>'
        decode['activity_status'] = 'no such activity' if activity_id is not None else 'no activity id'
    print(json.dumps(decode))
    return HttpResponse(json.dumps(decode))


@require_POST
@csrf_exempt
def join(request):
    try:
        post_data = json.loads(request.body.decode('utf-8'))
        openid = post_data['openid']
        user = Participant.objects.get(openid=openid)
        activity_id = post_data['activity_id']
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

    del post_data['activity_id']
    post_data['uid'] = openid
    del post_data['openid']
    # xcx_user.nickname = post_data.get('nickName', 'Anonymous.')
    # xcx_user.avatar = post_data.get('avatarUrl', 'default_avatar')
    # xcx_user.gender = post_data.get('gender', 0)
    # xcx_user.country = post_data.get('country', 'Solar System')
    # xcx_user.province = post_data.get('province', 'Alpha Centauri')
    # xcx_user.city = post_data.get('city', 'Proxima Centauri')
    # xcx_user.language = post_data.get('language', 'Xenolinguistics')
    post_data['nickname'] = user.nickname
    post_data['avatar'] = user.avatar
    post_data['gender'] = user.gender
    post_data['country'] = user.country
    post_data['province'] = user.province
    post_data['city'] = user.city
    post_data['language'] = user.language
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "console_" + str(activity_id), {'type': 'chat.message', 'text': json.dumps(
            {'action': 'append-user', 'content': post_data})}
    )

    return JsonResponse({'result': 'ok',
                         'activity_name': activity.name,
                         'activity_status': activity.status})


def get_wxa_code(request):
    try:
        activity_id = request.GET['activity_id']
        activity = Activity.objects.get(id=activity_id)
        if activity.qrcode is not None:
            try:
                return HttpResponse(activity.qrcode.read(), content_type="image/jpeg")
            except ValueError:
                pass
    except KeyError:
        return HttpResponse('{"error": "no activity id"}')
    except Activity.DoesNotExist:
        return HttpResponse('{"error": "wrong activity"}')
    print('quest qa code for activity ' + str(activity_id))
    url = 'https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token=' + get_token()
    data = {
        'scene': str(activity_id),
        'page': 'pages/room/room'
    }
    print(data)
    # url = 'http://127.0.0.1:9000/avatar.png'

    response = requests.post(url, json=data)
    if 'application/json' in response.headers.get('Content-Type'):
        return HttpResponse(response.text)

    i = ImageFile(BytesIO(response.content), name="activity_qr_code_" + activity_id)
    activity.qrcode = i
    activity.save()
    return HttpResponse(response.content, content_type=response.headers['Content-Type'])


