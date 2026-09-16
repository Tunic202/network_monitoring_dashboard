from django.utils import timezone

from .models import Device, Interface
from .providers import get_monitoring_provider


provider = get_monitoring_provider()


def check_device(device):
    """Check whether a device is reachable."""

    return provider.check_device(device)


def monitor_interfaces(device):
    """Update interface monitoring data for a device."""

    interfaces = provider.get_interfaces(device)
    checked_at = timezone.now()

    results = []

    for interface_data in interfaces:
        interface, created = Interface.objects.update_or_create(
            device=device,
            name=interface_data["name"],
            defaults={
                "ip_address": interface_data["ip_address"],
                "status": interface_data["status"],
                "last_checked": checked_at,
            },
        )

        results.append(interface)

    return results


def monitor_device(device):
    """Check a device and update its monitoring information."""

    checked_at = timezone.now()
    is_online = check_device(device)

    device.last_checked = checked_at

    if is_online:
        device.status = "online"
        device.last_seen = checked_at

        system_description = provider.get_system_description(
            device
        )

        if system_description:
            if isinstance(system_description, dict):
                device.system_description = system_description.get(
                    "sys_descr",
                    "",
                )
            else:
                device.system_description = str(
                    system_description
                )

        monitor_interfaces(device)

    else:
        device.status = "offline"
        device.last_seen = None
        device.system_description = ""

    device.save(
        update_fields=[
            "status",
            "last_seen",
            "last_checked",
            "system_description",
        ]
    )

    return is_online


def monitor_all_devices():
    """Check all enabled devices."""

    devices = Device.objects.filter(enabled=True)

    results = []

    for device in devices:
        is_online = monitor_device(device)

        results.append(
            {
                "device": device,
                "online": is_online,
            }
        )

    return results
