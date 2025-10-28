"""Database models."""

from src.models.dns import DNSServer, ISP, ASNMapping, QueryLog

__all__ = ["DNSServer", "ISP", "ASNMapping", "QueryLog"]
