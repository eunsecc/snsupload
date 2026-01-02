"""Post API 엔드포인트"""

from typing import Annotated, Optional

from fastapi import APIRouter, Query, status

from src.api.deps import PostServiceDep
from src.domain.post.schemas import (
    Platform,
    PostCreate,
    PostGenerateRequest,
    PostListResponse,
    PostResponse,
    PostUpdate,
)

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
async def create_post(
    service: PostServiceDep,
    post_data: PostCreate,
) -> PostResponse:
    """
    포스트 생성 (수동)

    Args:
        service: Post Service
        post_data: 포스트 생성 데이터

    Returns:
        생성된 포스트 정보
    """
    return await service.create_post(post_data)


@router.post(
    "/generate", status_code=status.HTTP_201_CREATED, response_model=PostResponse
)
async def generate_post(
    service: PostServiceDep,
    generate_request: PostGenerateRequest,
) -> PostResponse:
    """
    AI를 사용하여 포스트 생성

    Args:
        service: Post Service
        generate_request: AI 포스트 생성 요청

    Returns:
        생성된 포스트 정보
    """
    return await service.generate_post(generate_request)


@router.get("/", response_model=PostListResponse)
async def list_posts(
    service: PostServiceDep,
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    platform: Optional[Platform] = Query(None, description="플랫폼 필터"),
) -> PostListResponse:
    """
    포스트 목록 조회

    Args:
        service: Post Service
        skip: 페이징 - 건너뛸 개수
        limit: 페이징 - 조회할 개수
        platform: 플랫폼 필터 (선택)

    Returns:
        포스트 목록
    """
    return await service.list_posts(skip, limit, platform)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    service: PostServiceDep,
    post_id: int,
) -> PostResponse:
    """
    포스트 상세 조회

    Args:
        service: Post Service
        post_id: 포스트 ID

    Returns:
        포스트 정보
    """
    return await service.get_post_by_id(post_id)


@router.get("/video/{video_id}", response_model=list[PostResponse])
async def get_posts_by_video(
    service: PostServiceDep,
    video_id: int,
    platform: Optional[Platform] = Query(None, description="플랫폼 필터"),
) -> list[PostResponse]:
    """
    Video ID로 포스트 목록 조회

    Args:
        service: Post Service
        video_id: 영상 ID
        platform: 플랫폼 필터 (선택)

    Returns:
        포스트 목록
    """
    return await service.get_posts_by_video_id(video_id, platform)


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    service: PostServiceDep,
    post_id: int,
    update_data: PostUpdate,
) -> PostResponse:
    """
    포스트 업데이트

    Args:
        service: Post Service
        post_id: 포스트 ID
        update_data: 업데이트할 데이터

    Returns:
        업데이트된 포스트 정보
    """
    return await service.update_post(post_id, update_data)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    service: PostServiceDep,
    post_id: int,
) -> None:
    """
    포스트 삭제

    Args:
        service: Post Service
        post_id: 포스트 ID
    """
    await service.delete_post(post_id)
