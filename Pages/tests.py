import datetime
import json

from django.test import TestCase, Client

from MicroProgram import models


class TestPage(TestCase):
    def test_auth_signup(self):
        client = Client()
        r = client.post('/signup', {'username': '123', 'password': '123', 'email': '123@123.com'},
                        content_type='application/json')
        self.assertEqual(r.content.decode(),
                         '{"result": "success", "uid": %d}' % models.User.objects.get(username='123').id)
        r = client.post('/signup', {'username': '123', 'password': '123', 'email': '123@123.com'},
                        content_type='application/json')
        self.assertEqual(r.content.decode(), json.dumps({"result": "error", "msg": "该用户已经存在"}))
        r = client.post('/signup', {'username1': '123', 'password': '123', 'email': '123@123.com'},
                        content_type='application/json')
        self.assertEqual(r.content.decode(), '{"result": "error", "msg": "no username"}')
        r = client.post('/signup', {'username': '123', 'password1': '123', 'email': '123@123.com'},
                        content_type='application/json')
        self.assertEqual(r.content.decode(), '{"result": "error", "msg": "no password"}')
        r = client.post('/signup', {'username': '123', 'password': '123', 'email1': '123@123.com'},
                        content_type='application/json')
        self.assertEqual(r.content.decode(), '{"result": "error", "msg": "no email"}')

    def test_signin(self):
        client = Client()
        client.post('/signup', {'username': '123', 'password': '123', 'email': '123@123.com'},
                    content_type='application/json')
        r = client.post('/signin', {'username': '123', 'password': '123'}, content_type='application/json')
        self.assertEqual(r.content.decode(),
                         '{"result": "success", "uid": %d}' % models.User.objects.get(username='123').id)
        r = client.post('/signin', {'username1': '123', 'password': '123'}, content_type='application/json')
        self.assertEqual(r.content.decode(), json.dumps({"result": "error", "msg": "no username"}))
        r = client.post('/signin', {'username': '123', 'password1': '123'}, content_type='application/json')
        self.assertEqual(r.content.decode(), json.dumps({"result": "error", "msg": "no password"}))
        r = client.post('/signin', {'username': '123', 'password': '435'}, content_type='application/json')
        self.assertEqual(r.content.decode(), json.dumps({"result": "error", "msg": "用户名或密码错误"}))

    def test_logout(self):
        client = Client()
        r = client.post('/logout')
        self.assertEqual(r.content.decode(), '{"result": "success"}')

    def test_change_password(self):
        client = Client()
        client.post('/signup', {'username': '123', 'password': '123', 'email': '123@123.com'},
                    content_type='application/json')
        r = client.post('/changepsw', {'old_psw1': '123', 'new_psw': '456'}, content_type='application/json')
        self.assertEqual(r.content.decode(), json.dumps({"result": "error", "msg": "no old password"}))
        r = client.post('/changepsw', {'old_psw': '123', 'new_psw1': '456'}, content_type='application/json')
        self.assertEqual(r.content.decode(), json.dumps({"result": "error", "msg": "no new password"}))
        r = client.post('/changepsw', {'old_psw': '456', 'new_psw': '456'}, content_type='application/json')
        self.assertEqual(r.content.decode(), json.dumps({"result": "error", "msg": "旧密码错误"}))
        r = client.post('/changepsw', {'old_psw': '123', 'new_psw': '456'}, content_type='application/json')
        self.assertEqual(r.content.decode(), json.dumps({"result": "success"}))
        r = client.post('/signin', {'username': '123', 'password': '456'}, content_type='application/json')
        self.assertEqual(r.content.decode(),
                         '{"result": "success", "uid": %d}' % models.User.objects.get(username='123').id)


class TestFunc(TestCase):
    def setUp(self):
        client = Client()
        client.post('/signup', {'username': '123', 'password': '123', 'email': '123@123.com'},
                    content_type='application/json')
        self.client = client
        user = models.User.objects.get(username='123')
        organizer = models.Organizer.objects.get(user=user)
        self.act = models.Activity.objects.create(name='act111', belong=organizer)
        participant = models.Participant.objects.create(nickname='ccc', openid="444")
        self.act.participants.add(participant)
        self.act.save()
        models.Danmu.objects.create(sender=participant, activity=self.act, text='danmu1',
                                    time=datetime.datetime.now(datetime.timezone.utc))
        models.Danmu.objects.create(sender=participant, activity=self.act, text='danmu2',
                                    time=datetime.datetime.now(datetime.timezone.utc))

    def test_get_danmu(self):
        client = self.client
        r = client.get('/get-danmu', data={'activity': 1})
        danmus = models.Danmu.objects.all()
        expect = json.dumps({
            'draw': 0,
            'recordsTotal': 2,
            'recordsFiltered': 2,
            'data': [{
                'id': danmus[1].id,
                'openid': '444',
                'nickName': 'ccc',
                'text': 'danmu2',
                'time': danmus[1].time.strftime("%Y-%m-%d %H:%M:%S")
            }, {
                'id': danmus[0].id,
                'openid': '444',
                'nickName': 'ccc',
                'text': 'danmu1',
                'time': danmus[0].time.strftime("%Y-%m-%d %H:%M:%S")
            }]
        })
        self.assertEqual(r.content.decode(), expect)

    def test_get_participant(self):
        client = self.client
        r = client.get('/get-participants', data={'activity': 1})
        i = models.Participant.objects.get(openid="444")
        expect = json.dumps([{
            'id': i.pk,
            'nickname': i.nickname,
            'avatar': i.avatar,
            'gender': i.gender,
            'country': i.country,
            'province': i.province,
            'city': i.city,
            'language': i.language
        }])
        self.assertEqual(r.content.decode(), expect)
