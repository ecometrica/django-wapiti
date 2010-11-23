# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.
from django.contrib import admin

from models import *

class PermissionInline(admin.TabularInline):
    model = Permission

class APIKeyAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    inlines = [
        PermissionInline,
    ]

class PermissionAdmin(admin.ModelAdmin):
    pass

admin.site.register(APIKey, APIKeyAdmin)
admin.site.register(Permission, PermissionAdmin)

