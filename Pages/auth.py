import json

from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import auth
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

# from Lottery.captcha import pc_validate
from MicroProgram.models import Organizer

from . import views


@csrf_exempt
def signup(request):
    if request.method == "GET":
        return views.signup(request)
    if request.method != "POST":
        return HttpResponseForbidden()
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseForbidden("Json decode error")
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    if not username:
        return JsonResponse({"result": "error", "msg": "no username"})
    if not password:
        return JsonResponse({"result": "error", "msg": "no password"})
    if not email:
        return JsonResponse({"result": "error", "msg": "no email"})
    # if False and not pc_validate(request):
    #     return JsonResponse({"result": "error", "msg": "验证码错误"})
    query = User.objects.filter(username=username)
    if len(query) > 0:
        return JsonResponse({"result": "error", "msg": "该用户已经存在"})
    user = User.objects.create_user(username=username, password=password, email=email)
    organizer = Organizer()
    organizer.user = user
    organizer.save()
    auth.login(request, user)
    return JsonResponse({"result": "success", "uid": user.id})


@csrf_exempt
def signin(request):
    if request.method == "GET":
        return views.signin(request)
    if request.method != "POST":
        return HttpResponseForbidden()
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.decoder.JSONDecodeError:
        return HttpResponseForbidden("json decode error")

    username = data.get("username")
    password = data.get("password")
    if not username:
        return JsonResponse({"result": "error", "msg": "no username"})
    if not password:
        return JsonResponse({"result": "error", "msg": "no password"})
    # if False and not pc_validate(request):
    #     return JsonResponse({"result": "error", "msg": "验证码错误"})

    user = auth.authenticate(username=username, password=password)
    if user is None:
        return JsonResponse({"result": "error", "msg": "用户名或密码错误"})
    auth.login(request, user)
    return JsonResponse({"result": "success", "uid": user.id})


def logout(request):
    if request.method != "POST":
        return HttpResponseForbidden()
    auth.logout(request)
    return JsonResponse({"result": "success"})

@csrf_exempt
def changePsw(request):
    if request.method != "POST":
        return HttpResponseForbidden()
    data = json.loads(request.body.decode("utf-8"))
    old_psw = data.get("old_psw")
    new_psw = data.get("new_psw")
    if not old_psw:
        return JsonResponse({"result": "error", "msg": "no old password"})
    if not new_psw:
        return JsonResponse({"result": "error", "msg": "no new password"})
    # if False and not pc_validate(request):
    #     return JsonResponse({"result": "error", "msg": "验证码错误"})

    user = request.user
    if not user.check_password(old_psw):
        return JsonResponse({"result": "error", "msg": "旧密码错误"})
    user.set_password(new_psw)
    user.save()
    return JsonResponse({"result": "success"})
