from django.contrib import admin

from ida.models import Duty


class DutyAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'name', 'mobile', 'group')

admin.site.register(Duty, DutyAdmin)
