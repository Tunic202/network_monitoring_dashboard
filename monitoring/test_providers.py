from django.test import TestCase

from .models import Device
from .providers import MockMonitoringProvider


class MockMonitoringProviderTests(TestCase):
    """Test the mock monitoring provider."""

    def setUp(self):
        self.device = Device.objects.create(
            name="Test Router",
            ip_address="192.168.1.100",
            device_type="cisco_ios",
            location="Lab",
            enabled=True,
        )

        self.provider = MockMonitoringProvider()

    def test_get_system_description(self):
        """The provider should return system information."""

        result = self.provider.get_system_description(
            self.device
        )

        self.assertEqual(
            result["ip_address"],
            "192.168.1.100",
        )

        self.assertIn(
            "Cisco IOS",
            result["sys_descr"],
        )

    def test_get_interfaces(self):
        """The provider should return interface information."""

        result = self.provider.get_interfaces(
            self.device
        )

        self.assertEqual(
            len(result),
            3,
        )

        self.assertEqual(
            result[0]["name"],
            "GigabitEthernet0/0",
        )
