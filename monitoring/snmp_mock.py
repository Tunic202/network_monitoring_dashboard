def get_mock_system_description(ip_address):
    """Return simulated SNMP system information."""

    return {
        "ip_address": ip_address,
        "sys_descr": "Cisco IOS Software - Simulated Device",
        "sys_uptime": "14 days, 6 hours",
    }


def get_mock_interfaces(ip_address):
    """Return simulated SNMP interface information."""

    return [
        {
            "name": "GigabitEthernet0/0",
            "ip_address": ip_address,
            "status": "up",
        },
        {
            "name": "GigabitEthernet0/1",
            "ip_address": None,
            "status": "down",
        },
        {
            "name": "GigabitEthernet0/2",
            "ip_address": None,
            "status": "up",
        },
    ]
