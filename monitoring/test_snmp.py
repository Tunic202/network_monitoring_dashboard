from django.test import SimpleTestCase

from .snmp_mock import (
    get_mock_system_description,
    get_mock_interfaces,
)


class MockSNMPTests(SimpleTestCase):
    """Test the mock SNMP provider."""

    def test_mock_system_description(self):
        """Mock SNMP should return system information."""

        result = get_mock_system_description(
            "192.168.1.1"
        )

        self.assertEqual(
            result["ip_address"],
            "192.168.1.1",
        )

        self.assertIn(
            "Cisco IOS",
            result["sys_descr"],
        )

        self.assertIn(
            "14 days",
            result["sys_uptime"],
        )

    def test_mock_interfaces(self):
        """Mock SNMP should return three interfaces."""

        result = get_mock_interfaces(
            "192.168.1.1"
        )

        self.assertEqual(
            len(result),
            3,
        )

        self.assertEqual(
            result[0]["name"],
            "GigabitEthernet0/0",
        )

        self.assertEqual(
            result[0]["status"],
            "up",
        )

        self.assertEqual(
            result[1]["status"],
            "down",
        )
