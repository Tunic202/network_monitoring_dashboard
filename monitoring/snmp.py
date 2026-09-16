import os

from dotenv import load_dotenv
from pysnmp.hlapi.v3arch.asyncio import (
    CommunityData,
    ContextData,
    ObjectIdentity,
    ObjectType,
    SnmpEngine,
    UdpTransportTarget,
    get_cmd,
    walk_cmd,
)


load_dotenv()


SNMP_COMMUNITY = os.getenv(
    "SNMP_COMMUNITY",
    "public",
)

SNMP_PORT = int(
    os.getenv(
        "SNMP_PORT",
        "161",
    )
)


def normalize_interface_status(status):
    """Convert an SNMP ifOperStatus value to a readable status."""

    status_map = {
        1: "up",
        2: "down",
        3: "testing",
        4: "unknown",
        5: "dormant",
        6: "not_present",
        7: "lower_layer_down",
    }

    return status_map.get(
        int(status),
        "unknown",
    )


async def get_system_description(
    ip_address,
    community=SNMP_COMMUNITY,
    port=SNMP_PORT,
    timeout=2,
    retries=1,
):
    """Retrieve the system description from an SNMP device."""

    snmp_engine = SnmpEngine()

    try:
        error_indication, error_status, error_index, var_binds = await get_cmd(
            snmp_engine,
            CommunityData(
                community,
                mpModel=1,
            ),
            await UdpTransportTarget.create(
                (ip_address, port),
                timeout=timeout,
                retries=retries,
            ),
            ContextData(),
            ObjectType(
                ObjectIdentity(
                    "SNMPv2-MIB",
                    "sysDescr",
                    0,
                )
            ),
        )

        if error_indication or error_status:
            return None

        for var_bind in var_binds:
            return str(var_bind[1])

        return None

    except Exception:
        return None

    finally:
        snmp_engine.close_dispatcher()


async def get_interfaces(
    ip_address,
    community=SNMP_COMMUNITY,
    port=SNMP_PORT,
    timeout=2,
    retries=1,
):
    """Retrieve interface names from an SNMP device."""

    snmp_engine = SnmpEngine()

    interfaces = []

    try:
        async for (
            error_indication,
            error_status,
            error_index,
            var_binds,
        ) in walk_cmd(
            snmp_engine,
            CommunityData(
                community,
                mpModel=1,
            ),
            await UdpTransportTarget.create(
                (ip_address, port),
                timeout=timeout,
                retries=retries,
            ),
            ContextData(),
            ObjectType(
                ObjectIdentity(
                    "IF-MIB",
                    "ifDescr",
                )
            ),
            lexicographicMode=False,
        ):
            if error_indication or error_status:
                return []

            for var_bind in var_binds:
                oid, value = var_bind

                oid_string = str(oid)
                interface_index = oid_string.split(".")[-1]

                interfaces.append(
                    {
                        "index": interface_index,
                        "name": str(value),
                    }
                )

        return interfaces

    except Exception:
        return []

    finally:
        snmp_engine.close_dispatcher()


async def get_interface_statuses(
    ip_address,
    community=SNMP_COMMUNITY,
    port=SNMP_PORT,
    timeout=2,
    retries=1,
):
    """Retrieve operational status for all SNMP interfaces."""

    snmp_engine = SnmpEngine()

    statuses = {}

    try:
        async for (
            error_indication,
            error_status,
            error_index,
            var_binds,
        ) in walk_cmd(
            snmp_engine,
            CommunityData(
                community,
                mpModel=1,
            ),
            await UdpTransportTarget.create(
                (ip_address, port),
                timeout=timeout,
                retries=retries,
            ),
            ContextData(),
            ObjectType(
                ObjectIdentity(
                    "IF-MIB",
                    "ifOperStatus",
                )
            ),
            lexicographicMode=False,
        ):
            if error_indication or error_status:
                return {}

            for var_bind in var_binds:
                oid, value = var_bind

                oid_string = str(oid)
                interface_index = oid_string.split(".")[-1]

                statuses[interface_index] = (
                    normalize_interface_status(value)
                )

        return statuses

    except Exception:
        return {}

    finally:
        snmp_engine.close_dispatcher()
