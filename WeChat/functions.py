import hashlib
import json
import time

import requests
from django.http import HttpResponse
from Lottery.secret import wechat_token, wechat_appid, wechat_appsecret


def checksignature(request):
    if request.method == 'GET':
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        echostr = request.GET.get('echostr', 'success')
        nonce = request.GET.get('nonce')
    elif request.method == 'POST':
        signature = request.POST.get('signature')
        timestamp = request.POST.get('timestamp')
        echostr = 'success'
        nonce = request.POST.get('nonce')
    else:
        return False

    if signature and timestamp and echostr:
        l = [wechat_token, nonce, timestamp]
        l.sort()
        s = ''.join(l)
        s = hashlib.sha1(s.encode('utf-8')).hexdigest()
        if s == signature:
            return True
    return False


def handle_wechat(request):
    if request.method == 'GET':
        if checksignature(request):
            return HttpResponse(request.GET.get('nonce'))
        else:
            return HttpResponse('Fail')





wx_token_expire_time = 0
wx_token = ''


def get_token(request):
    if request.method != 'GET':
        return HttpResponse('Hello')
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(
        wechat_appid, wechat_appsecret)
    global wx_token_expire_time, wx_token
    if wx_token_expire_time - time.time() <= 0:
        r = requests.get(url).content.decode()
        o = json.loads(r)
        if 'access_token' in o:
            wx_token_expire_time = time.time() + o['expires_in']
            wx_token = o['access_token']
        else:
            return HttpResponse(r)  # 返回错误代码
    return HttpResponse(wx_token)
