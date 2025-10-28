"""API routes."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import (
    DNSCommandExample,
    DNSResolveRequest,
    DNSResolveResponse,
    DNSServerResponse,
    DNSServerWithISP,
    ISPDetectionRequest,
    ISPDetectionResponse,
    ISPResponse,
    ISPWithDNS,
)
from src.core.database import get_db
from src.models.dns import QueryLog
from src.services.dns_service import DNSService
from src.services.isp_service import ISPService

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/isps", response_model=list[ISPWithDNS])
async def get_isps(
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db),
) -> list[ISPWithDNS]:
    """Get all ISPs with their DNS servers."""
    isps = await ISPService.get_all_isps(db, include_dns=True)

    if not include_inactive:
        isps = [isp for isp in isps if isp.is_active]

    return isps


@router.get("/isps/{isp_id}", response_model=ISPWithDNS)
async def get_isp(
    isp_id: int,
    db: AsyncSession = Depends(get_db),
) -> ISPWithDNS:
    """Get specific ISP with DNS servers."""
    isp = await ISPService.get_isp_by_id(db, isp_id, include_dns=True)

    if not isp:
        raise HTTPException(status_code=404, detail="ISP not found")

    return isp


@router.get("/dns", response_model=list[DNSServerResponse])
async def get_dns_servers(
    isp_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
) -> list[DNSServerResponse]:
    """Get DNS servers, optionally filtered by ISP."""
    if isp_id:
        servers = await ISPService.get_dns_servers_by_isp(db, isp_id)
    else:
        # Get all active DNS servers
        from sqlalchemy import select

        from src.models.dns import DNSServer

        result = await db.execute(
            select(DNSServer).where(DNSServer.is_active == True).order_by(DNSServer.priority)
        )
        servers = list(result.scalars().all())

    return servers


@router.post("/resolve", response_model=DNSResolveResponse)
async def resolve_domain(
    request: DNSResolveRequest,
    req: Request,
    db: AsyncSession = Depends(get_db),
) -> DNSResolveResponse:
    """Resolve domain using specified DNS server."""
    # Perform DNS resolution
    result = await DNSService.resolve_domain(
        domain=request.domain,
        dns_server=request.dns_server,
        record_type=request.record_type,
    )

    # Log query
    client_ip = req.client.host if req.client else None
    log_entry = QueryLog(
        client_ip=client_ip,
        domain=request.domain,
        dns_server=result["dns_server"],
        response_time_ms=result["response_time_ms"],
        success=result["success"],
        error_message=result["error_message"],
    )
    db.add(log_entry)
    await db.commit()

    return DNSResolveResponse(**result)


@router.get("/resolve/examples", response_model=list[DNSCommandExample])
async def get_command_examples(
    domain: str = "google.com",
    dns_server: str = "8.8.8.8",
) -> list[DNSCommandExample]:
    """Get DNS query command examples for different platforms."""
    examples = DNSService.generate_command_examples(domain, dns_server)
    return [DNSCommandExample(**example) for example in examples]


@router.post("/detect-isp", response_model=ISPDetectionResponse)
async def detect_isp(
    request: ISPDetectionRequest,
    req: Request,
    db: AsyncSession = Depends(get_db),
) -> ISPDetectionResponse:
    """Detect ISP from IP address using ASN lookup."""
    # Use provided IP or client IP
    ip_address = request.ip_address or (req.client.host if req.client else None)

    if not ip_address:
        raise HTTPException(status_code=400, detail="IP address is required")

    # Detect ISP
    result = await ISPService.detect_isp_from_ip(db, ip_address)

    if not result:
        return ISPDetectionResponse(
            ip_address=ip_address,
            detected=False,
        )

    return ISPDetectionResponse(**result)
