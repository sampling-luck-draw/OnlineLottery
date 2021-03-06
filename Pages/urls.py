
from django.urls import path, include

import Pages.auth, Pages.views, Pages.function

urlpatterns = [
    path('', Pages.views.index),
    path('signup', Pages.auth.signup),
    path('signin', Pages.auth.signin),
    path('logout', Pages.auth.logout),
    path('changepsw', Pages.auth.changePsw),
    path('usercenter', Pages.views.usercenter),
    path('usercenter/danmu', Pages.views.danmu_manage),
    path('usercenter/participant', Pages.views.participant_manage),
    path('usercenter/activity', Pages.views.activity_manage),

    path('testws', Pages.views.test_ws),
    path('get-csrf', Pages.views.get_csrf),

    path('get-participants', Pages.function.get_participants),
    path('get-activities', Pages.function.get_activities),
    # path('get-participants/<int:activity_id>)', Pages.views.get_participants),
    path('get-danmu', Pages.function.get_danmu),
    path('append-activity', Pages.function.append_activity),
]