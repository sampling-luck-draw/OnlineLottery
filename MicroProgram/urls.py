from django.urls import path
from .functions import *

urlpatterns = [
    path('sanddanmu', send_danmu),
    path('gettoken', get_token_http),
    path('login', login),
    path('join', join),
    path('get-qr', get_wxa_code)
]