"""Post Repository - JSON 기반 CRUD"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.config import settings
from src.domain.post.schemas import Platform, PostCreate, PostUpdate


class PostRepository:
    """Post JSON Repository"""

    def __init__(self):
        self.data_file = settings.data_dir / "posts.json"
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

    def create(self, post: PostCreate) -> dict:
        """새 포스트 생성"""
        posts = self._load()
        new_id = max((p["id"] for p in posts), default=0) + 1
        now = datetime.utcnow().isoformat()

        new_post = {
            "id": new_id,
            **post.model_dump(),
            "platform": post.platform.value,
            "created_at": now,
            "updated_at": now,
        }
        posts.append(new_post)
        self._save(posts)
        return new_post

    def get_by_id(self, post_id: int) -> Optional[dict]:
        """ID로 포스트 조회"""
        posts = self._load()
        return next((p for p in posts if p["id"] == post_id), None)

    def get_by_video_id(
        self, video_id: int, platform: Optional[Platform] = None
    ) -> list[dict]:
        """Video ID로 포스트 조회"""
        posts = self._load()
        result = [p for p in posts if p["video_id"] == video_id]
        if platform:
            result = [p for p in result if p["platform"] == platform.value]
        return result

    def get_all(
        self, skip: int = 0, limit: int = 100, platform: Optional[Platform] = None
    ) -> list[dict]:
        """포스트 목록 조회"""
        posts = self._load()

        # 플랫폼 필터링
        if platform:
            posts = [p for p in posts if p["platform"] == platform.value]

        # 페이징
        return posts[skip : skip + limit]

    def count(self, platform: Optional[Platform] = None) -> int:
        """포스트 개수 조회"""
        posts = self._load()
        if platform:
            posts = [p for p in posts if p["platform"] == platform.value]
        return len(posts)

    def update(self, post_id: int, update_data: PostUpdate) -> Optional[dict]:
        """포스트 업데이트"""
        posts = self._load()
        for i, p in enumerate(posts):
            if p["id"] == post_id:
                # None이 아닌 값만 업데이트
                update_dict = update_data.model_dump(exclude_unset=True)
                posts[i] = {**p, **update_dict, "updated_at": datetime.utcnow().isoformat()}
                self._save(posts)
                return posts[i]
        return None

    def delete(self, post_id: int) -> bool:
        """포스트 삭제"""
        posts = self._load()
        filtered = [p for p in posts if p["id"] != post_id]
        if len(filtered) < len(posts):
            self._save(filtered)
            return True
        return False
