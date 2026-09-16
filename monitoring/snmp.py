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

    finally:
        snmp_engine.close_dispatcher()
