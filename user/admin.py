from django.contrib import admin

from django.contrib.auth.admin import UserAdmin

from user.models import BanUser, User, SpecialReportUser, UserReport


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


class ReportUserAdmin(admin.ModelAdmin):
    list_display = ('report_user', 'be_report_user', 'be_report_user_id', 'desc', 'date')

    def report_user(self, obj):
        u = User.get(obj.user_id)
        return u.nickname
    report_user.short_description = u'举报人'

    def be_report_user(self, obj):
        u = User.get(obj.to_user_id)
        return u.nickname
    be_report_user.short_description = u'被举报人'

    def be_report_user_id(self, obj):
        return obj.to_user_id
    be_report_user_id.short_description = u'被举报人ID'

    def desc(self, obj):
        if obj.type == 2:
            return "自动封禁"
        elif obj.type == 1:
            return "普通举报"
        return obj.type
    desc.short_description = u'说明'


admin.site.unregister(User)
admin.site.register(User, PaUserAdmin)
admin.site.register(SpecialReportUser, SpecialReportUserAdmin)
admin.site.register(UserReport, ReportUserAdmin)
