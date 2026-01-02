from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class VideoStatus(str, Enum):
    """영상 상태"""

    UPLOADED = "uploaded"  # 업로드됨
    PROCESSING = "processing"  # 처리중
    READY = "ready"  # 업로드 준비 완료
    PUBLISHED = "published"  # 발행됨
    FAILED = "failed"  # 실패


class VideoBase(BaseModel):
    """영상 기본 스키마"""

    title: str = Field(..., min_length=1, max_length=200, description="영상 제목")
    description: Optional[str] = Field(None, max_length=5000, description="영상 설명")
    tags: list[str] = Field(default_factory=list, description="태그 목록")
    duration_seconds: Optional[int] = Field(None, description="영상 길이(초)")
    file_size_bytes: Optional[int] = Field(None, description="파일 크기(바이트)")


class VideoCreate(VideoBase):
    """영상 생성 요청 스키마"""

    pass


class VideoUpdate(BaseModel):
    """영상 수정 요청 스키마"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    tags: Optional[list[str]] = None


class VideoResponse(VideoBase):
    """영상 응답 스키마"""

    id: int
    status: VideoStatus
    video_file_path: Optional[str] = None
    thumbnail_file_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VideoListResponse(BaseModel):
    """영상 목록 응답 스키마"""

    total: int
    videos: list[VideoResponse]
