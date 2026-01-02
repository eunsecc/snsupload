import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.config import settings
from src.domain.video.schemas import VideoCreate, VideoStatus, VideoUpdate


class VideoRepository:
    """Video JSON Repository"""

    def __init__(self):
        self.data_file = settings.data_dir / "videos.json"
        self._ensure_data_file()

    def _ensure_data_file(self) -> None:
        """데이터 파일 초기화"""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self.data_file.write_text("[]", encoding="utf-8")

    def _load(self) -> list[dict]:
        """JSON 파일 로드"""
        return json.loads(self.data_file.read_text(encoding="utf-8"))

    def _save(self, data: list[dict]) -> None:
        """JSON 파일 저장"""
        self.data_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def create(self, video: VideoCreate) -> dict:
        """새 영상 생성"""
        videos = self._load()
        new_id = max((v["id"] for v in videos), default=0) + 1
        now = datetime.utcnow().isoformat()

        new_video = {
            "id": new_id,
            **video.model_dump(),
            "status": VideoStatus.UPLOADED.value,
            "video_file_path": None,
            "thumbnail_file_path": None,
            "created_at": now,
            "updated_at": now,
        }
        videos.append(new_video)
        self._save(videos)
        return new_video

    def get_by_id(self, video_id: int) -> Optional[dict]:
        """ID로 영상 조회"""
        videos = self._load()
        return next((v for v in videos if v["id"] == video_id), None)

    def get_all(
        self, skip: int = 0, limit: int = 100, status: Optional[VideoStatus] = None
    ) -> list[dict]:
        """영상 목록 조회"""
        videos = self._load()

        # 상태 필터링
        if status:
            videos = [v for v in videos if v["status"] == status.value]

        # 페이징
        return videos[skip : skip + limit]

    def count(self, status: Optional[VideoStatus] = None) -> int:
        """영상 개수 조회"""
        videos = self._load()
        if status:
            videos = [v for v in videos if v["status"] == status.value]
        return len(videos)

    def update(self, video_id: int, update_data: VideoUpdate) -> Optional[dict]:
        """영상 업데이트"""
        videos = self._load()
        for i, v in enumerate(videos):
            if v["id"] == video_id:
                # None이 아닌 값만 업데이트
                update_dict = update_data.model_dump(exclude_unset=True)
                videos[i] = {**v, **update_dict, "updated_at": datetime.utcnow().isoformat()}
                self._save(videos)
                return videos[i]
        return None

    def update_file_paths(
        self,
        video_id: int,
        video_path: Optional[str] = None,
        thumbnail_path: Optional[str] = None,
    ) -> Optional[dict]:
        """파일 경로 업데이트"""
        videos = self._load()
        for i, v in enumerate(videos):
            if v["id"] == video_id:
                if video_path:
                    videos[i]["video_file_path"] = video_path
                if thumbnail_path:
                    videos[i]["thumbnail_file_path"] = thumbnail_path
                videos[i]["updated_at"] = datetime.utcnow().isoformat()
                self._save(videos)
                return videos[i]
        return None

    def update_status(self, video_id: int, status: VideoStatus) -> Optional[dict]:
        """상태 업데이트"""
        videos = self._load()
        for i, v in enumerate(videos):
            if v["id"] == video_id:
                videos[i]["status"] = status.value
                videos[i]["updated_at"] = datetime.utcnow().isoformat()
                self._save(videos)
                return videos[i]
        return None

    def delete(self, video_id: int) -> bool:
        """영상 삭제"""
        videos = self._load()
        filtered = [v for v in videos if v["id"] != video_id]
        if len(filtered) < len(videos):
            self._save(filtered)
            return True
        return False
