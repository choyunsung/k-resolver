"""DNS and ISP database models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class ISP(Base):
    """통신사 정보."""

    __tablename__ = "isps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name_en: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(10), default="KR", nullable=False)
    isp_type: Mapped[str] = mapped_column(
        String(20), default="landline", nullable=False
    )  # landline, mobile, both
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    dns_servers: Mapped[list["DNSServer"]] = relationship(back_populates="isp", cascade="all, delete-orphan")
    asn_mappings: Mapped[list["ASNMapping"]] = relationship(back_populates="isp", cascade="all, delete-orphan")


class DNSServer(Base):
    """DNS 서버 정보."""

    __tablename__ = "dns_servers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    isp_id: Mapped[int] = mapped_column(Integer, ForeignKey("isps.id"), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)  # IPv4/IPv6
    priority: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 1=Primary, 2=Secondary
    region: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 지역 (서울, 부산 등)
    server_type: Mapped[str] = mapped_column(
        String(20), default="standard", nullable=False
    )  # standard, doh, dot
    doh_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # DNS-over-HTTPS URL
    dot_hostname: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # DNS-over-TLS hostname
    is_anycast: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    isp: Mapped["ISP"] = relationship(back_populates="dns_servers")


class ASNMapping(Base):
    """ASN to ISP 매핑."""

    __tablename__ = "asn_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    isp_id: Mapped[int] = mapped_column(Integer, ForeignKey("isps.id"), nullable=False)
    asn: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    as_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    isp: Mapped["ISP"] = relationship(back_populates="asn_mappings")


class QueryLog(Base):
    """DNS 쿼리 로그 (통계/분석용)."""

    __tablename__ = "query_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    client_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    dns_server: Mapped[str] = mapped_column(String(45), nullable=False)
    response_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, index=True
    )
