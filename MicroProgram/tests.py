from django.test import TestCase
import MicroProgram.models as models


class MicroProgramTestCase(TestCase):
    def setUp(self):
        d = {
            "nickName": "Anonymous",
            "avatarUrl": "avatarUrl",
            "gender": 0,
            "country": "Solar System",
            "province": "Alpha Centauri",
            "city": "Proxima Centauri",
            "language": "Xenolinguistics",
            "openid": "123"
        }
        models.Participant.objects.create(**d)

    def test_join(self):
        p = models.Participant.objects.get(openid="123")
        self.assertEqual(p.nickName, "Anonymous")

