from django.contrib import admin

from daka.models import Task, Log


class TaskAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'daka_time', 'created')
    readonly_fields = ('created',)


class LogAdmin(admin.ModelAdmin):
    list_display = ('task', 'message', 'created')


admin.site.register(Task, TaskAdmin)
admin.site.register(Log, LogAdmin)
