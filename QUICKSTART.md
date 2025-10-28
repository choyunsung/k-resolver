# 🚀 K-Resolver 빠른 시작 가이드

## 1분 안에 실행하기

### 1. 환경 확인

```bash
# Podman 또는 Docker 설치 확인
podman --version
# 또는
docker --version

# Podman Compose 또는 Docker Compose 설치 확인
podman-compose --version
# 또는
docker-compose --version
```

### 2. 프로젝트 클론

```bash
git clone <repository-url>
cd k-resolver
```

### 3. 환경 설정 (선택사항)

`.env` 파일은 이미 기본값으로 생성되어 있습니다. 필요시 수정:

```bash
# 데이터베이스 비밀번호 변경 등
nano .env
```

### 4. 서비스 시작

```bash
# Podman 사용
make build    # 또는: podman-compose build
make up       # 또는: podman-compose up -d

# Docker 사용
docker-compose build
docker-compose up -d
```

### 5. 데이터베이스 초기화

```bash
# 마이그레이션 실행
make migrate  # 또는: podman-compose exec api alembic upgrade head

# 초기 데이터 시드
make seed     # 또는: podman-compose exec api python scripts/seed_data.py
```

### 6. 서비스 접속

브라우저에서 다음 주소로 접속:

- 메인 페이지: http://localhost:8000
- API 문서 (Swagger): http://localhost:8000/docs
- API 문서 (ReDoc): http://localhost:8000/redoc

## 주요 명령어

```bash
# 로그 확인
make logs

# API 컨테이너 쉘 접속
make shell

# 데이터베이스 쉘 접속
make db-shell

# 테스트 실행
make test

# 서비스 중지
make down

# 전체 정리 (볼륨 포함)
make clean
```

## API 사용 예제

### 1. 모든 통신사 조회

```bash
curl http://localhost:8000/api/isps
```

### 2. DNS 쿼리 수행

```bash
curl -X POST http://localhost:8000/api/resolve \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "google.com",
    "dns_server": "168.126.63.1",
    "record_type": "A"
  }'
```

### 3. ISP 자동 감지

```bash
curl -X POST http://localhost:8000/api/detect-isp \
  -H "Content-Type: application/json" \
  -d '{
    "ip_address": "1.2.3.4"
  }'
```

### 4. DNS 테스트 명령어 생성

```bash
curl "http://localhost:8000/api/resolve/examples?domain=google.com&dns_server=8.8.8.8"
```

## 문제 해결

### 포트 충돌

기본 포트(8000, 5432)가 사용 중이면 `.env` 파일에서 변경:

```env
API_PORT=8001
POSTGRES_PORT=5433
```

### 컨테이너 재시작

```bash
make down
make up
```

### 로그 확인

```bash
# 전체 로그
make logs

# API만
podman-compose logs -f api

# DB만
podman-compose logs -f db
```

### 데이터베이스 초기화

```bash
# 모든 데이터 삭제 및 재생성
make clean
make up
make migrate
make seed
```

## 다음 단계

- README.md: 전체 문서
- CLAUDE.md: 개발자 가이드
- /docs: API 문서 (브라우저)
