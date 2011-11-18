from django.contrib import admin
from apps.components.analytics.models import ApacheLog, MakahikiLog

class ApacheLogAdmin(admin.ModelAdmin):
    # ...
    list_display = ('host', 'url', 'request_time')

admin.site.register(ApacheLog, ApacheLogAdmin)

class MakahikiLogAdmin(admin.ModelAdmin):
    # ...
    list_display = ('host', "remote_user", 'url', 'request_time')

admin.site.register(MakahikiLog, MakahikiLogAdmin)