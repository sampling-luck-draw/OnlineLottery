import json

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
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

    def change_password(self):
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