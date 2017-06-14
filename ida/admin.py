from django.contrib import admin

from ida.models import Duty, WageUser
from user.models import User


class DutyAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'nickname', 'group', 'memo')

    def nickname(self, obj):
        u = User.get(obj.user_id)
        return u.nickname
    nickname.short_description = u'昵称'

<<<<<<< HEAD
<<<<<<< HEAD
=======

>>>>>>> 06ee61a08a7f9f3205bf93fbc086322697d154dc
=======

>>>>>>> 06ee61a08a7f9f3205bf93fbc086322697d154dc
class WageUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'date')


admin.site.register(Duty, DutyAdmin)
admin.site.register(WageUser, WageUserAdmin)
