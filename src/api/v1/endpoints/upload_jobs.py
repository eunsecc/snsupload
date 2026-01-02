"""Upload Job API 엔드포인트"""

from typing import Optional

from fastapi import APIRouter, Query, status

from src.api.deps import UploadJobServiceDep
from src.domain.upload_job.schemas import (
    UploadJobCreate,
    UploadJobExecuteRequest,
    UploadJobListResponse,
    UploadJobResponse,
    UploadJobUpdate,
    UploadPlatform,
    UploadStatus,
)

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UploadJobResponse)
async def create_upload_job(
    service: UploadJobServiceDep,
    job_data: UploadJobCreate,
) -> UploadJobResponse:
    """
    업로드 작업 생성

    Args:
        service: Upload Job Service
        job_data: 업로드 작업 생성 데이터

    Returns:
        생성된 업로드 작업 정보
    """
    return await service.create_job(job_data)


@router.post(
    "/{job_id}/execute",
    status_code=status.HTTP_200_OK,
    response_model=UploadJobResponse,
)
async def execute_upload_job(
    service: UploadJobServiceDep,
    job_id: int,
    force: bool = Query(False, description="강제 실행 (예약 시간 무시)"),
) -> UploadJobResponse:
    """
    업로드 작업 실행

    Args:
        service: Upload Job Service
        job_id: 작업 ID
        force: 강제 실행 여부

    Returns:
        실행된 작업 정보
    """
    return await service.execute_job(job_id, force)


@router.get("/pending", response_model=list[UploadJobResponse])
async def list_pending_jobs(
    service: UploadJobServiceDep,
) -> list[UploadJobResponse]:
    """
    실행 대기 중인 작업 조회

    Args:
        service: Upload Job Service

    Returns:
        대기 중인 작업 목록
    """
    return await service.get_pending_jobs()


@router.get("/", response_model=UploadJobListResponse)
async def list_upload_jobs(
    service: UploadJobServiceDep,
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    status: Optional[UploadStatus] = Query(None, description="상태 필터"),
    platform: Optional[UploadPlatform] = Query(None, description="플랫폼 필터"),
) -> UploadJobListResponse:
    """
    업로드 작업 목록 조회

    Args:
        service: Upload Job Service
        skip: 페이징 - 건너뛸 개수
        limit: 페이징 - 조회할 개수
        status: 상태 필터 (선택)
        platform: 플랫폼 필터 (선택)

    Returns:
        업로드 작업 목록
    """
    return await service.list_jobs(skip, limit, status, platform)


@router.get("/{job_id}", response_model=UploadJobResponse)
async def get_upload_job(
    service: UploadJobServiceDep,
    job_id: int,
) -> UploadJobResponse:
    """
    업로드 작업 상세 조회

    Args:
        service: Upload Job Service
        job_id: 작업 ID

    Returns:
        작업 정보
    """
    return await service.get_job_by_id(job_id)


@router.get("/video/{video_id}", response_model=list[UploadJobResponse])
async def get_jobs_by_video(
    service: UploadJobServiceDep,
    video_id: int,
    platform: Optional[UploadPlatform] = Query(None, description="플랫폼 필터"),
) -> list[UploadJobResponse]:
    """
    Video ID로 작업 목록 조회

    Args:
        service: Upload Job Service
        video_id: 영상 ID
        platform: 플랫폼 필터 (선택)

    Returns:
        작업 목록
    """
    return await service.get_jobs_by_video_id(video_id, platform)


@router.patch("/{job_id}", response_model=UploadJobResponse)
async def update_upload_job(
    service: UploadJobServiceDep,
    job_id: int,
    update_data: UploadJobUpdate,
) -> UploadJobResponse:
    """
    업로드 작업 업데이트

    Args:
        service: Upload Job Service
        job_id: 작업 ID
        update_data: 업데이트할 데이터

    Returns:
        업데이트된 작업 정보
    """
    return await service.update_job(job_id, update_data)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_upload_job(
    service: UploadJobServiceDep,
    job_id: int,
) -> None:
    """
    업로드 작업 삭제

    Args:
        service: Upload Job Service
        job_id: 작업 ID
    """
    await service.delete_job(job_id)
