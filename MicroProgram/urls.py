from django.urls import path
from .xcx import *

urlpatterns = [
    path('sanddanmu', xcx_send_danmu),
    path('gettoken', get_token_http),
    path('login', login),
    path('join', join),
    path('get-qr', get_wxa_code)
]