"""Pydantic schemas for API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, IPvAnyAddress


# ISP Schemas
class ISPBase(BaseModel):
    """ISP base schema."""

    name: str = Field(..., description="통신사 이름")
    name_en: Optional[str] = Field(None, description="통신사 영문 이름")
    country: str = Field(default="KR", description="국가 코드")
    isp_type: str = Field(default="landline", description="통신사 타입 (landline, mobile, both)")
    is_active: bool = Field(default=True, description="활성화 여부")


class ISPCreate(ISPBase):
    """ISP creation schema."""

    pass


class ISPResponse(ISPBase):
    """ISP response schema."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# DNS Server Schemas
class DNSServerBase(BaseModel):
    """DNS server base schema."""

    ip_address: str = Field(..., description="DNS 서버 IP 주소")
    priority: int = Field(default=1, description="우선순위 (1=Primary, 2=Secondary)")
    region: Optional[str] = Field(None, description="지역")
    server_type: str = Field(default="standard", description="서버 타입 (standard, doh, dot)")
    doh_url: Optional[str] = Field(None, description="DNS-over-HTTPS URL")
    dot_hostname: Optional[str] = Field(None, description="DNS-over-TLS hostname")
    is_anycast: bool = Field(default=False, description="Anycast 여부")
    is_active: bool = Field(default=True, description="활성화 여부")
    notes: Optional[str] = Field(None, description="비고")


class DNSServerCreate(DNSServerBase):
    """DNS server creation schema."""

    isp_id: int = Field(..., description="통신사 ID")


class DNSServerResponse(DNSServerBase):
    """DNS server response schema."""

    id: int
    isp_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DNSServerWithISP(DNSServerResponse):
    """DNS server with ISP info."""

    isp: ISPResponse


# ISP with DNS Servers
class ISPWithDNS(ISPResponse):
    """ISP with DNS servers."""

    dns_servers: list[DNSServerResponse]


# DNS Query Schemas
class DNSResolveRequest(BaseModel):
    """DNS resolve request schema."""

    domain: str = Field(..., description="조회할 도메인", examples=["google.com"])
    dns_server: Optional[str] = Field(None, description="사용할 DNS 서버 (미지정시 시스템 기본값)")
    record_type: str = Field(default="A", description="레코드 타입 (A, AAAA, MX, NS, TXT 등)")


class DNSResolveResponse(BaseModel):
    """DNS resolve response schema."""

    domain: str
    dns_server: str
    record_type: str
    answers: list[str]
    response_time_ms: int
    success: bool
    error_message: Optional[str] = None


# Command Example Schema
class DNSCommandExample(BaseModel):
    """DNS 테스트 명령어 예시."""

    platform: str = Field(..., description="플랫폼 (windows, macos, linux)")
    command: str = Field(..., description="실행 명령어")
    description: str = Field(..., description="설명")


# ISP Detection Schema
class ISPDetectionRequest(BaseModel):
    """ISP detection request schema."""

    ip_address: Optional[str] = Field(None, description="IP 주소 (미지정시 요청자 IP 사용)")


class ISPDetectionResponse(BaseModel):
    """ISP detection response schema."""

    ip_address: str
    asn: Optional[int] = None
    as_name: Optional[str] = None
    isp: Optional[ISPResponse] = None
    detected: bool


# Health Check Schema
class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(default="healthy")
    version: str
    database: str = Field(default="connected")
