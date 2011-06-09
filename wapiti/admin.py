# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.
from django.contrib import admin

from models import *

class PermissionInline(admin.TabularInline):
    model = Permission

class LimitInline(admin.TabularInline):
    model = Limit

class APIKeyAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    inlines = [
        PermissionInline,
        LimitInline,
    ]

class PermissionAdmin(admin.ModelAdmin):
    pass

class LimitTrackingInline(admin.TabularInline):
    model = LimitTracking

class LimitAdmin(admin.ModelAdmin):
    inlines = [
        LimitTrackingInline,
    ]

class LimitTrackingAdmin(admin.ModelAdmin):
    model = LimitTracking
    list_display = ('count', 'user', 'session_id', 'last_update', 'limit')

admin.site.register(APIKey, APIKeyAdmin)
admin.site.register(Permission, PermissionAdmin)
admin.site.register(Limit, LimitAdmin)
admin.site.register(LimitTracking, LimitTrackingAdmin)

