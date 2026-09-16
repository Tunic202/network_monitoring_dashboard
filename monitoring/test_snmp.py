from unittest.mock import AsyncMock, patch

from django.test import SimpleTestCase

from .snmp import get_interfaces
from .snmp_mock import (
    get_mock_interfaces,
    get_mock_system_description,
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


class SNMPInterfaceTests(SimpleTestCase):
    """Test parsing of SNMP interface information."""

    async def test_get_interfaces(self):
        """SNMP interface data should be converted into dictionaries."""

        mock_var_binds = [
            (
                "1.3.6.1.2.1.2.2.1.2.1",
                "GigabitEthernet0/0",
            ),
            (
                "1.3.6.1.2.1.2.2.1.2.2",
                "GigabitEthernet0/1",
            ),
            (
                "1.3.6.1.2.1.2.2.1.2.3",
                "GigabitEthernet0/2",
            ),
        ]

        async def mock_walk_cmd(*args, **kwargs):
            for var_bind in mock_var_binds:
                yield (
                    None,
                    0,
                    0,
                    [var_bind],
                )

        with patch(
            "monitoring.snmp.walk_cmd",
            side_effect=mock_walk_cmd,
        ), patch(
            "monitoring.snmp.SnmpEngine"
        ) as mock_engine:

            mock_engine.return_value.close_dispatcher = (
                lambda: None
            )

            result = await get_interfaces(
                "192.168.1.1"
            )

        self.assertEqual(
            len(result),
            3,
        )

        self.assertEqual(
            result[0]["index"],
            "1",
        )

        self.assertEqual(
            result[0]["name"],
            "GigabitEthernet0/0",
        )

        self.assertEqual(
            result[1]["index"],
            "2",
        )

        self.assertEqual(
            result[1]["name"],
            "GigabitEthernet0/1",
        )

        self.assertEqual(
            result[2]["index"],
            "3",
        )

        self.assertEqual(
            result[2]["name"],
            "GigabitEthernet0/2",
        )
