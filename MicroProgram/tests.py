import json

from django.contrib.auth.models import User
from django.test import TestCase

import MicroProgram.models as models
from django.test import Client


class MicroProgramTestCase(TestCase):
    def setUp(self):
        d = {
            "nickName": "才小羊",
            "avatarUrl": "avatarUrl",
            "gender": 0,
            "country": "Solar System",
            "province": "Alpha Centauri",
            "city": "Proxima Centauri",
            "language": "Xenolinguistics",
            "openid": "123"
        }
        models.Participant.objects.create(**d)
        user = User.objects.create_user(username="aa", password="aa", email="aa@aa.com")
        organizer = models.Organizer.objects.create(user=user)
        models.Activity.objects.create(id=1, name="act", belong=organizer)

    def test_join(self):
        client = Client()
        response = client.post('/xcx/join')
        self.assertEqual(response.content, b'{"result": "json decode error"}')
        response = client.post('/xcx/join', data={"uid": "123"}, content_type='application/json')
        self.assertEqual(response.content, b'{"result": "no open id or activity"}')
        response = client.post('/xcx/join', data={"openid": "1243", "activity_id": 1}, content_type='application/json')
        self.assertEqual(response.content, b'{"result": "no such user"}')
        response = client.post('/xcx/join', data={"openid": "123", "activity_id": 2}, content_type='application/json')
        self.assertEqual(response.content, b'{"result": "no such activity"}')
        response = client.post('/xcx/join', data={"openid": "123", "activity_id": 1}, content_type='application/json')
        self.assertEqual(response.content.decode('utf-8'),
                         json.dumps({"result": "ok",
                                     "activity_name": models.Activity.objects.get(id=1).name,
                                     "activity_status": models.Activity.objects.get(id=1).status
                                     }))
        self.assertEqual(models.Activity.objects.get(id=1).participants.count(), 1)
        self.assertEqual(models.Participant.objects.get(openid="123").activate_in, 1)
