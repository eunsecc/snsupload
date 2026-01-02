from typing import Annotated

from fastapi import Depends

from src.domain.post.repository import PostRepository
from src.domain.post.service import PostService
from src.domain.script.repository import ScriptRepository
from src.domain.script.service import ScriptService
from src.domain.video.repository import VideoRepository
from src.domain.video.service import VideoService
from src.integrations.openai_service import OpenAIService


# Repository Dependencies
def get_video_repository() -> VideoRepository:
    """Video Repository 의존성"""
    return VideoRepository()


def get_script_repository() -> ScriptRepository:
    """Script Repository 의존성"""
    return ScriptRepository()


def get_post_repository() -> PostRepository:
    """Post Repository 의존성"""
    return PostRepository()


# Integration Dependencies
def get_openai_service() -> OpenAIService:
    """OpenAI Service 의존성"""
    return OpenAIService()


# Service Dependencies
def get_video_service(
    repository: Annotated[VideoRepository, Depends(get_video_repository)],
) -> VideoService:
    """Video Service 의존성"""
    return VideoService(repository)


def get_script_service(
    repository: Annotated[ScriptRepository, Depends(get_script_repository)],
) -> ScriptService:
    """Script Service 의존성"""
    return ScriptService(repository)


def get_post_service(
    repository: Annotated[PostRepository, Depends(get_post_repository)],
    script_repository: Annotated[ScriptRepository, Depends(get_script_repository)],
    openai_service: Annotated[OpenAIService, Depends(get_openai_service)],
) -> PostService:
    """Post Service 의존성"""
    return PostService(repository, script_repository, openai_service)


# Type Aliases
VideoServiceDep = Annotated[VideoService, Depends(get_video_service)]
ScriptServiceDep = Annotated[ScriptService, Depends(get_script_service)]
PostServiceDep = Annotated[PostService, Depends(get_post_service)]
