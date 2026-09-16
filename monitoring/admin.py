from django.contrib import admin

from .models import Device, Interface


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "ip_address",
        "device_type",
        "location",
        "enabled",
        "last_seen",
    )
    list_filter = (
        "device_type",
        "enabled",
    )
    search_fields = (
        "name",
        "ip_address",
        "location",
    )


@admin.register(Interface)
class InterfaceAdmin(admin.ModelAdmin):
    list_display = (
        "device",
        "name",
        "ip_address",
        "status",
        "last_checked",
    )
    list_filter = (
        "status",
    )
    search_fields = (
        "name",
        "ip_address",
        "device__name",
    )
