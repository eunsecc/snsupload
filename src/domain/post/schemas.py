"""Post 도메인 스키마"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Platform(str, Enum):
    """SNS 플랫폼"""

    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"


class PostCreate(BaseModel):
    """포스트 생성 요청"""

    video_id: int = Field(..., description="연결된 영상 ID")
    script_id: Optional[int] = Field(None, description="연결된 스크립트 ID")
    platform: Platform = Field(..., description="SNS 플랫폼")
    content: str = Field(..., min_length=1, description="포스트 바디글 내용")
    hashtags: list[str] = Field(default_factory=list, description="해시태그 리스트")


class PostUpdate(BaseModel):
    """포스트 업데이트 요청"""

    content: Optional[str] = Field(None, min_length=1, description="포스트 바디글 내용")
    hashtags: Optional[list[str]] = Field(None, description="해시태그 리스트")


class PostResponse(BaseModel):
    """포스트 응답"""

    id: int = Field(..., description="포스트 ID")
    video_id: int = Field(..., description="연결된 영상 ID")
    script_id: Optional[int] = Field(None, description="연결된 스크립트 ID")
    platform: Platform = Field(..., description="SNS 플랫폼")
    content: str = Field(..., description="포스트 바디글 내용")
    hashtags: list[str] = Field(default_factory=list, description="해시태그 리스트")
    created_at: datetime = Field(..., description="생성 시각")
    updated_at: datetime = Field(..., description="수정 시각")

    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    """포스트 목록 응답"""

    total: int = Field(..., description="전체 포스트 수")
    posts: list[PostResponse] = Field(default_factory=list, description="포스트 목록")


class PostGenerateRequest(BaseModel):
    """AI 포스트 생성 요청"""

    video_id: int = Field(..., description="영상 ID")
    script_id: int = Field(..., description="스크립트 ID")
    platform: Platform = Field(..., description="SNS 플랫폼")
    generate_hashtags: bool = Field(True, description="해시태그 자동 생성 여부")
    hashtag_count: int = Field(10, ge=1, le=30, description="생성할 해시태그 개수")
