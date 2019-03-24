from django.urls import path
from .functions import handle_wechat, get_token


urlpatterns = [
    path('', handle_wechat),
    path('gettoken', get_token)
]