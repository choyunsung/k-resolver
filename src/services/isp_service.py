"""ISP detection and management service."""

from typing import Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.dns import ASNMapping, DNSServer, ISP


class ISPService:
    """ISP detection and management service."""

    @staticmethod
    async def get_all_isps(db: AsyncSession, include_dns: bool = False) -> list[ISP]:
        """Get all ISPs."""
        if include_dns:
            result = await db.execute(select(ISP).options(selectinload(ISP.dns_servers)))
        else:
            result = await db.execute(select(ISP))
        return list(result.scalars().all())

    @staticmethod
    async def get_isp_by_id(db: AsyncSession, isp_id: int, include_dns: bool = False) -> Optional[ISP]:
        """Get ISP by ID."""
        if include_dns:
            result = await db.execute(
                select(ISP).where(ISP.id == isp_id).options(selectinload(ISP.dns_servers))
            )
        else:
            result = await db.execute(select(ISP).where(ISP.id == isp_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_dns_servers_by_isp(db: AsyncSession, isp_id: int) -> list[DNSServer]:
        """Get DNS servers for specific ISP."""
        result = await db.execute(
            select(DNSServer)
            .where(DNSServer.isp_id == isp_id)
            .where(DNSServer.is_active == True)
            .order_by(DNSServer.priority)
        )
        return list(result.scalars().all())

    @staticmethod
    async def detect_isp_from_ip(db: AsyncSession, ip_address: str) -> Optional[dict]:
        """Detect ISP from IP address using ASN lookup."""
        # Try to get ASN info from IP
        asn_info = await ISPService._get_asn_from_ip(ip_address)

        if not asn_info:
            return None

        # Find ISP by ASN
        result = await db.execute(
            select(ISP)
            .join(ASNMapping)
            .where(ASNMapping.asn == asn_info["asn"])
            .options(selectinload(ISP.dns_servers))
        )

        isp = result.scalar_one_or_none()

        return {
            "ip_address": ip_address,
            "asn": asn_info["asn"],
            "as_name": asn_info["as_name"],
            "isp": isp,
            "detected": isp is not None,
        }

    @staticmethod
    async def _get_asn_from_ip(ip_address: str) -> Optional[dict]:
        """Get ASN information from IP address using Team Cymru service."""
        try:
            # Use Team Cymru's whois service (free, no API key needed)
            # Alternative: MaxMind GeoIP2 (requires license key)
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"https://api.bgpview.io/ip/{ip_address}",
                    headers={"Accept": "application/json"},
                )

                if response.status_code == 200:
                    data = response.json()
                    prefixes = data.get("data", {}).get("prefixes", [])

                    if prefixes:
                        prefix = prefixes[0]
                        return {
                            "asn": prefix.get("asn", {}).get("asn"),
                            "as_name": prefix.get("asn", {}).get("name"),
                        }

        except Exception:
            pass

        return None
