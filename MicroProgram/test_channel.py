import pytest
import requests
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User

import MicroProgram.consumers
from django.test import Client, TestCase

from MicroProgram import models
from aiounittest import async_test, AsyncTestCase


class TestChannel(AsyncTestCase):
    def setUp(self):
        user = User.objects.create_user(username="aa", password="aa", email="aa@aa.com")
        organizer = models.Organizer.objects.create(user=user)
        models.Activity.objects.create(id=1, name='才明洋', belong=organizer)
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


# @pytest.mark.django_db
# def test_signin():
#     client = Client()
#     client.post('/signup', data={"username": "123", "password": "123"}, content_type="application/json")
#     response = client.post('/signin', data={"username": "123", "password": "123"}, content_type="application/json")
#     assert response.content.decode('utf-8') == '{"status": "ok", "uid": "123"}'
#     global headers
#     headers = [(b'origin', b'...'), (b'cookie', response.cookies.output(header='', sep='; ').encode())]
#
#
# @pytest.mark.asyncio
# async def test_connect():
#     communicator = WebsocketCommunicator(MicroProgram.consumers.Console, "/ws/1", headers)
#     connected, subprotocol = await communicator.connect()
#     assert connected
#     message = await communicator.receive_from()
#     assert message == 'BLXDN1Z'
#     await communicator.disconnect()
#
