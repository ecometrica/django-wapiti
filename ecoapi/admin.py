from django.contrib import admin

from models import *

class APIKeyAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

class PermissionAdmin(admin.ModelAdmin):
    pass

admin.site.register(APIKey, APIKeyAdmin)
admin.site.register(Permission, PermissionAdmin)

