import asyncio
import os

from dotenv import load_dotenv

from .snmp import (
    get_interface_statuses,
    get_interfaces as snmp_get_interfaces,
    get_system_description,
)
from .snmp_mock import (
    get_mock_interfaces,
    get_mock_system_description,
)


load_dotenv()


def run_async(coroutine):
    """Run an asynchronous operation synchronously."""

    return asyncio.run(coroutine)


class MockMonitoringProvider:
    """Provide simulated monitoring data."""

    def check_device(self, device):
        """Simulate checking whether a device is reachable."""

        if not device.enabled:
            return False

        return True

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

    def check_device(self, device):
        """Check whether the device responds to SNMP."""

        if not device.enabled:
            return False

        result = run_async(
            get_system_description(
                str(device.ip_address)
            )
        )

        return result is not None

    def get_system_description(self, device):
        return run_async(
            get_system_description(
                str(device.ip_address)
            )
        )

    def get_interfaces(self, device):
        interfaces = run_async(
            snmp_get_interfaces(
                str(device.ip_address)
            )
        )

        statuses = run_async(
            get_interface_statuses(
                str(device.ip_address)
            )
        )

        results = []

        for interface in interfaces:
            interface_index = interface["index"]

            results.append(
                {
                    "name": interface["name"],
                    "ip_address": None,
                    "status": statuses.get(
                        interface_index,
                        "unknown",
                    ),
                }
            )

        return results


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
