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
)


load_dotenv()

SNMP_COMMUNITY = os.getenv("SNMP_COMMUNITY", "public")


async def get_system_description(
    ip_address,
    community=SNMP_COMMUNITY,
    port=161,
    timeout=2,
    retries=1,
):
    """Retrieve the system description from an SNMP device."""

    snmp_engine = SnmpEngine()

    try:
        error_indication, error_status, error_index, var_binds = await get_cmd(
            snmp_engine,
            CommunityData(community, mpModel=1),
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

        if error_indication:
            return None

        if error_status:
            return None

        for var_bind in var_binds:
            return str(var_bind[1])

        return None

    finally:
        snmp_engine.close_dispatcher()
