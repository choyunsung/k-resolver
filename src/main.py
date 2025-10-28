"""Main FastAPI application."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy import text

from src import __version__
from src.api.routes import router as api_router
from src.api.schemas import HealthResponse
from src.core.config import settings
from src.core.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan events."""
    # Startup
    print("🚀 Starting K-Resolver API...")
    print(f"📊 Environment: {settings.env}")
    print(f"🌐 CORS Origins: {settings.cors_origins}")

    # Test database connection
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

    yield

    # Shutdown
    print("👋 Shutting down K-Resolver API...")
    await engine.dispose()


app = FastAPI(
    title="K-Resolver",
    description="통신사별 네임서버 조회 서비스 - Korean ISP DNS Resolver Service",
    version=__version__,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)


@app.get("/", response_class=HTMLResponse)
async def root() -> str:
    """Root endpoint with simple HTML interface."""
    return """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>K-Resolver - 통신사별 네임서버 조회</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 800px;
            width: 100%;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .feature-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        .feature-card h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
        .feature-card p {
            color: #666;
            font-size: 0.9em;
        }
        .links {
            display: flex;
            gap: 15px;
            margin-top: 30px;
            flex-wrap: wrap;
        }
        .btn {
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s;
        }
        .btn-primary {
            background: #667eea;
            color: white;
        }
        .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .btn-secondary {
            background: white;
            color: #667eea;
            border: 2px solid #667eea;
        }
        .btn-secondary:hover {
            background: #667eea;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 K-Resolver</h1>
        <p class="subtitle">통신사별 네임서버 조회 서비스</p>

        <div class="feature-grid">
            <div class="feature-card">
                <h3>🏢 통신사별 DNS</h3>
                <p>KT, SKT, LG U+ 등 주요 통신사의 DNS 서버 정보를 제공합니다.</p>
            </div>
            <div class="feature-card">
                <h3>🔍 자동 감지</h3>
                <p>IP 주소의 ASN을 기반으로 통신사를 자동으로 감지합니다.</p>
            </div>
            <div class="feature-card">
                <h3>⚡ DNS 테스트</h3>
                <p>실시간으로 DNS 쿼리를 테스트하고 응답 시간을 측정합니다.</p>
            </div>
            <div class="feature-card">
                <h3>📋 명령어 생성</h3>
                <p>dig, nslookup 등의 테스트 명령어를 자동으로 생성합니다.</p>
            </div>
        </div>

        <div class="links">
            <a href="/docs" class="btn btn-primary">📚 API 문서</a>
            <a href="/redoc" class="btn btn-secondary">📖 ReDoc</a>
            <a href="/api/isps" class="btn btn-secondary">🏢 통신사 목록</a>
            <a href="/health" class="btn btn-secondary">💚 상태 확인</a>
        </div>
    </div>
</body>
</html>
    """


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        version=__version__,
        database=db_status,
    )
