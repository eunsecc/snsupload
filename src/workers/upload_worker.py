"""Upload Worker - 백그라운드 업로드 작업 처리"""

import asyncio
import time
from typing import Optional

from src.api.deps import (
    get_instagram_service,
    get_post_repository,
    get_upload_job_repository,
    get_upload_job_service,
    get_video_repository,
    get_youtube_service,
)
from src.core.logging import get_logger

logger = get_logger(__name__)


class UploadWorker:
    """업로드 작업 백그라운드 Worker"""

    def __init__(self, check_interval: int = 60):
        """
        Args:
            check_interval: 작업 확인 간격 (초)
        """
        self.check_interval = check_interval
        self.running = False

        # 서비스 초기화
        self.upload_job_service = get_upload_job_service(
            repository=get_upload_job_repository(),
            video_repository=get_video_repository(),
            post_repository=get_post_repository(),
            youtube_service=get_youtube_service(),
            instagram_service=get_instagram_service(),
        )

    async def start(self):
        """Worker 시작"""
        self.running = True
        logger.info("Upload worker started")

        while self.running:
            try:
                await self._process_pending_jobs()
            except Exception as e:
                logger.error(f"Error in upload worker: {e}")

            # 다음 확인까지 대기
            await asyncio.sleep(self.check_interval)

        logger.info("Upload worker stopped")

    def stop(self):
        """Worker 중지"""
        self.running = False

    async def _process_pending_jobs(self):
        """대기 중인 작업 처리"""
        # 실행 대기 중인 작업 조회
        jobs = await self.upload_job_service.get_pending_jobs()

        if not jobs:
            logger.debug("No pending upload jobs")
            return

        logger.info(f"Found {len(jobs)} pending upload jobs")

        # 각 작업 실행
        for job in jobs:
            try:
                logger.info(f"Executing upload job {job.id}")
                await self.upload_job_service.execute_job(job.id, force=False)
                logger.info(f"Upload job {job.id} completed successfully")
            except Exception as e:
                logger.error(f"Failed to execute upload job {job.id}: {e}")


async def run_worker(check_interval: int = 60):
    """
    Worker 실행 함수

    Args:
        check_interval: 작업 확인 간격 (초)
    """
    worker = UploadWorker(check_interval)
    await worker.start()


if __name__ == "__main__":
    # Worker를 독립 프로세스로 실행
    logger.info("Starting upload worker as standalone process")
    asyncio.run(run_worker())
