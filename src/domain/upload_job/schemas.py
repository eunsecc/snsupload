"""Upload Job 도메인 스키마"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class UploadPlatform(str, Enum):
    """업로드 플랫폼"""

    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"


class UploadStatus(str, Enum):
    """업로드 작업 상태"""

    PENDING = "pending"  # 대기 중
    PROCESSING = "processing"  # 처리 중
    COMPLETED = "completed"  # 완료
    FAILED = "failed"  # 실패


class UploadJobCreate(BaseModel):
    """업로드 작업 생성 요청"""

    video_id: int = Field(..., description="영상 ID")
    post_id: Optional[int] = Field(None, description="포스트 ID (선택)")
    platform: UploadPlatform = Field(..., description="업로드 플랫폼")
    scheduled_at: Optional[datetime] = Field(None, description="예약 업로드 시간 (선택)")


class UploadJobUpdate(BaseModel):
    """업로드 작업 업데이트 요청"""

    status: Optional[UploadStatus] = Field(None, description="작업 상태")
    scheduled_at: Optional[datetime] = Field(None, description="예약 업로드 시간")
    platform_video_id: Optional[str] = Field(
        None, description="플랫폼 영상 ID (YouTube/Instagram)"
    )
    error_message: Optional[str] = Field(None, description="에러 메시지")


class UploadJobResponse(BaseModel):
    """업로드 작업 응답"""

    id: int = Field(..., description="작업 ID")
    video_id: int = Field(..., description="영상 ID")
    post_id: Optional[int] = Field(None, description="포스트 ID")
    platform: UploadPlatform = Field(..., description="업로드 플랫폼")
    status: UploadStatus = Field(..., description="작업 상태")
    scheduled_at: Optional[datetime] = Field(None, description="예약 업로드 시간")
    uploaded_at: Optional[datetime] = Field(None, description="실제 업로드 완료 시간")
    platform_video_id: Optional[str] = Field(
        None, description="플랫폼 영상 ID (YouTube/Instagram)"
    )
    platform_url: Optional[str] = Field(None, description="플랫폼 영상 URL")
    error_message: Optional[str] = Field(None, description="에러 메시지")
    created_at: datetime = Field(..., description="생성 시각")
    updated_at: datetime = Field(..., description="수정 시각")

    model_config = {"from_attributes": True}


class UploadJobListResponse(BaseModel):
    """업로드 작업 목록 응답"""

    total: int = Field(..., description="전체 작업 수")
    jobs: list[UploadJobResponse] = Field(
        default_factory=list, description="업로드 작업 목록"
    )


class UploadJobExecuteRequest(BaseModel):
    """업로드 작업 실행 요청"""

    job_id: int = Field(..., description="작업 ID")
    force: bool = Field(False, description="강제 실행 여부 (예약 시간 무시)")
