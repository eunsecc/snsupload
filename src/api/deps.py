from typing import Annotated

from fastapi import Depends

from src.domain.post.repository import PostRepository
from src.domain.post.service import PostService
from src.domain.script.repository import ScriptRepository
from src.domain.script.service import ScriptService
from src.domain.upload_job.repository import UploadJobRepository
from src.domain.upload_job.service import UploadJobService
from src.domain.video.repository import VideoRepository
from src.domain.video.service import VideoService
from src.integrations.instagram_service import InstagramService
from src.integrations.openai_service import OpenAIService
from src.integrations.youtube_service import YouTubeService


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


def get_upload_job_repository() -> UploadJobRepository:
    """Upload Job Repository 의존성"""
    return UploadJobRepository()


# Integration Dependencies
def get_openai_service() -> OpenAIService:
    """OpenAI Service 의존성"""
    return OpenAIService()


def get_youtube_service() -> YouTubeService:
    """YouTube Service 의존성"""
    return YouTubeService()


def get_instagram_service() -> InstagramService:
    """Instagram Service 의존성"""
    return InstagramService()


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


def get_upload_job_service(
    repository: Annotated[UploadJobRepository, Depends(get_upload_job_repository)],
    video_repository: Annotated[VideoRepository, Depends(get_video_repository)],
    post_repository: Annotated[PostRepository, Depends(get_post_repository)],
    youtube_service: Annotated[YouTubeService, Depends(get_youtube_service)],
    instagram_service: Annotated[InstagramService, Depends(get_instagram_service)],
) -> UploadJobService:
    """Upload Job Service 의존성"""
    return UploadJobService(
        repository, video_repository, post_repository, youtube_service, instagram_service
    )


# Type Aliases
VideoServiceDep = Annotated[VideoService, Depends(get_video_service)]
ScriptServiceDep = Annotated[ScriptService, Depends(get_script_service)]
PostServiceDep = Annotated[PostService, Depends(get_post_service)]
UploadJobServiceDep = Annotated[UploadJobService, Depends(get_upload_job_service)]
