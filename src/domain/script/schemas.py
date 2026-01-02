"""Script 도메인 스키마"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ScriptCreate(BaseModel):
    """스크립트 생성 요청"""

    video_id: int = Field(..., description="연결된 영상 ID")
    content: str = Field(..., min_length=1, description="스크립트 내용")


class ScriptUpdate(BaseModel):
    """스크립트 업데이트 요청"""

    content: Optional[str] = Field(None, min_length=1, description="스크립트 내용")


class ScriptResponse(BaseModel):
    """스크립트 응답"""

    id: int = Field(..., description="스크립트 ID")
    video_id: int = Field(..., description="연결된 영상 ID")
    content: str = Field(..., description="스크립트 내용")
    created_at: datetime = Field(..., description="생성 시각")
    updated_at: datetime = Field(..., description="수정 시각")

    model_config = {"from_attributes": True}


class ScriptListResponse(BaseModel):
    """스크립트 목록 응답"""

    total: int = Field(..., description="전체 스크립트 수")
    scripts: list[ScriptResponse] = Field(default_factory=list, description="스크립트 목록")
