from unittest.mock import Mock, patch

from django.test import TestCase
from django.urls import reverse

from .models import Device, Interface
from .monitoring import (
    check_device,
    monitor_all_devices,
    monitor_device,
    monitor_interfaces,
)


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
        """An enabled mock device should be reported as reachable."""

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
            Interface.objects.filter(
                device=self.device
            ).count(),
            3,
        )

    def test_monitor_device_saves_system_description(self):
        """Monitoring should save system description."""

        monitor_device(self.device)

        self.device.refresh_from_db()

        self.assertEqual(
            self.device.system_description,
            "Cisco IOS Software - Simulated Device",
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

    def test_offline_provider_clears_last_seen(self):
        """An offline provider result should clear last_seen."""

        self.device.last_seen = self.device.created_at
        self.device.save(
            update_fields=["last_seen"]
        )

        mock_provider = Mock()
        mock_provider.check_device.return_value = False

        with patch(
            "monitoring.monitoring.provider",
            mock_provider,
        ):
            result = monitor_device(self.device)

        self.assertFalse(result)

        self.device.refresh_from_db()

        self.assertIsNone(self.device.last_seen)

        mock_provider.check_device.assert_called_once_with(
            self.device
        )

    def test_provider_interfaces_are_saved(self):
        """Provider interface data should be persisted."""

        mock_provider = Mock()
        mock_provider.get_interfaces.return_value = [
            {
                "name": "GigabitEthernet0/5",
                "ip_address": "10.0.0.1",
                "status": "up",
            },
            {
                "name": "GigabitEthernet0/6",
                "ip_address": None,
                "status": "down",
            },
        ]

        with patch(
            "monitoring.monitoring.provider",
            mock_provider,
        ):
            interfaces = monitor_interfaces(
                self.device
            )

        self.assertEqual(len(interfaces), 2)

        interface = Interface.objects.get(
            device=self.device,
            name="GigabitEthernet0/5",
        )

        self.assertEqual(
            interface.ip_address,
            "10.0.0.1",
        )

        self.assertEqual(
            interface.status,
            "up",
        )

        mock_provider.get_interfaces.assert_called_once_with(
            self.device
        )


class DashboardViewTests(TestCase):
    """Test the monitoring dashboard and device detail pages."""

    def setUp(self):
        self.device = Device.objects.create(
            name="Test Router",
            ip_address="192.168.1.100",
            device_type="cisco_ios",
            location="Lab",
            enabled=True,
            system_description=(
                "Cisco IOS Software - Simulated Device"
            ),
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

    def test_dashboard_displays_last_seen(self):
        """The dashboard should display a device last-seen timestamp."""

        self.device.last_seen = self.device.created_at
        self.device.save(
            update_fields=["last_seen"]
        )

        response = self.client.get(
            reverse("monitoring:dashboard")
        )

        self.assertContains(
            response,
            self.device.last_seen.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
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

    def test_device_detail_displays_system_description(self):
        """The device detail page should display system information."""

        response = self.client.get(
            reverse(
                "monitoring:device_detail",
                args=[self.device.id],
            )
        )

        self.assertContains(
            response,
            "Cisco IOS Software - Simulated Device",
        )

    def test_device_detail_contains_edit_link(self):
        """The device detail page should contain an edit link."""

        response = self.client.get(
            reverse(
                "monitoring:device_detail",
                args=[self.device.id],
            )
        )

        self.assertContains(
            response,
            reverse(
                "monitoring:device_edit",
                args=[self.device.id],
            ),
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


class DeviceManagementTests(TestCase):
    """Test adding and editing devices through the web interface."""

    def setUp(self):
        self.device = Device.objects.create(
            name="Existing Router",
            ip_address="192.168.1.10",
            device_type="cisco_ios",
            location="Old Lab",
            enabled=True,
        )

    def test_add_device_page_loads(self):
        """The add-device page should load successfully."""

        response = self.client.get(
            reverse("monitoring:device_create")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Add Device",
        )

    def test_add_device_creates_device(self):
        """A valid form should create a new device."""

        data = {
            "name": "New Router",
            "ip_address": "192.168.1.20",
            "device_type": "cisco_ios",
            "snmp_version": "2c",
            "location": "New Lab",
            "enabled": True,
        }

        response = self.client.post(
            reverse("monitoring:device_create"),
            data=data,
        )

        new_device = Device.objects.get(
            ip_address="192.168.1.20"
        )

        self.assertRedirects(
            response,
            reverse(
                "monitoring:device_detail",
                args=[new_device.id],
            ),
        )

        self.assertEqual(
            new_device.name,
            "New Router",
        )

    def test_add_device_rejects_duplicate_ip(self):
        """A duplicate IP address should be rejected."""

        data = {
            "name": "Duplicate Router",
            "ip_address": "192.168.1.10",
            "device_type": "cisco_ios",
            "snmp_version": "2c",
            "location": "Lab",
            "enabled": True,
        }

        response = self.client.post(
            reverse("monitoring:device_create"),
            data=data,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Device with this Ip address already exists.",
        )

        self.assertEqual(
            Device.objects.filter(
                name="Duplicate Router"
            ).count(),
            0,
        )

    def test_edit_device_page_loads(self):
        """The edit-device page should load successfully."""

        response = self.client.get(
            reverse(
                "monitoring:device_edit",
                args=[self.device.id],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Edit Device",
        )

    def test_edit_device_updates_device(self):
        """A valid form should update an existing device."""

        data = {
            "name": "Updated Router",
            "ip_address": "192.168.1.11",
            "device_type": "cisco_ios",
            "snmp_version": "2c",
            "location": "Updated Lab",
            "enabled": True,
        }

        response = self.client.post(
            reverse(
                "monitoring:device_edit",
                args=[self.device.id],
            ),
            data=data,
        )

        self.assertRedirects(
            response,
            reverse(
                "monitoring:device_detail",
                args=[self.device.id],
            ),
        )

        self.device.refresh_from_db()

        self.assertEqual(
            self.device.name,
            "Updated Router",
        )

        self.assertEqual(
            str(self.device.ip_address),
            "192.168.1.11",
        )

        self.assertEqual(
            self.device.location,
            "Updated Lab",
        )

    def test_edit_invalid_device_returns_404(self):
        """Editing an invalid device ID should return 404."""

        response = self.client.get(
            reverse(
                "monitoring:device_edit",
                args=[9999],
            )
        )

        self.assertEqual(response.status_code, 404)
