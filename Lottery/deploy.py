import hmac
import os
from hashlib import sha1
from .secret import github_webhook_secret

from django.utils.encoding import force_bytes
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseForbidden, HttpResponseServerError, HttpResponse


@csrf_exempt
def deploy(request):
    if request.method != 'POST' or not request.body:
        return HttpResponseForbidden("Permission denied. 1")

    header_signature = request.META.get('HTTP_X_HUB_SIGNATURE')
    if header_signature is None:
        return HttpResponseForbidden('Permission denied. 2')

    splited = header_signature.split('=')
    if len(splited) == 1:
        return HttpResponseForbidden('Permission denied. 4')
    sha_name, signature = splited
    if sha_name != 'sha1':
        return HttpResponseServerError('Operation not supported.', status=501)

    mac = hmac.new(force_bytes(github_webhook_secret), msg=force_bytes(request.body), digestmod=sha1)
    if not hmac.compare_digest(force_bytes(mac.hexdigest()), force_bytes(signature)):
        return HttpResponseForbidden('Permission denied. 3')

    event_type = request.META.get('HTTP_X_GITHUB_EVENT')
    if event_type == 'ping':
        return HttpResponse('pong!')
    if event_type == 'push':
        os.system('cd /web-server/OnlineLottery/ && bash deploy.sh')
        return HttpResponse('deploy.')

    return HttpResponseServerError('Operation not supported.', status=502)

