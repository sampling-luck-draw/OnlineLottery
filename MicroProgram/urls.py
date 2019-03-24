from django.urls import path
from .functions import send_danmuku, get_token

urlpatterns = [
    path('sanddanmuku', send_danmuku),
    path('geettoken', get_token)
]