import time
from io import BytesIO

import requests
import untangle
from django.core.files.images import ImageFile

import WeChat.functions
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
    if content == '修改头像':
        MySession().set(openid, SC.SET_AVATAR)
        return text.set_avatar_hint
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


def set_avatar(openid, media_id):
    if MySession().get(openid) != SC.SET_AVATAR:
        return text.send_img_hint
    try:
        participant = models.Participant.objects.get(openid=openid)
    except models.Participant.DoesNotExist:
        return ""
    url = 'https://api.weixin.qq.com/cgi-bin/media/get?access_token={}&media_id={}'.\
        format(WeChat.functions.get_token(), media_id)
    print('avatar_url')
    response = requests.get(url)
    avatar = ImageFile(BytesIO(response.content), name="avatar_file_" + openid)
    avatar.close()
    participant.avatarUrl = 'avatar/avatar_file_' + openid
    participant.save()

    return ''


def reply(request):
    data = request.body.decode()
    msg = untangle.parse(data).xml
    type = msg.MsgType.cdata
    msgid = msg.MsgId.cdata
    openid = msg.FromUserName.cdata

    rep_text = ''
    print(data)
    if type == 'text':
        content = msg.Content.cdata
        if content == '【收到不支持的消息类型，暂无法显示】':
            rep_text = '【收到不支持的消息类型，暂无法显示】'
        else:
            rep_text = process(content, openid)
    elif type == 'image':
        rep_text = set_avatar(openid, msg.MediaId.cdata)
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
