from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url

from MicroProgram import consumers

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([
            url(r'^ws/(?P<activity_id>[^/]+)$', consumers.Console),
            url(r'^ws$', consumers.Console),
        ])
    ),
})
