from typing import Optional

from fastapi import UploadFile

from src.core.exceptions import NotFoundError
from src.core.file_utils import delete_video_files, save_thumbnail_file, save_video_file
from src.domain.video.repository import VideoRepository
from src.domain.video.schemas import (
    VideoCreate,
    VideoListResponse,
    VideoResponse,
    VideoStatus,
    VideoUpdate,
)


class VideoService:
    """Video 비즈니스 로직"""

    def __init__(self, repository: VideoRepository):
        self.repository = repository

    async def create_video_with_file(
        self,
        video_data: VideoCreate,
        video_file: UploadFile,
        thumbnail_file: Optional[UploadFile] = None,
    ) -> VideoResponse:
        """
        영상 생성 + 파일 저장

        Args:
            video_data: 영상 메타데이터
            video_file: 영상 파일
            thumbnail_file: 썸네일 파일 (선택)

        Returns:
            생성된 영상 정보
        """
        # 1. 메타데이터 저장
        video_dict = self.repository.create(video_data)
        video_id = video_dict["id"]

        try:
            # 2. 영상 파일 저장
            video_path = await save_video_file(video_id, video_file)

            # 3. 썸네일 파일 저장 (있는 경우)
            thumbnail_path = None
            if thumbnail_file:
                thumbnail_path = await save_thumbnail_file(video_id, thumbnail_file)

            # 4. 파일 경로 업데이트
            updated = self.repository.update_file_paths(
                video_id, video_path, thumbnail_path
            )

            # 5. 상태를 READY로 업데이트
            updated = self.repository.update_status(video_id, VideoStatus.READY)

            return VideoResponse(**updated)

        except Exception as e:
            # 에러 발생 시 FAILED 상태로 업데이트
            self.repository.update_status(video_id, VideoStatus.FAILED)
            raise e

    async def get_video_by_id(self, video_id: int) -> VideoResponse:
        """영상 조회"""
        video = self.repository.get_by_id(video_id)
        if not video:
            raise NotFoundError(f"Video with id {video_id} not found")
        return VideoResponse(**video)

    async def list_videos(
        self, skip: int = 0, limit: int = 100, status: Optional[VideoStatus] = None
    ) -> VideoListResponse:
        """영상 목록 조회"""
        videos = self.repository.get_all(skip, limit, status)
        total = self.repository.count(status)
        return VideoListResponse(
            total=total, videos=[VideoResponse(**v) for v in videos]
        )

    async def update_video(
        self, video_id: int, update_data: VideoUpdate
    ) -> VideoResponse:
        """영상 업데이트"""
        updated = self.repository.update(video_id, update_data)
        if not updated:
            raise NotFoundError(f"Video with id {video_id} not found")
        return VideoResponse(**updated)

    async def delete_video(self, video_id: int) -> bool:
        """영상 삭제"""
        # 파일 삭제
        delete_video_files(video_id)

        # DB 삭제
        success = self.repository.delete(video_id)
        if not success:
            raise NotFoundError(f"Video with id {video_id} not found")
        return True
