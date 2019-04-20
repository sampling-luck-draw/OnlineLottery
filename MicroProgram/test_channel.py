import json

import pytest
import requests
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User

import MicroProgram.consumers
from django.test import Client, TestCase

from MicroProgram import models
from aiounittest import async_test, AsyncTestCase

from Pages.utils import id_to_invite_code


class TestChannel(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        user = User.objects.create_user(username="aa", password="aa", email="aa@aa.com")
        organizer = models.Organizer.objects.create(user=user)
        models.Activity.objects.create(id=1, name='才明洋', belong=organizer)

    def setUp(self):
        self.client = Client()
        self.client.login(username="aa", password="aa")
        self.headers = [(b'origin', b'...'),
                        (b'cookie', self.client.cookies.output(header='', sep='; ').encode())]

    @async_test
    async def test_append_user(self):
        communicator = WebsocketCommunicator(MicroProgram.consumers.Console, "/ws?activity_id=1", self.headers)
        connected, subprotocol = await communicator.connect()
        self.assertEqual(connected, True)
        message = await communicator.receive_from(10)
        self.assertEqual(message, 'BLXDNZ')
        await communicator.send_json_to(
            {"action": "append-user",
             "content": {
                 "avatar": "头像地址",
                 "nickname": "Yeah...TT",
                 "language": "zh_CN",
                 "country": "China",
                 "province": "Jilin",
                 "gender": 1,
                 "uid": "oxwbU5M0-CCKSRFknXXXXXXXXXXX",
                 "city": "Yanbian"
             }
             })
        message = await communicator.receive_from(10)
        self.assertEqual(message, '{"result": "success"}')
        await communicator.send_json_to({"action": "get-participants"})
        message = await communicator.receive_json_from(10)
        self.assertEqual(json.dumps(message, sort_keys=True),
                         json.dumps({"action": "participants",
                                     "content": [
                                         {
                                             "avatar": "头像地址",
                                             "nickname": "Yeah...TT",
                                             "language": "zh_CN",
                                             "country": "China",
                                             "province": "Jilin",
                                             "gender": 1,
                                             "uid": "oxwbU5M0-CCKSRFknXXXXXXXXXXX",
                                             "city": "Yanbian",
                                             "activate_in": 1
                                         }
                                     ]}, sort_keys=True))
        await communicator.disconnect()

    @async_test
    async def test_modify_activity(self):
        communicator = WebsocketCommunicator(MicroProgram.consumers.Console, "/ws?activity_id=1", self.headers)
        connected, subprotocol = await communicator.connect()
        self.assertEqual(connected, True)
        message = await communicator.receive_from(10)
        self.assertEqual(message, 'BLXDNZ')
        await communicator.send_json_to({"action": "modify-activity", "content": {"start_time": "2019-07-01 13:05:40"}})
        message = await communicator.receive_from(10)
        self.assertEqual(message, '{"result": "success"}')
        await communicator.send_json_to({"action": "get-activity-info"})
        message = await communicator.receive_json_from(10)
        self.assertEqual(json.dumps(message, sort_keys=True),
                         json.dumps({"action": "activity-info",
                                     "content": {
                                         "name": "才明洋",
                                         "start_time": "2019-07-01 13:05:40",
                                         "end_time": "未结束",
                                         "invite_code": id_to_invite_code(1)
                                     }}, sort_keys=True))
        await communicator.disconnect()
