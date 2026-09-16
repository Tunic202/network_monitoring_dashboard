from django.shortcuts import get_object_or_404, render

from .models import Device, Interface
from .monitoring import monitor_all_devices


def dashboard(request):
    """Display the network monitoring dashboard."""

    monitor_all_devices()

    devices = Device.objects.filter(enabled=True)
    interfaces = Interface.objects.filter(
        device__enabled=True
    )

    context = {
        "devices": devices,
        "device_count": devices.count(),
        "online_count": devices.filter(
            last_seen__isnull=False
        ).count(),
        "offline_count": devices.filter(
            last_seen__isnull=True
        ).count(),
        "interfaces": interfaces,
        "interface_count": interfaces.count(),
        "interface_up_count": interfaces.filter(
            status="up"
        ).count(),
        "interface_down_count": interfaces.filter(
            status="down"
        ).count(),
    }

    return render(
        request,
        "monitoring/dashboard.html",
        context,
    )


def device_detail(request, device_id):
    """Display details and interfaces for one device."""

    device = get_object_or_404(
        Device,
        id=device_id,
    )

    interfaces = Interface.objects.filter(
        device=device
    ).order_by("name")

    context = {
        "device": device,
        "interfaces": interfaces,
    }

    return render(
        request,
        "monitoring/device_detail.html",
        context,
    )
