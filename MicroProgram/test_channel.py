import json

from aiounittest import async_test, AsyncTestCase
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User
from django.test import Client

import MicroProgram.consumers
from MicroProgram import models
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
    async def test_connect(self):
        communicator = WebsocketCommunicator(MicroProgram.consumers.Console, "/ws?activity_id=1", self.headers)
        connected, subprotocol = await communicator.connect()
        self.assertEqual(connected, True)
        message = await communicator.receive_from(10)
        self.assertEqual(message, 'BLXDNZ')
        await communicator.disconnect()

        communicator = WebsocketCommunicator(MicroProgram.consumers.Console, "/ws?activity_id=1")
        connected, subprotocol = await communicator.connect()
        self.assertEqual(connected, True)
        message = await communicator.receive_from(10)
        self.assertEqual(message, '{"error":"unauthenticated"}')
        await communicator.disconnect()

        communicator = WebsocketCommunicator(MicroProgram.consumers.Console, "/ws?activity_id=1", headers="123")
        connected, subprotocol = await communicator.connect()
        self.assertEqual(connected, True)
        message = await communicator.receive_from(10)
        self.assertEqual(message, '{"error":"unauthenticated"}')
        await communicator.disconnect()

        communicator = WebsocketCommunicator(MicroProgram.consumers.Console, "/ws", self.headers)
        connected, subprotocol = await communicator.connect()
        self.assertEqual(connected, True)
        message = await communicator.receive_from(10)
        self.assertEqual(message, 'BLXDNZ')
        await communicator.disconnect()

        communicator = WebsocketCommunicator(MicroProgram.consumers.Console, "/ws?activity_id=2", self.headers)
        connected, subprotocol = await communicator.connect()
        self.assertEqual(connected, True)
        message = await communicator.receive_from(10)
        self.assertEqual(message, '{"error":"invalid activity id"}')
        await communicator.disconnect()

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

    @async_test
    async def test_award(self):
        communicator = WebsocketCommunicator(MicroProgram.consumers.Console, "/ws?activity_id=1", self.headers)
        connected, subprotocol = await communicator.connect()
        self.assertEqual(connected, True)
        message = await communicator.receive_from(10)
        self.assertEqual(message, 'BLXDNZ')

        await communicator.send_json_to({"action": "append-award",
                                         "content": {
                                             "name": "一等奖",
                                             "prize": "兰博基尼五元优惠券",
                                             "amount": 10
                                         }})
        message = await communicator.receive_from(10)
        self.assertEqual(message, '{"result": "success"}')
        await communicator.send_json_to({"action": "get-awards"})
        message = await communicator.receive_json_from(10)
        self.assertEqual(json.dumps(message, sort_keys=True),
                         json.dumps({"action": "awards", "content": [
                             {"id": 1, "award_name": "一等奖", "prize_name": "兰博基尼五元优惠券", "amount": 10,
                              "activity_id": 1}]}, sort_keys=True))
        await communicator.send_json_to({"action": "append-award",
                                         "content": {
                                             "name": "二等奖",
                                             "prize": "才明洋陪你玩",
                                             "amount": 1
                                         }})
        message = await communicator.receive_from(10)
        self.assertEqual(message, '{"result": "success"}')
        await communicator.send_json_to({"action": "get-awards"})
        message = await communicator.receive_json_from(10)
        self.assertEqual(json.dumps(message, sort_keys=True),
                         json.dumps({"action": "awards", "content": [
                             {"id": 1, "award_name": "一等奖", "prize_name": "兰博基尼五元优惠券", "amount": 10, "activity_id": 1},
                             {"id": 2, "award_name": "二等奖", "prize_name": "才明洋陪你玩", "amount": 1, "activity_id": 1
                              }]}, sort_keys=True))
        await communicator.send_json_to({"action": "delete-award", "content": {"name": "一等奖"}})
        message = await communicator.receive_from(10)
        self.assertEqual(message, '{"result": "success"}')
        await communicator.send_json_to({"action": "get-awards"})
        message = await communicator.receive_json_from(10)
        self.assertEqual(json.dumps(message, sort_keys=True),
                         json.dumps({"action": "awards", "content": [
                             {"id": 2, "award_name": "二等奖", "prize_name": "才明洋陪你玩", "amount": 1, "activity_id": 1
                              }]}, sort_keys=True))

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
        await communicator.send_json_to({"action": "lucky-dog", "content":
            {"uid": "oxwbU5M0-CCKSRFknXXXXXXXXXXX", "award": "二等奖"}})
        message = await communicator.receive_from(10)
        self.assertEqual(message, '{"result": "success"}')
        await communicator.send_json_to({"action": "get-lucky-dogs"})
        message = await communicator.receive_json_from(10)
        self.assertEqual(json.dumps(message, sort_keys=True),
                         json.dumps({"action": "lucky-dogs", "content": [
                             ["二等奖", "oxwbU5M0-CCKSRFknXXXXXXXXXXX"]
                         ]}, sort_keys=True))
        await communicator.send_json_to({"action": "lucky-dog", "content":
            {"uid": "oxwbU5MXXXXX", "award": "二等奖"}})
        message = await communicator.receive_from(10)
        self.assertEqual(message, '{"error": "no such user"}')
        await communicator.send_json_to({"action": "lucky-dog", "content":
            {"uid": "oxwbU5M0-CCKSRFknXXXXXXXXXXX", "award": "一等奖"}})
        message = await communicator.receive_from(10)
        self.assertEqual(message, '{"error": "no such award"}')
        await communicator.disconnect()
