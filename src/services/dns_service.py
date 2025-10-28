"""DNS resolution and query service."""

import time
from typing import Optional

import dns.resolver


class DNSService:
    """DNS query and resolution service."""

    @staticmethod
    async def resolve_domain(
        domain: str, dns_server: Optional[str] = None, record_type: str = "A"
    ) -> dict:
        """Resolve domain using specified DNS server."""
        start_time = time.time()

        try:
            resolver = dns.resolver.Resolver()

            if dns_server:
                resolver.nameservers = [dns_server]

            # Query DNS
            answers = resolver.resolve(domain, record_type)

            # Extract results
            results = [str(rdata) for rdata in answers]

            response_time_ms = int((time.time() - start_time) * 1000)

            return {
                "domain": domain,
                "dns_server": dns_server or "system_default",
                "record_type": record_type,
                "answers": results,
                "response_time_ms": response_time_ms,
                "success": True,
                "error_message": None,
            }

        except dns.exception.DNSException as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            return {
                "domain": domain,
                "dns_server": dns_server or "system_default",
                "record_type": record_type,
                "answers": [],
                "response_time_ms": response_time_ms,
                "success": False,
                "error_message": str(e),
            }
        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            return {
                "domain": domain,
                "dns_server": dns_server or "system_default",
                "record_type": record_type,
                "answers": [],
                "response_time_ms": response_time_ms,
                "success": False,
                "error_message": f"Unexpected error: {str(e)}",
            }

    @staticmethod
    def generate_command_examples(domain: str, dns_server: str) -> list[dict]:
        """Generate DNS query command examples for different platforms."""
        return [
            {
                "platform": "windows",
                "command": f"nslookup {domain} {dns_server}",
                "description": "Windows에서 nslookup 사용",
            },
            {
                "platform": "macos",
                "command": f"dig @{dns_server} {domain}",
                "description": "macOS에서 dig 사용",
            },
            {
                "platform": "linux",
                "command": f"dig @{dns_server} {domain}",
                "description": "Linux에서 dig 사용",
            },
            {
                "platform": "linux",
                "command": f"nslookup {domain} {dns_server}",
                "description": "Linux에서 nslookup 사용 (대안)",
            },
        ]
