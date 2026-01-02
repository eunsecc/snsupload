"""YouTube Data API v3 통합 서비스"""

import os
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from src.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

# YouTube API 권한 범위
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


class YouTubeService:
    """YouTube Data API v3 서비스"""

    def __init__(self):
        self.credentials = None
        self.youtube = None
        self._authenticate()

    def _authenticate(self) -> None:
        """YouTube API 인증"""
        creds = None
        token_file = Path(settings.youtube_token_file)
        credentials_file = Path(settings.youtube_credentials_file)

        # 토큰 파일이 있으면 로드
        if token_file.exists():
            creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

        # 토큰이 없거나 유효하지 않으면 새로 생성
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing YouTube credentials")
                creds.refresh(Request())
            else:
                if not credentials_file.exists():
                    logger.warning(
                        f"YouTube credentials file not found: {credentials_file}"
                    )
                    logger.warning(
                        "YouTube upload will be skipped. Please add credentials file."
                    )
                    return

                logger.info("Starting OAuth flow for YouTube")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_file), SCOPES
                )
                creds = flow.run_local_server(port=0)

            # 토큰 저장
            token_file.parent.mkdir(parents=True, exist_ok=True)
            with open(token_file, "w") as token:
                token.write(creds.to_json())

        self.credentials = creds
        if creds:
            self.youtube = build("youtube", "v3", credentials=creds)
            logger.info("YouTube API authenticated successfully")

    async def upload_video(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: Optional[list[str]] = None,
        category_id: str = "22",  # 22 = People & Blogs
        privacy_status: str = "private",  # private, public, unlisted
        thumbnail_path: Optional[str] = None,
    ) -> dict:
        """
        YouTube에 영상 업로드

        Args:
            video_path: 영상 파일 경로
            title: 영상 제목
            description: 영상 설명
            tags: 태그 리스트
            category_id: 카테고리 ID
            privacy_status: 공개 설정
            thumbnail_path: 썸네일 파일 경로 (선택)

        Returns:
            업로드된 영상 정보 (video_id 포함)

        Raises:
            Exception: YouTube API 인증이 설정되지 않은 경우
        """
        if not self.youtube:
            raise Exception(
                "YouTube API not authenticated. Please configure credentials."
            )

        # 영상 메타데이터 설정
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags or [],
                "categoryId": category_id,
            },
            "status": {"privacyStatus": privacy_status},
        }

        # 영상 파일 업로드
        logger.info(f"Uploading video to YouTube: {title}")
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

        request = self.youtube.videos().insert(
            part="snippet,status", body=body, media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.info(
                    f"Upload progress: {int(status.progress() * 100)}% complete"
                )

        video_id = response["id"]
        logger.info(f"Video uploaded successfully. Video ID: {video_id}")

        # 썸네일 업로드 (선택적)
        if thumbnail_path and os.path.exists(thumbnail_path):
            await self.upload_thumbnail(video_id, thumbnail_path)

        return {
            "video_id": video_id,
            "title": response["snippet"]["title"],
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "privacy_status": response["status"]["privacyStatus"],
        }

    async def upload_thumbnail(self, video_id: str, thumbnail_path: str) -> None:
        """
        YouTube 영상 썸네일 업로드

        Args:
            video_id: YouTube 영상 ID
            thumbnail_path: 썸네일 파일 경로
        """
        if not self.youtube:
            raise Exception(
                "YouTube API not authenticated. Please configure credentials."
            )

        logger.info(f"Uploading thumbnail for video: {video_id}")
        media = MediaFileUpload(thumbnail_path, resumable=True)

        self.youtube.thumbnails().set(videoId=video_id, media_body=media).execute()

        logger.info(f"Thumbnail uploaded successfully for video: {video_id}")

    async def update_video(
        self,
        video_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[list[str]] = None,
        privacy_status: Optional[str] = None,
    ) -> dict:
        """
        YouTube 영상 메타데이터 업데이트

        Args:
            video_id: YouTube 영상 ID
            title: 영상 제목 (선택)
            description: 영상 설명 (선택)
            tags: 태그 리스트 (선택)
            privacy_status: 공개 설정 (선택)

        Returns:
            업데이트된 영상 정보
        """
        if not self.youtube:
            raise Exception(
                "YouTube API not authenticated. Please configure credentials."
            )

        # 현재 영상 정보 가져오기
        video = (
            self.youtube.videos()
            .list(part="snippet,status", id=video_id)
            .execute()["items"][0]
        )

        # 업데이트할 필드만 변경
        if title:
            video["snippet"]["title"] = title
        if description:
            video["snippet"]["description"] = description
        if tags:
            video["snippet"]["tags"] = tags
        if privacy_status:
            video["status"]["privacyStatus"] = privacy_status

        # 업데이트 요청
        logger.info(f"Updating video metadata: {video_id}")
        response = (
            self.youtube.videos().update(part="snippet,status", body=video).execute()
        )

        logger.info(f"Video metadata updated successfully: {video_id}")
        return {
            "video_id": response["id"],
            "title": response["snippet"]["title"],
            "privacy_status": response["status"]["privacyStatus"],
        }

    async def delete_video(self, video_id: str) -> None:
        """
        YouTube 영상 삭제

        Args:
            video_id: YouTube 영상 ID
        """
        if not self.youtube:
            raise Exception(
                "YouTube API not authenticated. Please configure credentials."
            )

        logger.info(f"Deleting video: {video_id}")
        self.youtube.videos().delete(id=video_id).execute()
        logger.info(f"Video deleted successfully: {video_id}")
