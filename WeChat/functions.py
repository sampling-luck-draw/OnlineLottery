import hashlib
import json
import time

import requests
import untangle as untangle
from django.http import HttpResponse
from Lottery.secret import wechat_token, wechat_appid, wechat_appsecret


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
        l = [wechat_token, nonce, timestamp]
        l.sort()
        s = ''.join(l)
        s = hashlib.sha1(s.encode('utf-8')).hexdigest()
        if s == signature:
            return True
    return False


def reply(request):
    data = request.body.decode()
    msg = untangle.parse(data).xml
    id = msg.MsgId.cdata

    response = '<xml> ' \
               '<ToUserName><![CDATA[%s]]></ToUserName> ' \
               '<FromUserName><![CDATA[%s]]></FromUserName> ' \
               '<CreateTime>%d</CreateTime> ' \
               '<MsgType>text</MsgType> <Content>' \
               '<![CDATA[%s]]></Content>' \
               '</xml> ' % (msg.FromUserName.cdata, msg.ToUserName.cdata, time.time(), msg.FromUserName.cdata)
    return response


def handle_wechat(request):
    if request.method == 'GET':
        if checksignature(request):
            return HttpResponse(request.GET.get('echostr'))
        else:
            return HttpResponse('Fail')
    elif request.method == 'POST':
        return HttpResponse(reply(request))





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
