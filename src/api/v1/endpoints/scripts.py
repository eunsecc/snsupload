"""Script API 엔드포인트"""

from fastapi import APIRouter, Query, status
from typing import Annotated

from src.api.deps import ScriptServiceDep
from src.domain.script.schemas import (
    ScriptCreate,
    ScriptListResponse,
    ScriptResponse,
    ScriptUpdate,
)

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ScriptResponse)
async def create_script(
    service: ScriptServiceDep,
    script_data: ScriptCreate,
) -> ScriptResponse:
    """
    스크립트 생성

    Args:
        service: Script Service
        script_data: 스크립트 생성 데이터

    Returns:
        생성된 스크립트 정보
    """
    return await service.create_script(script_data)


@router.get("/", response_model=ScriptListResponse)
async def list_scripts(
    service: ScriptServiceDep,
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
) -> ScriptListResponse:
    """
    스크립트 목록 조회

    Args:
        service: Script Service
        skip: 페이징 - 건너뛸 개수
        limit: 페이징 - 조회할 개수

    Returns:
        스크립트 목록
    """
    return await service.list_scripts(skip, limit)


@router.get("/{script_id}", response_model=ScriptResponse)
async def get_script(
    service: ScriptServiceDep,
    script_id: int,
) -> ScriptResponse:
    """
    스크립트 상세 조회

    Args:
        service: Script Service
        script_id: 스크립트 ID

    Returns:
        스크립트 정보
    """
    return await service.get_script_by_id(script_id)


@router.get("/video/{video_id}", response_model=ScriptResponse)
async def get_script_by_video(
    service: ScriptServiceDep,
    video_id: int,
) -> ScriptResponse:
    """
    Video ID로 스크립트 조회

    Args:
        service: Script Service
        video_id: 영상 ID

    Returns:
        스크립트 정보
    """
    return await service.get_script_by_video_id(video_id)


@router.patch("/{script_id}", response_model=ScriptResponse)
async def update_script(
    service: ScriptServiceDep,
    script_id: int,
    update_data: ScriptUpdate,
) -> ScriptResponse:
    """
    스크립트 업데이트

    Args:
        service: Script Service
        script_id: 스크립트 ID
        update_data: 업데이트할 데이터

    Returns:
        업데이트된 스크립트 정보
    """
    return await service.update_script(script_id, update_data)


@router.delete("/{script_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_script(
    service: ScriptServiceDep,
    script_id: int,
) -> None:
    """
    스크립트 삭제

    Args:
        service: Script Service
        script_id: 스크립트 ID
    """
    await service.delete_script(script_id)
