from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status

from src.api.deps import VideoServiceDep
from src.domain.video.schemas import (
    VideoCreate,
    VideoListResponse,
    VideoResponse,
    VideoStatus,
    VideoUpdate,
)

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=VideoResponse)
async def create_video(
    service: VideoServiceDep,
    title: Annotated[str, Form()],
    video_file: Annotated[UploadFile, File()],
    description: Annotated[Optional[str], Form()] = None,
    tags: Annotated[Optional[str], Form()] = None,
    thumbnail_file: Annotated[Optional[UploadFile], File()] = None,
) -> VideoResponse:
    """
    영상 업로드 및 생성

    Args:
        title: 영상 제목
        video_file: 영상 파일
        description: 영상 설명 (선택)
        tags: 태그 (쉼표로 구분, 선택)
        thumbnail_file: 썸네일 파일 (선택)
        service: Video Service

    Returns:
        생성된 영상 정보
    """
    # tags 파싱 (쉼표로 구분된 문자열 -> 리스트)
    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    video_data = VideoCreate(title=title, description=description, tags=tag_list)

    return await service.create_video_with_file(video_data, video_file, thumbnail_file)


@router.get("/", response_model=VideoListResponse)
async def list_videos(
    service: VideoServiceDep,
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    status: Optional[VideoStatus] = Query(None, description="상태 필터"),
) -> VideoListResponse:
    """
    영상 목록 조회

    Args:
        skip: 페이징 - 건너뛸 개수
        limit: 페이징 - 조회할 개수
        status: 상태 필터 (선택)
        service: Video Service

    Returns:
        영상 목록
    """
    return await service.list_videos(skip, limit, status)


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    service: VideoServiceDep,
    video_id: int,
) -> VideoResponse:
    """
    영상 상세 조회

    Args:
        video_id: 영상 ID
        service: Video Service

    Returns:
        영상 정보
    """
    return await service.get_video_by_id(video_id)


@router.patch("/{video_id}", response_model=VideoResponse)
async def update_video(
    service: VideoServiceDep,
    video_id: int,
    update_data: VideoUpdate,
) -> VideoResponse:
    """
    영상 메타데이터 업데이트

    Args:
        video_id: 영상 ID
        update_data: 업데이트할 데이터
        service: Video Service

    Returns:
        업데이트된 영상 정보
    """
    return await service.update_video(video_id, update_data)


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(
    service: VideoServiceDep,
    video_id: int,
) -> None:
    """
    영상 삭제

    Args:
        video_id: 영상 ID
        service: Video Service
    """
    await service.delete_video(video_id)
