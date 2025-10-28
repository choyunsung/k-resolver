"""Seed initial data for Korean ISPs and their DNS servers."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select

from src.core.database import AsyncSessionLocal, engine
from src.models.dns import ASNMapping, DNSServer, ISP


async def seed_data():
    """Seed initial ISP and DNS server data."""
    print("🌱 Seeding initial data...")

    async with AsyncSessionLocal() as session:
        # Check if data already exists
        result = await session.execute(select(ISP))
        if result.scalars().first():
            print("⚠️  Data already exists. Skipping seed.")
            return

        # Create ISPs
        isps_data = [
            {
                "name": "KT",
                "name_en": "KT Corporation",
                "country": "KR",
                "isp_type": "both",
                "asns": [4766],
            },
            {
                "name": "SK브로드밴드",
                "name_en": "SK Broadband",
                "country": "KR",
                "isp_type": "both",
                "asns": [9318],
            },
            {
                "name": "LG U+",
                "name_en": "LG Uplus",
                "country": "KR",
                "isp_type": "both",
                "asns": [17858],
            },
            {
                "name": "SK텔레콤",
                "name_en": "SK Telecom",
                "country": "KR",
                "isp_type": "mobile",
                "asns": [9318],
            },
        ]

        # DNS servers data for each ISP
        dns_servers_data = {
            "KT": [
                {"ip": "168.126.63.1", "priority": 1, "region": "전국"},
                {"ip": "168.126.63.2", "priority": 2, "region": "전국"},
            ],
            "SK브로드밴드": [
                {"ip": "210.220.163.82", "priority": 1, "region": "전국"},
                {"ip": "219.250.36.130", "priority": 2, "region": "전국"},
            ],
            "LG U+": [
                {"ip": "164.124.101.2", "priority": 1, "region": "전국"},
                {"ip": "203.248.252.2", "priority": 2, "region": "전국"},
            ],
            "SK텔레콤": [
                {"ip": "210.220.163.82", "priority": 1, "region": "전국"},
                {"ip": "219.250.36.130", "priority": 2, "region": "전국"},
            ],
        }

        # Insert ISPs and their DNS servers
        for isp_data in isps_data:
            asns = isp_data.pop("asns")

            # Create ISP
            isp = ISP(
                name=isp_data["name"],
                name_en=isp_data["name_en"],
                country=isp_data["country"],
                isp_type=isp_data["isp_type"],
            )
            session.add(isp)
            await session.flush()

            print(f"✅ Created ISP: {isp.name} (ID: {isp.id})")

            # Create ASN mappings
            for asn in asns:
                asn_mapping = ASNMapping(
                    isp_id=isp.id,
                    asn=asn,
                    as_name=isp_data["name_en"],
                )
                session.add(asn_mapping)

            # Create DNS servers
            if isp.name in dns_servers_data:
                for dns_data in dns_servers_data[isp.name]:
                    dns_server = DNSServer(
                        isp_id=isp.id,
                        ip_address=dns_data["ip"],
                        priority=dns_data["priority"],
                        region=dns_data.get("region"),
                        server_type="standard",
                        is_active=True,
                    )
                    session.add(dns_server)
                    print(f"  ✅ Added DNS: {dns_data['ip']} (Priority: {dns_data['priority']})")

        # Add public DNS servers (Google, Cloudflare, Quad9)
        print("\n📡 Adding public DNS servers...")

        public_isps = [
            {
                "name": "Google Public DNS",
                "name_en": "Google Public DNS",
                "country": "US",
                "isp_type": "both",
                "dns_servers": [
                    {"ip": "8.8.8.8", "priority": 1, "doh_url": "https://dns.google/dns-query"},
                    {"ip": "8.8.4.4", "priority": 2, "doh_url": "https://dns.google/dns-query"},
                ],
            },
            {
                "name": "Cloudflare DNS",
                "name_en": "Cloudflare DNS",
                "country": "US",
                "isp_type": "both",
                "dns_servers": [
                    {"ip": "1.1.1.1", "priority": 1, "doh_url": "https://cloudflare-dns.com/dns-query"},
                    {"ip": "1.0.0.1", "priority": 2, "doh_url": "https://cloudflare-dns.com/dns-query"},
                ],
            },
            {
                "name": "Quad9 DNS",
                "name_en": "Quad9 DNS",
                "country": "US",
                "isp_type": "both",
                "dns_servers": [
                    {"ip": "9.9.9.9", "priority": 1, "doh_url": "https://dns.quad9.net/dns-query"},
                    {"ip": "149.112.112.112", "priority": 2, "doh_url": "https://dns.quad9.net/dns-query"},
                ],
            },
        ]

        for public_isp_data in public_isps:
            dns_servers = public_isp_data.pop("dns_servers")

            public_isp = ISP(
                name=public_isp_data["name"],
                name_en=public_isp_data["name_en"],
                country=public_isp_data["country"],
                isp_type=public_isp_data["isp_type"],
            )
            session.add(public_isp)
            await session.flush()

            print(f"✅ Created Public DNS: {public_isp.name} (ID: {public_isp.id})")

            for dns_data in dns_servers:
                server_type = "doh" if dns_data.get("doh_url") else "standard"
                dns_server = DNSServer(
                    isp_id=public_isp.id,
                    ip_address=dns_data["ip"],
                    priority=dns_data["priority"],
                    server_type=server_type,
                    doh_url=dns_data.get("doh_url"),
                    is_anycast=True,
                    is_active=True,
                )
                session.add(dns_server)
                print(f"  ✅ Added DNS: {dns_data['ip']} (Priority: {dns_data['priority']})")

        await session.commit()
        print("\n✅ Seeding completed successfully!")


async def main():
    """Main entry point."""
    try:
        await seed_data()
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
