"""Lottery URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from Lottery import deploy, captcha
from Pages.views import index, test_ws, get_csrf, usercenter
import Pages.auth


urlpatterns = [
    path('', index),
    path('', include('gentelella.urls')),
    path('testws', test_ws),
    path('wx/', include('WeChat.urls')),
    path('xcx/', include('MicroProgram.urls')),

    path('get-csrf', get_csrf),
    path('signup', Pages.auth.signup),
    path('signin', Pages.auth.signin),
    path('logout', Pages.auth.logout),
    path('changepsw', Pages.auth.changePsw),
    path('usercenter', usercenter),

    path('pc-geetest/get', captcha.pc_getcaptcha),
    path('pc-geetest/validate', captcha.pc_validate),

    path('deploy', deploy.deploy),
    path('admin/', admin.site.urls),
]