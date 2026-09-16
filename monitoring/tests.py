from django.test import TestCase
from django.urls import reverse

from .models import Device, Interface
from .monitoring import (
    check_device,
    monitor_device,
    monitor_interfaces,
    monitor_all_devices,
)
from .snmp_mock import get_mock_interfaces


class MonitoringTests(TestCase):
    """Test the network monitoring service."""

    def setUp(self):
        self.device = Device.objects.create(
            name="Test Router",
            ip_address="192.168.1.100",
            device_type="cisco_ios",
            location="Lab",
            enabled=True,
        )

    def test_check_enabled_device(self):
        """An enabled device should be reported as reachable."""

        result = check_device(self.device)

        self.assertTrue(result)

    def test_check_disabled_device(self):
        """A disabled device should not be monitored."""

        self.device.enabled = False

        result = check_device(self.device)

        self.assertFalse(result)

    def test_monitor_device_updates_last_seen(self):
        """Monitoring an online device should update last_seen."""

        self.assertIsNone(self.device.last_seen)

        result = monitor_device(self.device)

        self.assertTrue(result)

        self.device.refresh_from_db()

        self.assertIsNotNone(self.device.last_seen)

    def test_monitor_device_creates_interfaces(self):
        """Monitoring a device should create its interfaces."""

        monitor_device(self.device)

        self.assertEqual(
            Interface.objects.filter(device=self.device).count(),
            3,
        )

    def test_monitor_interfaces(self):
        """Interface monitoring should save interface state."""

        interfaces = monitor_interfaces(self.device)

        self.assertEqual(len(interfaces), 3)

        self.assertEqual(
            Interface.objects.filter(
                device=self.device,
                status="up",
            ).count(),
            2,
        )

        self.assertEqual(
            Interface.objects.filter(
                device=self.device,
                status="down",
            ).count(),
            1,
        )

    def test_monitor_all_devices(self):
        """All enabled devices should be monitored."""

        Device.objects.create(
            name="Test Router 2",
            ip_address="192.168.1.101",
            device_type="cisco_ios",
            location="Lab",
            enabled=True,
        )

        results = monitor_all_devices()

        self.assertEqual(len(results), 2)

        for result in results:
            self.assertTrue(result["online"])


class DashboardViewTests(TestCase):
    """Test the monitoring dashboard and device detail pages."""

    def setUp(self):
        self.device = Device.objects.create(
            name="Test Router",
            ip_address="192.168.1.100",
            device_type="cisco_ios",
            location="Lab",
            enabled=True,
        )

        Interface.objects.create(
            device=self.device,
            name="GigabitEthernet0/0",
            ip_address="192.168.1.100",
            status="up",
        )

        Interface.objects.create(
            device=self.device,
            name="GigabitEthernet0/1",
            ip_address=None,
            status="down",
        )

    def test_dashboard_loads(self):
        """The dashboard should return a successful response."""

        response = self.client.get(
            reverse("monitoring:dashboard")
        )

        self.assertEqual(response.status_code, 200)

    def test_dashboard_displays_device(self):
        """The dashboard should display the device name."""

        response = self.client.get(
            reverse("monitoring:dashboard")
        )

        self.assertContains(
            response,
            "Test Router",
        )

    def test_device_detail_loads(self):
        """The device detail page should return a successful response."""

        response = self.client.get(
            reverse(
                "monitoring:device_detail",
                args=[self.device.id],
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_device_detail_displays_interfaces(self):
        """The device detail page should display its interfaces."""

        response = self.client.get(
            reverse(
                "monitoring:device_detail",
                args=[self.device.id],
            )
        )

        self.assertContains(
            response,
            "GigabitEthernet0/0",
        )

        self.assertContains(
            response,
            "GigabitEthernet0/1",
        )

    def test_invalid_device_returns_404(self):
        """An invalid device ID should return a 404 response."""

        response = self.client.get(
            reverse(
                "monitoring:device_detail",
                args=[9999],
            )
        )

        self.assertEqual(response.status_code, 404)
