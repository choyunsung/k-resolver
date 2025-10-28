# Podman 이미지 사용 (docker.quetta-soft.com)
FROM docker.quetta-soft.com/python:3.14-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 설치 (DNS 조회 도구)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    dnsutils \
    iputils-ping \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사
COPY pyproject.toml ./

# pip 업그레이드 및 의존성 설치
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# 애플리케이션 코드 복사
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# 비루트 사용자 생성 및 전환
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# 포트 노출
EXPOSE 8000

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 애플리케이션 실행
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
