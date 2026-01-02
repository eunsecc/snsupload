"""Instagram Graph API 통합 서비스"""

import asyncio
import time
from typing import Optional

import httpx

from src.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class InstagramService:
    """Instagram Graph API 서비스"""

    def __init__(self):
        self.access_token = settings.instagram_access_token
        self.user_id = settings.instagram_user_id
        self.base_url = "https://graph.facebook.com/v18.0"

    async def upload_video(
        self,
        video_url: str,
        caption: str = "",
        thumbnail_url: Optional[str] = None,
        share_to_feed: bool = True,
    ) -> dict:
        """
        Instagram에 영상 업로드 (비디오 게시물)

        Instagram API는 2단계 프로세스:
        1. 컨테이너 생성 (영상 업로드)
        2. 컨테이너 게시

        Args:
            video_url: 공개 접근 가능한 영상 URL
            caption: 게시물 캡션
            thumbnail_url: 썸네일 URL (선택)
            share_to_feed: 피드에 공유 여부

        Returns:
            게시된 미디어 정보

        Note:
            video_url은 반드시 공개 접근 가능한 URL이어야 합니다.
            로컬 파일의 경우 별도의 호스팅 서버가 필요합니다.
        """
        if not self.access_token or not self.user_id:
            logger.warning(
                "Instagram credentials not configured. Upload will be skipped."
            )
            return {
                "status": "skipped",
                "message": "Instagram credentials not configured",
            }

        # 1단계: 비디오 컨테이너 생성
        logger.info("Creating Instagram video container")
        container_id = await self._create_video_container(
            video_url, caption, thumbnail_url, share_to_feed
        )

        # 2단계: 컨테이너 상태 확인 (업로드 완료 대기)
        logger.info(f"Waiting for video upload completion: {container_id}")
        await self._wait_for_upload_completion(container_id)

        # 3단계: 컨테이너 게시
        logger.info(f"Publishing Instagram video container: {container_id}")
        media_id = await self._publish_container(container_id)

        logger.info(f"Video published successfully. Media ID: {media_id}")
        return {
            "media_id": media_id,
            "status": "published",
            "url": f"https://www.instagram.com/p/{media_id}/",
        }

    async def upload_reel(
        self,
        video_url: str,
        caption: str = "",
        thumbnail_url: Optional[str] = None,
        share_to_feed: bool = True,
    ) -> dict:
        """
        Instagram Reels 업로드

        Args:
            video_url: 공개 접근 가능한 영상 URL
            caption: 게시물 캡션
            thumbnail_url: 썸네일 URL (선택)
            share_to_feed: 피드에 공유 여부

        Returns:
            게시된 릴스 정보
        """
        if not self.access_token or not self.user_id:
            logger.warning(
                "Instagram credentials not configured. Upload will be skipped."
            )
            return {
                "status": "skipped",
                "message": "Instagram credentials not configured",
            }

        # Reels 컨테이너 생성
        logger.info("Creating Instagram Reels container")
        container_id = await self._create_reels_container(
            video_url, caption, thumbnail_url, share_to_feed
        )

        # 컨테이너 상태 확인 (업로드 완료 대기)
        logger.info(f"Waiting for Reels upload completion: {container_id}")
        await self._wait_for_upload_completion(container_id)

        # 컨테이너 게시
        logger.info(f"Publishing Instagram Reels container: {container_id}")
        media_id = await self._publish_container(container_id)

        logger.info(f"Reels published successfully. Media ID: {media_id}")
        return {
            "media_id": media_id,
            "status": "published",
            "url": f"https://www.instagram.com/reel/{media_id}/",
        }

    async def _create_video_container(
        self,
        video_url: str,
        caption: str,
        thumbnail_url: Optional[str],
        share_to_feed: bool,
    ) -> str:
        """비디오 컨테이너 생성"""
        async with httpx.AsyncClient() as client:
            params = {
                "access_token": self.access_token,
                "media_type": "VIDEO",
                "video_url": video_url,
                "caption": caption,
            }

            if thumbnail_url:
                params["thumb_offset"] = thumbnail_url

            response = await client.post(
                f"{self.base_url}/{self.user_id}/media", params=params
            )
            response.raise_for_status()
            return response.json()["id"]

    async def _create_reels_container(
        self,
        video_url: str,
        caption: str,
        thumbnail_url: Optional[str],
        share_to_feed: bool,
    ) -> str:
        """Reels 컨테이너 생성"""
        async with httpx.AsyncClient() as client:
            params = {
                "access_token": self.access_token,
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption,
                "share_to_feed": share_to_feed,
            }

            if thumbnail_url:
                params["cover_url"] = thumbnail_url

            response = await client.post(
                f"{self.base_url}/{self.user_id}/media", params=params
            )
            response.raise_for_status()
            return response.json()["id"]

    async def _wait_for_upload_completion(
        self, container_id: str, max_wait: int = 300, check_interval: int = 5
    ) -> None:
        """
        컨테이너 업로드 완료 대기

        Args:
            container_id: 컨테이너 ID
            max_wait: 최대 대기 시간 (초)
            check_interval: 상태 확인 간격 (초)

        Raises:
            Exception: 업로드가 완료되지 않거나 실패한 경우
        """
        async with httpx.AsyncClient() as client:
            elapsed = 0
            while elapsed < max_wait:
                params = {
                    "access_token": self.access_token,
                    "fields": "status_code",
                }

                response = await client.get(
                    f"{self.base_url}/{container_id}", params=params
                )
                response.raise_for_status()
                status = response.json().get("status_code")

                if status == "FINISHED":
                    logger.info("Video upload completed")
                    return
                elif status == "ERROR":
                    raise Exception("Video upload failed")

                logger.info(f"Upload status: {status}. Waiting...")
                await asyncio.sleep(check_interval)
                elapsed += check_interval

            raise Exception(f"Upload timeout after {max_wait} seconds")

    async def _publish_container(self, container_id: str) -> str:
        """컨테이너 게시"""
        async with httpx.AsyncClient() as client:
            params = {
                "access_token": self.access_token,
                "creation_id": container_id,
            }

            response = await client.post(
                f"{self.base_url}/{self.user_id}/media_publish", params=params
            )
            response.raise_for_status()
            return response.json()["id"]

    async def delete_media(self, media_id: str) -> None:
        """
        Instagram 미디어 삭제

        Args:
            media_id: 미디어 ID
        """
        if not self.access_token:
            logger.warning("Instagram credentials not configured. Delete skipped.")
            return

        async with httpx.AsyncClient() as client:
            params = {"access_token": self.access_token}

            response = await client.delete(
                f"{self.base_url}/{media_id}", params=params
            )
            response.raise_for_status()
            logger.info(f"Media deleted successfully: {media_id}")
