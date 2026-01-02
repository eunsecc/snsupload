"""Script Repository - JSON 기반 CRUD"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.config import settings
from src.domain.script.schemas import ScriptCreate, ScriptUpdate


class ScriptRepository:
    """Script JSON Repository"""

    def __init__(self):
        self.data_file = settings.data_dir / "scripts.json"
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

    def create(self, script: ScriptCreate) -> dict:
        """새 스크립트 생성"""
        scripts = self._load()
        new_id = max((s["id"] for s in scripts), default=0) + 1
        now = datetime.utcnow().isoformat()

        new_script = {
            "id": new_id,
            **script.model_dump(),
            "created_at": now,
            "updated_at": now,
        }
        scripts.append(new_script)
        self._save(scripts)
        return new_script

    def get_by_id(self, script_id: int) -> Optional[dict]:
        """ID로 스크립트 조회"""
        scripts = self._load()
        return next((s for s in scripts if s["id"] == script_id), None)

    def get_by_video_id(self, video_id: int) -> Optional[dict]:
        """Video ID로 스크립트 조회"""
        scripts = self._load()
        return next((s for s in scripts if s["video_id"] == video_id), None)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[dict]:
        """스크립트 목록 조회"""
        scripts = self._load()
        return scripts[skip : skip + limit]

    def count(self) -> int:
        """스크립트 개수 조회"""
        scripts = self._load()
        return len(scripts)

    def update(self, script_id: int, update_data: ScriptUpdate) -> Optional[dict]:
        """스크립트 업데이트"""
        scripts = self._load()
        for i, s in enumerate(scripts):
            if s["id"] == script_id:
                # None이 아닌 값만 업데이트
                update_dict = update_data.model_dump(exclude_unset=True)
                scripts[i] = {**s, **update_dict, "updated_at": datetime.utcnow().isoformat()}
                self._save(scripts)
                return scripts[i]
        return None

    def delete(self, script_id: int) -> bool:
        """스크립트 삭제"""
        scripts = self._load()
        filtered = [s for s in scripts if s["id"] != script_id]
        if len(filtered) < len(scripts):
            self._save(filtered)
            return True
        return False
