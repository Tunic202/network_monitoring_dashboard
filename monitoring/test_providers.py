from unittest.mock import patch

from django.test import TestCase

from .models import Device
from .providers import (
    MockMonitoringProvider,
    get_monitoring_provider,
)


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


class MonitoringProviderSelectionTests(TestCase):
    """Test monitoring provider selection."""

    def test_default_provider_is_mock(self):
        """The default provider should be the mock provider."""

        with patch.dict(
            "os.environ",
            {},
            clear=True,
        ):
            provider = get_monitoring_provider()

        self.assertIsInstance(
            provider,
            MockMonitoringProvider,
        )

    def test_mock_provider_is_selected(self):
        """The mock provider should be selected explicitly."""

        with patch.dict(
            "os.environ",
            {"MONITORING_PROVIDER": "mock"},
            clear=True,
        ):
            provider = get_monitoring_provider()

        self.assertIsInstance(
            provider,
            MockMonitoringProvider,
        )

    def test_provider_name_is_case_insensitive(self):
        """Provider selection should ignore letter case."""

        with patch.dict(
            "os.environ",
            {"MONITORING_PROVIDER": "MOCK"},
            clear=True,
        ):
            provider = get_monitoring_provider()

        self.assertIsInstance(
            provider,
            MockMonitoringProvider,
        )

    def test_unsupported_provider_raises_error(self):
        """An unsupported provider should raise ValueError."""

        with patch.dict(
            "os.environ",
            {"MONITORING_PROVIDER": "invalid"},
            clear=True,
        ):
            with self.assertRaises(ValueError):
                get_monitoring_provider()
