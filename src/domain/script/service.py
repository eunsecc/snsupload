"""Script Service - 비즈니스 로직"""

from src.core.exceptions import NotFoundError
from src.domain.script.repository import ScriptRepository
from src.domain.script.schemas import (
    ScriptCreate,
    ScriptListResponse,
    ScriptResponse,
    ScriptUpdate,
)


class ScriptService:
    """Script 비즈니스 로직"""

    def __init__(self, repository: ScriptRepository):
        self.repository = repository

    async def create_script(self, script_data: ScriptCreate) -> ScriptResponse:
        """스크립트 생성"""
        script = self.repository.create(script_data)
        return ScriptResponse(**script)

    async def get_script_by_id(self, script_id: int) -> ScriptResponse:
        """스크립트 상세 조회"""
        script = self.repository.get_by_id(script_id)
        if not script:
            raise NotFoundError(f"Script ID {script_id} not found")
        return ScriptResponse(**script)

    async def get_script_by_video_id(self, video_id: int) -> ScriptResponse:
        """Video ID로 스크립트 조회"""
        script = self.repository.get_by_video_id(video_id)
        if not script:
            raise ResourceNotFoundError(f"Script for Video ID {video_id} not found")
        return ScriptResponse(**script)

    async def list_scripts(self, skip: int = 0, limit: int = 100) -> ScriptListResponse:
        """스크립트 목록 조회"""
        scripts = self.repository.get_all(skip, limit)
        total = self.repository.count()
        return ScriptListResponse(
            total=total, scripts=[ScriptResponse(**s) for s in scripts]
        )

    async def update_script(
        self, script_id: int, update_data: ScriptUpdate
    ) -> ScriptResponse:
        """스크립트 업데이트"""
        script = self.repository.update(script_id, update_data)
        if not script:
            raise NotFoundError(f"Script ID {script_id} not found")
        return ScriptResponse(**script)

    async def delete_script(self, script_id: int) -> None:
        """스크립트 삭제"""
        success = self.repository.delete(script_id)
        if not success:
            raise NotFoundError(f"Script ID {script_id} not found")
