from .snmp_mock import (
    get_mock_interfaces,
    get_mock_system_description,
)


class MockMonitoringProvider:
    """Provide simulated monitoring data."""

    def get_system_description(self, device):
        return get_mock_system_description(
            str(device.ip_address)
        )

    def get_interfaces(self, device):
        return get_mock_interfaces(
            str(device.ip_address)
        )
