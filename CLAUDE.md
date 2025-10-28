# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

K-Resolver는 한국 통신사별 네임서버(DNS) 정보를 제공하고, 실시간 DNS 쿼리 테스트를 수행하는 FastAPI 기반 웹 서비스입니다.

**핵심 기능:**
- 통신사별 DNS 서버 정보 제공 (KT, SK브로드밴드, LG U+, SK텔레콤 등)
- IP 주소 기반 ISP 자동 감지 (ASN lookup)
- 실시간 DNS 쿼리 수행 및 응답 시간 측정
- DNS 테스트 명령어 생성 (dig, nslookup)

## Technology Stack

- **Language**: Python 3.14+
- **Framework**: FastAPI
- **Database**: PostgreSQL 17
- **ORM**: SQLAlchemy 2.0 (async)
- **Migration**: Alembic
- **Containerization**: Podman (base image from docker.quetta-soft.com)
- **Orchestration**: Docker/Podman Compose

## Project Structure

```
src/
├── api/              # API 엔드포인트 및 Pydantic 스키마
│   ├── routes.py     # FastAPI 라우터 정의
│   └── schemas.py    # 요청/응답 스키마
├── core/             # 코어 설정 및 유틸리티
│   ├── config.py     # Pydantic Settings 기반 설정
│   └── database.py   # SQLAlchemy async 엔진 및 세션
├── models/           # SQLAlchemy ORM 모델
│   └── dns.py        # ISP, DNSServer, ASNMapping, QueryLog
├── services/         # 비즈니스 로직
│   ├── dns_service.py   # DNS 쿼리 및 해석
│   └── isp_service.py   # ISP 감지 및 관리
└── main.py           # FastAPI 앱 초기화 및 라이프사이클
```

## Common Commands

### 개발 환경 실행

```bash
# Podman Compose로 전체 스택 실행 (권장)
podman-compose up --build

# 백그라운드 실행
podman-compose up -d --build

# 로그 확인
podman-compose logs -f api
```

### 데이터베이스 마이그레이션

```bash
# 마이그레이션 생성
alembic revision --autogenerate -m "migration message"

# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 롤백
alembic downgrade -1
```

### 초기 데이터 시드

```bash
# 컨테이너 내부에서 실행
python scripts/seed_data.py
```

### 로컬 개발 서버

```bash
# 가상환경 활성화 후
uvicorn src.main:app --reload --port 8000 --log-level debug
```

### 테스트 실행

```bash
# 전체 테스트
pytest

# 커버리지 포함
pytest --cov=src --cov-report=html

# 특정 테스트 파일
pytest tests/test_api.py

# 특정 테스트 함수
pytest tests/test_api.py::test_get_isps -v
```

### 코드 품질

```bash
# Linting 및 포맷 체크
ruff check src/

# 자동 포맷팅
ruff format src/

# 타입 체킹
mypy src/
```

## Architecture Patterns

### Async/Await 패턴

- 모든 데이터베이스 작업은 async/await 사용
- SQLAlchemy의 AsyncSession 활용
- FastAPI 엔드포인트는 async def로 정의

```python
async def get_isps(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ISP))
    return result.scalars().all()
```

### Dependency Injection

- FastAPI의 Depends를 통한 의존성 주입
- 데이터베이스 세션은 `get_db()` 의존성 사용
- 서비스 계층은 정적 메서드로 구현하여 테스트 용이성 확보

```python
@router.get("/api/isps")
async def get_isps(db: AsyncSession = Depends(get_db)):
    return await ISPService.get_all_isps(db, include_dns=True)
```

### 계층 구조

1. **API Layer** (routes.py): HTTP 요청/응답 처리
2. **Service Layer** (services/): 비즈니스 로직
3. **Model Layer** (models/): 데이터베이스 모델
4. **Schema Layer** (schemas.py): 데이터 검증 및 직렬화

### 설정 관리

- Pydantic Settings를 통한 환경변수 관리
- `.env` 파일에서 설정 로드
- `src/core/config.py`에 중앙집중식 설정

