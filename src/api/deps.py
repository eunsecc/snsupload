from typing import Annotated

from fastapi import Depends

from src.domain.video.repository import VideoRepository
from src.domain.video.service import VideoService


# Repository Dependencies
def get_video_repository() -> VideoRepository:
    """Video Repository 의존성"""
    return VideoRepository()


# Service Dependencies
def get_video_service(
    repository: Annotated[VideoRepository, Depends(get_video_repository)],
) -> VideoService:
    """Video Service 의존성"""
    return VideoService(repository)


# Type Aliases
VideoServiceDep = Annotated[VideoService, Depends(get_video_service)]
