import time

import untangle
from MicroProgram import models
from Pages.utils import invite_code_to_id
from WeChat.session import MySession, SET_NICKNAME, SET_AVATAR
from WeChat import text


def register(openid):
    participant = models.Participant(openid=openid)
    participant.save()
    MySession().set(openid, SET_NICKNAME)
    return text.welcome


def check_function(content, openid, participant):
    if content == '帮助':
        return "TODO: 帮助文档"
    if content == '修改昵称':
        MySession().set(openid, SET_NICKNAME)
        return text.set_nickname_hint
    if content == '退出活动':
        participant.activate_in = None
        participant.save()
        return text.quit_success

    # 弹幕或加入
    if participant.activate_in is None or participant.activate_in.status == 'Finished':
        if len(content) == 5 and content.isalpha():
            # 可能是加入邀请码
            activity_id = invite_code_to_id(content.upper())
        participant.activate_in = None
        participant.save()
        return text.activity_finished
    return "弹幕"


def check_session(content, openid, participant):
    sess = MySession().get(openid)
    if sess is None:
        return check_function(content, openid, participant)
    elif sess == SET_NICKNAME:
        participant.nickName = content
        participant.save()
        MySession().remove(openid)
        return text.set_nickname_success.format(content)


def process(content, openid):
    try:
        participant = models.Participant.objects.get(openid=openid)
    except models.Participant.DoesNotExist:
        return register(openid)

    return check_session(content, openid, participant)


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