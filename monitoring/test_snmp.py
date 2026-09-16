from unittest.mock import patch

from django.test import SimpleTestCase

from .snmp import (
    get_interfaces,
    get_interface_statuses,
    get_system_description,
    normalize_interface_status,
)
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

    async def test_get_interfaces_handles_exception(self):
        """SNMP interface errors should return an empty list."""

        async def mock_walk_cmd(*args, **kwargs):
            raise RuntimeError("SNMP timeout")
            yield

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

        self.assertEqual(result, [])


class SNMPStatusTests(SimpleTestCase):
    """Test SNMP interface operational status handling."""

    def test_normalize_interface_status(self):
        """SNMP status codes should map to readable values."""

        expected_statuses = {
            1: "up",
            2: "down",
            3: "testing",
            4: "unknown",
            5: "dormant",
            6: "not_present",
            7: "lower_layer_down",
        }

        for code, expected in expected_statuses.items():
            with self.subTest(code=code):
                self.assertEqual(
                    normalize_interface_status(code),
                    expected,
                )

    def test_unknown_interface_status_defaults_to_unknown(self):
        """Unknown SNMP status codes should become unknown."""

        self.assertEqual(
            normalize_interface_status(99),
            "unknown",
        )

    async def test_get_interface_statuses(self):
        """SNMP interface statuses should be returned by index."""

        mock_var_binds = [
            (
                "1.3.6.1.2.1.2.2.1.8.1",
                1,
            ),
            (
                "1.3.6.1.2.1.2.2.1.8.2",
                2,
            ),
            (
                "1.3.6.1.2.1.2.2.1.8.3",
                7,
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

            result = await get_interface_statuses(
                "192.168.1.1"
            )

        self.assertEqual(
            result,
            {
                "1": "up",
                "2": "down",
                "3": "lower_layer_down",
            },
        )

    async def test_get_interface_statuses_handles_exception(self):
        """SNMP status errors should return an empty dictionary."""

        async def mock_walk_cmd(*args, **kwargs):
            raise RuntimeError("SNMP timeout")
            yield

        with patch(
            "monitoring.snmp.walk_cmd",
            side_effect=mock_walk_cmd,
        ), patch(
            "monitoring.snmp.SnmpEngine"
        ) as mock_engine:

            mock_engine.return_value.close_dispatcher = (
                lambda: None
            )

            result = await get_interface_statuses(
                "192.168.1.1"
            )

        self.assertEqual(result, {})


class SNMPSystemDescriptionTests(SimpleTestCase):
    """Test SNMP system-description handling."""

    async def test_get_system_description_handles_exception(self):
        """SNMP system errors should return None."""

        async def mock_get_cmd(*args, **kwargs):
            raise RuntimeError("SNMP timeout")

        with patch(
            "monitoring.snmp.get_cmd",
            side_effect=mock_get_cmd,
        ), patch(
            "monitoring.snmp.SnmpEngine"
        ) as mock_engine:

            mock_engine.return_value.close_dispatcher = (
                lambda: None
            )

            result = await get_system_description(
                "192.168.1.1"
            )

        self.assertIsNone(result)
