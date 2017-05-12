from django.contrib import admin

from user.models import BanUser


@admin.register(BanUser)
class BanUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'get_nickname', 'desc')

    def get_nickname(self, obj):
        return User.get(obj.user_id).nickname
    get_nickname.short_description = u"昵称"
