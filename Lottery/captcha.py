from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from .secret import pc_geetest_id, pc_geetest_key
from geetest import GeetestLib


def pc_getcaptcha(request):
    """极验验证函数"""
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)


def pc_validate(request):
    if request.method != 'POST':
        return False
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    challenge = request.POST.get(gt.FN_CHALLENGE, "")
    validate = request.POST.get(gt.FN_VALIDATE, "")
    seccode = request.POST.get(gt.FN_SECCODE, "")
    status = request.session[gt.GT_STATUS_SESSION_KEY]
    if status == 1:
        result = gt.success_validate(challenge, validate, seccode)
    else:
        result = gt.failback_validate(challenge, validate, seccode)
    return result