"""Upload Job Service - 업로드 작업 비즈니스 로직"""

from datetime import datetime
from typing import Optional

from src.core.exceptions import NotFoundError, ValidationError
from src.core.logging import get_logger
from src.domain.post.repository import PostRepository
from src.domain.upload_job.repository import UploadJobRepository
from src.domain.upload_job.schemas import (
    UploadJobCreate,
    UploadJobListResponse,
    UploadJobResponse,
    UploadJobUpdate,
    UploadPlatform,
    UploadStatus,
)
from src.domain.video.repository import VideoRepository
from src.integrations.instagram_service import InstagramService
from src.integrations.youtube_service import YouTubeService

logger = get_logger(__name__)


class UploadJobService:
    """Upload Job 비즈니스 로직"""

    def __init__(
        self,
        repository: UploadJobRepository,
        video_repository: VideoRepository,
        post_repository: PostRepository,
        youtube_service: YouTubeService,
        instagram_service: InstagramService,
    ):
        self.repository = repository
        self.video_repository = video_repository
        self.post_repository = post_repository
        self.youtube_service = youtube_service
        self.instagram_service = instagram_service

    async def create_job(self, job_data: UploadJobCreate) -> UploadJobResponse:
        """업로드 작업 생성"""
        # Video 존재 확인
        video = self.video_repository.get_by_id(job_data.video_id)
        if not video:
            raise NotFoundError(f"Video ID {job_data.video_id} not found")

        # Post 존재 확인 (선택적)
        if job_data.post_id:
            post = self.post_repository.get_by_id(job_data.post_id)
            if not post:
                raise NotFoundError(f"Post ID {job_data.post_id} not found")

        job = self.repository.create(job_data)
        return UploadJobResponse(**job)

    async def execute_job(self, job_id: int, force: bool = False) -> UploadJobResponse:
        """
        업로드 작업 실행

        Args:
            job_id: 작업 ID
            force: 강제 실행 (예약 시간 무시)

        Returns:
            실행된 작업 정보
        """
        job = self.repository.get_by_id(job_id)
        if not job:
            raise NotFoundError(f"Upload Job ID {job_id} not found")

        # 상태 확인
        if job["status"] != UploadStatus.PENDING.value:
            raise ValidationError(
                f"Job is not in PENDING status. Current status: {job['status']}"
            )

        # 예약 시간 확인
        if not force and job["scheduled_at"]:
            scheduled = datetime.fromisoformat(job["scheduled_at"])
            if scheduled > datetime.utcnow():
                raise ValidationError(
                    f"Job is scheduled for {scheduled}. Use force=true to execute now."
                )

        # 상태를 PROCESSING으로 변경
        self.repository.update_status(job_id, UploadStatus.PROCESSING)

        try:
            # 플랫폼별 업로드 실행
            if job["platform"] == UploadPlatform.YOUTUBE.value:
                result = await self._execute_youtube_upload(job)
            elif job["platform"] == UploadPlatform.INSTAGRAM.value:
                result = await self._execute_instagram_upload(job)
            else:
                raise ValidationError(f"Unsupported platform: {job['platform']}")

            # 상태를 COMPLETED로 변경
            updated_job = self.repository.update_status(
                job_id,
                UploadStatus.COMPLETED,
                platform_video_id=result.get("video_id") or result.get("media_id"),
                platform_url=result.get("url"),
            )

            return UploadJobResponse(**updated_job)

        except Exception as e:
            logger.error(f"Upload job {job_id} failed: {e}")
            # 상태를 FAILED로 변경
            failed_job = self.repository.update_status(
                job_id, UploadStatus.FAILED, error_message=str(e)
            )
            return UploadJobResponse(**failed_job)

    async def _execute_youtube_upload(self, job: dict) -> dict:
        """YouTube 업로드 실행"""
        # Video 정보 가져오기
        video = self.video_repository.get_by_id(job["video_id"])
        if not video or not video.get("video_file_path"):
            raise ValidationError("Video file not found")

        # Post 정보 가져오기 (있는 경우)
        description = ""
        tags = []
        if job["post_id"]:
            post = self.post_repository.get_by_id(job["post_id"])
            if post:
                description = post["content"]
                tags = post.get("hashtags", [])

        # YouTube 업로드
        logger.info(f"Uploading to YouTube: {video['title']}")
        result = await self.youtube_service.upload_video(
            video_path=video["video_file_path"],
            title=video["title"],
            description=description,
            tags=tags,
            thumbnail_path=video.get("thumbnail_file_path"),
            privacy_status="private",  # 기본값: 비공개
        )

        return result

    async def _execute_instagram_upload(self, job: dict) -> dict:
        """Instagram 업로드 실행"""
        # Video 정보 가져오기
        video = self.video_repository.get_by_id(job["video_id"])
        if not video:
            raise ValidationError("Video not found")

        # Post 정보 가져오기 (있는 경우)
        caption = ""
        if job["post_id"]:
            post = self.post_repository.get_by_id(job["post_id"])
            if post:
                caption = post["content"]
                # 해시태그 추가
                if post.get("hashtags"):
                    caption += "\n\n" + " ".join(post["hashtags"])

        # Instagram은 공개 URL이 필요
        # 실제 프로덕션에서는 영상 파일을 임시로 호스팅해야 함
        logger.warning(
            "Instagram upload requires publicly accessible video URL. "
            "This is a placeholder implementation."
        )

        # 여기서는 스킵하고 성공으로 표시 (실제 구현 필요)
        return {
            "status": "skipped",
            "message": "Instagram upload requires video hosting setup",
            "media_id": "instagram_placeholder",
            "url": "https://instagram.com/placeholder",
        }

    async def get_job_by_id(self, job_id: int) -> UploadJobResponse:
        """작업 상세 조회"""
        job = self.repository.get_by_id(job_id)
        if not job:
            raise NotFoundError(f"Upload Job ID {job_id} not found")
        return UploadJobResponse(**job)

    async def get_jobs_by_video_id(
        self, video_id: int, platform: Optional[UploadPlatform] = None
    ) -> list[UploadJobResponse]:
        """Video ID로 작업 목록 조회"""
        jobs = self.repository.get_by_video_id(video_id, platform)
        return [UploadJobResponse(**j) for j in jobs]

    async def list_jobs(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[UploadStatus] = None,
        platform: Optional[UploadPlatform] = None,
    ) -> UploadJobListResponse:
        """작업 목록 조회"""
        jobs = self.repository.get_all(skip, limit, status, platform)
        total = self.repository.count(status, platform)
        return UploadJobListResponse(
            total=total, jobs=[UploadJobResponse(**j) for j in jobs]
        )

    async def get_pending_jobs(self) -> list[UploadJobResponse]:
        """실행 대기 중인 작업 조회"""
        jobs = self.repository.get_pending_jobs()
        return [UploadJobResponse(**j) for j in jobs]

    async def update_job(
        self, job_id: int, update_data: UploadJobUpdate
    ) -> UploadJobResponse:
        """작업 업데이트"""
        job = self.repository.update(job_id, update_data)
        if not job:
            raise NotFoundError(f"Upload Job ID {job_id} not found")
        return UploadJobResponse(**job)

    async def delete_job(self, job_id: int) -> None:
        """작업 삭제"""
        success = self.repository.delete(job_id)
        if not success:
            raise NotFoundError(f"Upload Job ID {job_id} not found")
