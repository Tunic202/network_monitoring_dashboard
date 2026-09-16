import os

from dotenv import load_dotenv

from .snmp import get_system_description
from .snmp_mock import (
    get_mock_interfaces,
    get_mock_system_description,
)


load_dotenv()


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


class SNMPMonitoringProvider:
    """Provide monitoring data using SNMP."""

    async def get_system_description(self, device):
        return await get_system_description(
            str(device.ip_address)
        )


def get_monitoring_provider():
    """Return the configured monitoring provider."""

    provider_name = os.getenv(
        "MONITORING_PROVIDER",
        "mock",
    ).lower()

    if provider_name == "mock":
        return MockMonitoringProvider()

    if provider_name == "snmp":
        return SNMPMonitoringProvider()

    raise ValueError(
        f"Unsupported monitoring provider: {provider_name}"
    )
