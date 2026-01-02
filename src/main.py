from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.api.v1.router import api_router
from src.config import settings

app = FastAPI(
    title="Video Upload Automation",
    description="영상 콘텐츠 업로드 자동화 시스템",
    version="0.1.0",
    debug=settings.debug,
)

# API 라우터 등록
app.include_router(api_router, prefix="/api/v1")


# Health check 엔드포인트
@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "ok",
        "environment": settings.app_env,
        "debug": settings.debug,
    }


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Video Upload Automation API",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
