from django.contrib import admin

from ida.models import Duty, WageUser
from user.models import User


class DutyAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'nickname', 'group', 'memo')

    def nickname(self, obj):
        u = User.get(obj.user_id)
        return u.nickname
    nickname.short_description = u'昵称'


class WageUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'date')


admin.site.register(Duty, DutyAdmin)
admin.site.register(WageUser, WageUserAdmin)
