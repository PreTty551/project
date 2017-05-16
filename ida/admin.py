from django.contrib import admin

from ida.models import Duty
from user.models import User


class DutyAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'nickname', 'group', 'memo')

    def nickname(self, obj):
        u = User.get(obj.user_id)
        return u.nickname
    nickname.short_description = u'昵称'

admin.site.register(Duty, DutyAdmin)