## Database Models

### ISP (통신사)
- 통신사 기본 정보 (이름, 국가, 타입)
- DNS 서버와 1:N 관계
- ASN 매핑과 1:N 관계

### DNSServer (DNS 서버)
- IP 주소, 우선순위, 지역, 타입
- DoH/DoT URL 지원
- ISP와 N:1 관계

### ASNMapping (ASN 매핑)
- ASN 번호와 ISP 연결
- IP 주소로 ISP 자동 감지에 사용

### QueryLog (쿼리 로그)
- DNS 쿼리 이력 저장
- 통계 및 분석용

## External Dependencies

### DNS 조회
- `dnspython` 라이브러리 사용
- `dns.resolver.Resolver`로 DNS 쿼리 수행
- 타임아웃 및 에러 핸들링 필수

### ASN 조회
- BGPView API 사용 (https://api.bgpview.io)
- IP 주소 → ASN 변환
- 무료이며 API 키 불필요
- Alternative: MaxMind GeoIP2 (MAXMIND_LICENSE_KEY 설정 시)

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# API
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=info
CORS_ORIGINS=*

# Optional
MAXMIND_LICENSE_KEY=your_license_key
ENV=development
```

## Container Configuration

### Containerfile
- Base: `docker.quetta-soft.com/python:3.14-slim`
- 시스템 패키지: `dnsutils`, `iputils-ping`, `curl`
- 비루트 사용자로 실행 (appuser:1000)
- 헬스체크 포함

### compose.yml
- **db** 서비스: PostgreSQL 17 Alpine
- **api** 서비스: Python FastAPI 앱
- 볼륨: postgres_data (영구 데이터), logs (로그)
- 네트워크: 기본 브리지 네트워크

## Development Guidelines

### 새로운 API 엔드포인트 추가

1. `src/api/schemas.py`에 Pydantic 스키마 정의
2. `src/api/routes.py`에 엔드포인트 추가
3. 필요시 `src/services/`에 비즈니스 로직 추가
4. `tests/`에 테스트 작성

### 데이터베이스 모델 변경

1. `src/models/dns.py`에서 모델 수정
2. Alembic 마이그레이션 생성: `alembic revision --autogenerate -m "description"`
3. 마이그레이션 검토 및 수정 (alembic/versions/)
4. 마이그레이션 적용: `alembic upgrade head`
5. 필요시 seed 스크립트 업데이트

### 새로운 통신사 추가

1. `scripts/seed_data.py`에 통신사 정보 추가
2. DNS 서버 정보 및 ASN 정보 포함
3. 스크립트 재실행 또는 DB에 직접 INSERT

## Testing Strategy

- 단위 테스트: 서비스 로직 테스트
- 통합 테스트: API 엔드포인트 테스트
- pytest-asyncio 사용하여 async 테스트
- Mock을 사용하여 외부 API 호출 격리

## Performance Considerations

- 데이터베이스 쿼리는 `selectinload`로 N+1 문제 방지
- DNS 쿼리는 타임아웃 설정 (기본 5초)
- ASN 조회는 캐싱 고려 (향후 Redis 도입 가능)
- 쿼리 로그는 비동기로 저장

## Security

- SQL Injection: SQLAlchemy ORM 사용으로 방지
- CORS: 설정 가능한 origins
- 비루트 컨테이너 실행
- 민감 정보는 환경변수로 관리
- API 키는 `.env`에만 저장 (git ignore)

## Known Limitations

- ASN 조회는 외부 API 의존 (BGPView)
- MaxMind GeoIP2는 라이선스 키 필요
- DNS 쿼리는 시스템 네트워크 설정에 영향받음
- IPv6 지원은 제한적 (환경에 따라 다름)

## Future Enhancements

- Redis 캐싱 추가
- Prometheus metrics
- Rate limiting
- Admin 페이지
- 더 많은 통신사 지원
- Latency 측정 기능
- 지역별 DNS 서버 추천
