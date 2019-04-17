import time

import untangle
from MicroProgram import models
from MicroProgram.functions import send_danmu
from Pages.utils import invite_code_to_id
from WeChat.session import MySession
import WeChat.session as SC
from WeChat import text


def register(openid):
    participant = models.Participant(openid=openid)
    participant.save()
    MySession().set(openid, SC.SET_NICKNAME)
    return text.welcome


def check_function(content, openid, participant):
    if content == '帮助':
        return "TODO: 帮助文档"
    if content == '修改昵称':
        MySession().set(openid, SC.SET_NICKNAME)
        return text.set_nickname_hint
    if content == '退出活动':
        participant.activate_in = None
        participant.save()
        return text.quit_success

    activity = None
    if participant.activate_in:
        activity = models.Activity.objects.get(id=participant.activate_in)
        if activity.status == 'Finished':
            participant.activate_in = None
            participant.save()
            activity = None

    if len(content) == 5 and content.isalpha():
        # 可能是邀请码
        if activity is None:
            # 未加入有效活动
            activity_id = invite_code_to_id(content.upper())
            print('invite code {} activity id {}'.format(content, activity_id))
            try:
                activity = models.Activity.objects.get(id=activity_id)
            except models.Activity.DoesNotExist:
                return text.wrong_invite_code
            if activity.status == 'Finished':
                return text.activity_finished
            activity.participants.add(participant)
            activity.save()
            participant.activate_in = activity_id
            participant.save()
            return text.join_success.format(activity.name)
        else:
            # 已有活动
            if not MySession().get(openid + '_reminded'):
                MySession().set(openid + '_reminded', 1, 7200)
                send_danmu(participant, content)
                return text.already_in.format(activity.name)

    if activity is None:
        return text.activity_finished
    send_danmu(participant, content)
    return ""


def check_session(content, openid, participant):
    sess = MySession().get(openid)
    if sess is None:
        return check_function(content, openid, participant)
    elif sess == SC.SET_NICKNAME:
        participant.nickName = content
        participant.save()
        MySession().remove(openid)
        return text.set_nickname_success.format(content)
    return check_function(content, openid, participant)


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

    rep_text = process(content, openid)
    if rep_text == '':
        response = "success"
    else:
        response = \
            '<xml> ' \
            '<ToUserName><![CDATA[%s]]></ToUserName> ' \
            '<FromUserName><![CDATA[%s]]></FromUserName> ' \
            '<CreateTime>%d</CreateTime> ' \
            '<MsgType>text</MsgType>' \
            '<Content><![CDATA[%s]]></Content>' \
            '</xml> ' % (msg.FromUserName.cdata, msg.ToUserName.cdata, time.time(), rep_text)
    return response
