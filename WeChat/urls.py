from django.urls import path
from .functions import *


urlpatterns = [
    path('', handle_wechat),
    path('gettoken', get_token_http),
]