from django.contrib import admin

from django.contrib.auth.admin import UserAdmin

from user.models import BanUser, User, SpecialReportUser


@admin.register(BanUser)
class BanUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'get_nickname', 'desc')

    def get_nickname(self, obj):
        return User.get(obj.user_id).nickname
    get_nickname.short_description = u"昵称"


class PaUserAdmin(UserAdmin):
    search_fields = ('paid', 'nickname', 'mobile')
    list_display = ('nickname', 'mobile', 'id')
    ordering = ('-id',)


class SpecialReportUserAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'date')

    def nickname(self, obj):
        u = User.get(obj.user_id)
        return u.nickname
    nickname.short_description = u'用户ID'


admin.site.unregister(User)
admin.site.register(User, PaUserAdmin)
admin.site.register(SpecialReportUser, SpecialReportUserAdmin)
