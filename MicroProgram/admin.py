from django.contrib import admin

from MicroProgram.models import *


class OrganizerAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


class ParticipantAdmin(admin.ModelAdmin):
    readonly_fields = ('openid',)


class ActivityAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


class DanmuAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


class AwardAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


admin.site.register(Organizer, OrganizerAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Danmu, DanmuAdmin)
admin.site.register(Award, AwardAdmin)
