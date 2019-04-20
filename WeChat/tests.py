import datetime
import time

import untangle
from django.contrib.auth.models import User
from django.test import TestCase, Client

from MicroProgram import models
from Pages.utils import id_to_invite_code

import WeChat.text as text

fake_participant_id = 'test_wechat_user_1'


def make_message(text):
    response = \
        '<xml> ' \
        '<MsgId>0</MsgId>'\
        '<ToUserName><![CDATA[axx]]></ToUserName> ' \
        '<FromUserName><![CDATA[%s]]></FromUserName> ' \
        '<CreateTime>%d</CreateTime> ' \
        '<MsgType>text</MsgType>' \
        '<Content><![CDATA[%s]]></Content>' \
        '</xml> ' % (fake_participant_id, time.time(), text)
    return response


def get_content(xml_text):
    msg = untangle.parse(xml_text).xml
    return msg.Content.cdata


class TestWeChat(TestCase):
    def setUp(self):
        user = User.objects.create_user(username="aa", password="aa", email="aa@aa.com")
        organizer = models.Organizer.objects.create(user=user)
        models.Activity.objects.create(id=1, name='才明洋', belong=organizer)

    def test_signature(self):
        client = Client()
        response = client.get('/wx/', data={'timestamp': '1553427315',
                                           'nonce': '1445909175',
                                           'signature': '1f521b1fcbe1d84242032d7a6ad260943ddb9e14',
                                           "echostr": "2103962420066615283"})
        self.assertEqual(response.content, b'2103962420066615283')
        response = client.get('/wx/', data={'timestamp': '1553427315X',
                                            'nonce': '1445909175X',
                                            'signature': '1f521b1fcbe1d84242032d7a6ad260943ddb9e14X',
                                            "echostr": "2103962420066615283"})
        self.assertEqual(response.content, b'Fail')

    def test_get_token(self):
        client = Client()
        response = client.post('/wx/gettoken')
        self.assertEqual(response.content.decode(), 'Hello')
        response = client.get('/wx/gettoken')
        print(response.content)
        self.assertEqual(response.status_code, 200)

    def test_help(self):
        client = Client()
        client.post('/wx/', data=make_message('哈哈哈'), content_type='text/plain')
        client.post('/wx/', data=make_message('才124'), content_type='text/plain')
        response = client.post('/wx/', data=make_message('帮助'), content_type='text/plain')
        self.assertEqual(get_content(response.content.decode()), "TODO: 帮助文档")

    def test_unknown(self):
        client = Client()
        response = client.post('/wx/', data=make_message('【收到不支持的消息类型，暂无法显示】'), content_type='text/plain')
        self.assertEqual(get_content(response.content.decode()), '【收到不支持的消息类型，暂无法显示】')

    def test_join_and_quit(self):
        client = Client()
        client.post('/wx/', data=make_message('哈哈哈'), content_type='text/plain')
        client.post('/wx/', data=make_message('才124'), content_type='text/plain')
        client.post('/wx/', data=make_message(id_to_invite_code(1)), content_type='text/plain')
        participant = models.Participant.objects.get(openid=fake_participant_id)
        self.assertEqual(participant.activate_in, 1)
        self.assertTrue(participant in models.Activity.objects.get(id=1).participants.all())

        client.post('/wx/', data=make_message('退出活动'), content_type='text/plain')
        participant = models.Participant.objects.get(openid=fake_participant_id)
        self.assertEqual(participant.activate_in, None)

    def test_change_name(self):
        client = Client()
        client.post('/wx/', data=make_message('哈哈哈'), content_type='text/plain')
        client.post('/wx/', data=make_message('才124'), content_type='text/plain')
        client.post('/wx/', data=make_message('修改昵称'), content_type='text/plain')
        client.post('/wx/', data=make_message('才456'), content_type='text/plain')
        participant = models.Participant.objects.get(openid=fake_participant_id)
        self.assertEqual(participant.nickname, '才456')

    def test_invalid_invite_code(self):
        client = Client()
        client.post('/wx/', data=make_message('哈哈哈'), content_type='text/plain')
        client.post('/wx/', data=make_message('才124'), content_type='text/plain')
        # client.post('/wx/', data=make_message('退出活动'), content_type='text/plain')
        r = client.post('/wx/', data=make_message(id_to_invite_code(2)), content_type='text/plain')
        self.assertEqual(get_content(r.content.decode()), text.wrong_invite_code)
        r = client.post('/wx/', data=make_message(id_to_invite_code(1)), content_type='text/plain')
        r = client.post('/wx/', data=make_message(id_to_invite_code(2)), content_type='text/plain')
        self.assertEqual(get_content(r.content.decode()), text.already_in.format("才明洋"))

    def test_finish_activity(self):
        client = Client()
        client.post('/wx/', data=make_message('哈哈哈'), content_type='text/plain')
        client.post('/wx/', data=make_message('才124'), content_type='text/plain')
        client.post('/wx/', data=make_message(id_to_invite_code(1)), content_type='text/plain')
        activity = models.Activity.objects.get(id=1)
        activity.start_time = datetime.datetime.now() + datetime.timedelta(hours=-2)
        activity.end_time = datetime.datetime.now() + datetime.timedelta(hours=-1)
        activity.save()
        r = client.post('/wx/', data=make_message('弹幕'), content_type='text/plain')
        self.assertEqual(get_content(r.content.decode()), text.activity_finished)
        self.assertEqual(models.Participant.objects.get(openid=fake_participant_id).activate_in, None)
        r = client.post('/wx/', data=make_message(id_to_invite_code(1)), content_type='text/plain')
        self.assertEqual(get_content(r.content.decode()), text.activity_finished)

    def test_danmu(self):
        client = Client()
        client.post('/wx/', data=make_message('哈哈哈'), content_type='text/plain')
        client.post('/wx/', data=make_message('才124'), content_type='text/plain')
        client.post('/wx/', data=make_message(id_to_invite_code(1)), content_type='text/plain')
        r = client.post('/wx/', data=make_message('弹幕'), content_type='text/plain')
        self.assertEqual(r.content.decode(), 'success')
