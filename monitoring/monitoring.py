from django.utils import timezone

from .models import Device, Interface
from .providers import get_monitoring_provider


provider = get_monitoring_provider()


def check_device(device):
    """Simulate checking whether a device is reachable."""

    if not device.enabled:
        return False

    return True


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
    """Check a device and update its monitoring status."""

    is_online = check_device(device)

    if is_online:
        device.last_seen = timezone.now()
        monitor_interfaces(device)
    else:
        device.last_seen = None

    device.save(update_fields=["last_seen"])

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
