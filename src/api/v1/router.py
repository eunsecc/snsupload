from fastapi import APIRouter

from src.api.v1.endpoints import posts, scripts, upload_jobs, videos

api_router = APIRouter()

# API 라우터 등록
api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(scripts.router, prefix="/scripts", tags=["scripts"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(upload_jobs.router, prefix="/upload-jobs", tags=["upload-jobs"])
