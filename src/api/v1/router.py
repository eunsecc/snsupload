from fastapi import APIRouter

from src.api.v1.endpoints import videos

api_router = APIRouter()

# Video API 등록
api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
