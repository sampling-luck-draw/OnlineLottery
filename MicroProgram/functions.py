import datetime
import json
import time
import requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from .models import Participant, Danmu, Activity

from Lottery.secret import xcx_appid, xcx_appsecret


@csrf_exempt
def send_danmu(request):
    if request.method != 'POST':
        return HttpResponseForbidden('Forbidden')
    post_data = json.loads(request.body.decode('utf-8'))
    openid = post_data.get('openid', '')
    if not openid:
        return HttpResponseForbidden('no openid')
    text = post_data.get('danmu', '')
    if not text:
        return HttpResponseForbidden('no text')

    danmu = Danmu()
    try:
        danmu.sender = Participant.objects.get(openid=openid)
    except Participant.DoesNotExist:
        return HttpResponseForbidden('user not exist')
    try:
        channel_name = Activity.objects.get(id=danmu.sender.activate_in).channel_name
    except Activity.DoesNotExist:
        return HttpResponse('{"result": "fail", "reason": "Activity does not exist"}')

    channel_layer = get_channel_layer()

    post_data['uid'] = post_data['openid']
    del post_data['openid']
    async_to_sync(channel_layer.group_send)(
        'test_group',
        {
            'type': 'chat_message',
            'text': json.dumps(
            {'action': 'send-danmu', 'content': post_data})
        }
    )

    danmu.text = text
    danmu.time = datetime.datetime.now()
    try:
        danmu.activity = Activity.objects.get(id=4)
    except Activity.DoesNotExist:
        HttpResponseForbidden('activity not exist')
    danmu.save()
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


@csrf_exempt
def login(request):
    """
    用于小程序的“登陆”功能，获得用户openid和session_key
    """
    if request.method != 'POST':
        return HttpResponseForbidden("Forbidden")
    post_data = json.loads(request.body.decode('utf-8'))
    code = post_data.get('code', '')
    if not code:
        return HttpResponseForbidden("No code")
    response = requests.get('https://api.weixin.qq.com/sns/jscode2session?'
                            'appid={}&secret={}&js_code={}&grant_type=authorization_code'
                            .format(xcx_appid, xcx_appsecret, code))
    decode = json.loads(response.content.decode())
    openid = decode.get('openid', '')

    if not openid:
        return HttpResponseForbidden("No openid")

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
    xcx_user.activate_in = 4  # TODO: 读取二维码
    xcx_user.save()
    decode['result'] = 'ok'
    post_data['uid'] = openid
    post_data['avatar'] = post_data['avatarUrl']
    post_data['nickname'] = post_data['nickName']
    del post_data['avatarUrl']
    del post_data['code']
    del post_data['nickName']

    a = Activity.objects.get(id=4)
    a.participants.add(xcx_user)
    a.save()

    channel_layer = get_channel_layer()
    channel_name = Activity.objects.get(id=xcx_user.activate_in).channel_name
    # async_to_sync(channel_layer.send)(
    #     channel_name, {'type': 'chat.message', 'text': json.dumps(
    #         {'action': 'append-user', 'content': post_data})})

    async_to_sync(channel_layer.group_send)(
        'test_group',
        {
            'type': 'chat_message',
            'text': json.dumps(
                {'action': 'append-user', 'content': post_data})
        }
    )

    return HttpResponse(json.dumps(decode))


@csrf_exempt
def join(request):
    if request.method != 'POST':
        return HttpResponseForbidden("Forbidden")
    return HttpResponse('{"result": "ok"}')
