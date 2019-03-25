from django.urls import path
from .functions import *

urlpatterns = [
    path('sanddanmu', send_danmu),
    path('gettoken', get_token),
    path('login', micro_program_login)
]