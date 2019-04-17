import time

import untangle
from MicroProgram import models
from WeChat.session import MySession, SET_NICKNAME, SET_AVATAR
from WeChat import text


def register(openid):
    participant = models.Participant(openid=openid)
    participant.save()
    MySession().set(openid, SET_NICKNAME)
    return text.welcome


def process(content, openid):
    try:
        participant = models.Participant.objects.get(openid=openid)
    except models.Participant.DoesNotExist:
        return register(openid)

    sess = MySession().get(openid)
    if sess is None:
        # 弹幕和加入
        return "暂时不能加入和发弹幕"
    elif sess == SET_NICKNAME:
        participant.nickName = content
        participant.save()
        MySession().remove(openid)
        return text.set_nickname_success.format(content)


def reply(request):
    data = request.body.decode()
    msg = untangle.parse(data).xml
    msgid = msg.MsgId.cdata
    content = msg.Content.cdata
    openid = msg.FromUserName.cdata

    response = '<xml> ' \
               '<ToUserName><![CDATA[%s]]></ToUserName> ' \
               '<FromUserName><![CDATA[%s]]></FromUserName> ' \
               '<CreateTime>%d</CreateTime> ' \
               '<MsgType>text</MsgType>'\
               '<Content><![CDATA[%s]]></Content>' \
               '</xml> ' % (msg.FromUserName.cdata, msg.ToUserName.cdata, time.time(), process(content, openid))
    return response