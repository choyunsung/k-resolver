# 🌐 K-Resolver

**통신사별 네임서버 조회 서비스** - Korean ISP DNS Resolver Service

빠르고 정확한 한국 통신사별 DNS 서버 정보 제공 및 실시간 DNS 쿼리 테스트 서비스

## ✨ 주요 기능

- 🏢 **통신사별 DNS 정보**: KT, SK브로드밴드, LG U+, SK텔레콤 등 주요 통신사의 DNS 서버 정보 제공
- 🔍 **자동 ISP 감지**: IP 주소의 ASN을 기반으로 통신사 자동 감지
- ⚡ **실시간 DNS 테스트**: 도메인 조회 및 응답 시간 측정
- 📋 **명령어 생성**: dig, nslookup 등의 테스트 명령어 자동 생성
- 🌍 **Public DNS 포함**: Google DNS, Cloudflare, Quad9 등 글로벌 DNS 서비스 정보
- 📊 **DoH/DoT 지원**: DNS-over-HTTPS 및 DNS-over-TLS 엔드포인트 정보

## 🚀 빠른 시작

### 필수 요구사항

- Python 3.14+
- Podman 또는 Docker
- Docker Compose / Podman Compose

### 설치 및 실행

1. **레포지토리 클론**

```bash
git clone https://github.com/yourusername/k-resolver.git
cd k-resolver
```

2. **환경 변수 설정**

```bash
cp .env.example .env
# .env 파일을 편집하여 필요한 설정 변경
```

3. **Podman Compose로 실행**

```bash
# 빌드 및 실행
podman-compose up --build

# 또는 백그라운드 실행
podman-compose up -d --build
```

4. **데이터베이스 마이그레이션**

```bash
# 컨테이너 내부에서 실행
podman-compose exec api bash
alembic upgrade head
python scripts/seed_data.py
```

5. **서비스 접속**

- API 문서: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 메인 페이지: http://localhost:8000

## 📡 API 엔드포인트

### 통신사 정보

- `GET /api/isps` - 모든 통신사 및 DNS 서버 목록
- `GET /api/isps/{isp_id}` - 특정 통신사 정보
- `GET /api/dns?isp_id={id}` - 특정 통신사의 DNS 서버 목록

### DNS 쿼리

- `POST /api/resolve` - 도메인 DNS 쿼리 수행

```json
{
  "domain": "google.com",
  "dns_server": "8.8.8.8",
  "record_type": "A"
}
```

- `GET /api/resolve/examples` - DNS 쿼리 명령어 예시

### ISP 감지

- `POST /api/detect-isp` - IP 주소로 통신사 감지

```json
{
  "ip_address": "1.2.3.4"
}
```

### 헬스체크

- `GET /health` - 서비스 상태 확인

## 🏗️ 프로젝트 구조

```
k-resolver/
├── src/
│   ├── api/              # API 라우트 및 스키마
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── core/             # 코어 설정
│   │   ├── config.py
│   │   └── database.py
│   ├── models/           # 데이터베이스 모델
│   │   └── dns.py
│   ├── services/         # 비즈니스 로직
│   │   ├── dns_service.py
│   │   └── isp_service.py
│   └── main.py           # FastAPI 애플리케이션
├── alembic/              # 데이터베이스 마이그레이션
├── scripts/              # 유틸리티 스크립트
│   ├── init-db.sql
│   └── seed_data.py
├── tests/                # 테스트
├── Containerfile         # Podman 이미지 정의
├── compose.yml           # Docker/Podman Compose 설정
└── pyproject.toml        # 프로젝트 설정
```

## 🛠️ 개발 가이드

### 로컬 개발 환경 설정

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -e ".[dev]"

# 데이터베이스 설정 (PostgreSQL 실행 중이어야 함)
alembic upgrade head
python scripts/seed_data.py
```

### 개발 서버 실행

```bash
uvicorn src.main:app --reload --port 8000
```

### 테스트 실행

```bash
pytest
pytest --cov=src  # 커버리지 포함
```

### 코드 품질 검사

```bash
# Linting
ruff check src/

# Formatting
ruff format src/

# Type checking
mypy src/
```

## 🐳 프로덕션 배포

### Podman으로 배포

```bash
# 이미지 빌드
podman build -t k-resolver:latest -f Containerfile .

# 컨테이너 실행
podman run -d \
  --name k-resolver \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  k-resolver:latest
```

### Docker Compose로 배포

```bash
# 프로덕션 모드로 실행
ENV=production docker-compose up -d
```

## 📊 데이터베이스 스키마

### 주요 테이블

- **isps**: 통신사 정보
- **dns_servers**: DNS 서버 정보
- **asn_mappings**: ASN to ISP 매핑
- **query_logs**: DNS 쿼리 로그 (통계용)

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

This project is licensed under the MIT License.

## 🙏 크레딧

- DNS 조회: [dnspython](https://github.com/rthalley/dnspython)
- ASN 조회: [BGPView API](https://bgpview.io/)
- 프레임워크: [FastAPI](https://fastapi.tiangolo.com/)

## 📧 문의

프로젝트 관련 문의사항은 Issues를 통해 남겨주세요.
