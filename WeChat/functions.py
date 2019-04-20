import hashlib
import json
import time

import requests
import WeChat.reply
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from Lottery.secret import wechat_token_cmy, wechat_appid_cmy, wechat_appsecret_cmy


def checksignature(request):
    if request.method == 'GET':
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
    elif request.method == 'POST':
        signature = request.POST.get('signature')
        timestamp = request.POST.get('timestamp')
        nonce = request.POST.get('nonce')
    else:
        return False

    if signature and timestamp and nonce:
        l = [wechat_token_cmy, nonce, timestamp]
        l.sort()
        s = ''.join(l)
        s = hashlib.sha1(s.encode('utf-8')).hexdigest()
        if s == signature:
            return True
    return False


@csrf_exempt
def handle_wechat(request):
    if request.method == 'GET':
        if checksignature(request):
            return HttpResponse(request.GET.get('echostr'))
        else:
            return HttpResponse('Fail')
    elif request.method == 'POST':
        return HttpResponse(WeChat.reply.reply(request))


wx_token_expire_time = 0
wx_token = ''


def get_token():
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(
        wechat_appid_cmy, wechat_appsecret_cmy)
    global wx_token_expire_time, wx_token
    if wx_token_expire_time - time.time() <= 0:
        r = requests.get(url).content.decode()
        o = json.loads(r)
        if 'access_token' in o:
            wx_token_expire_time = time.time() + o['expires_in']
            wx_token = o['access_token']
        else:
            return r  # 返回错误代码
    return wx_token


def get_token_http(request):
    if request.method != 'GET':
        return HttpResponse('Hello')
    return HttpResponse(get_token())
