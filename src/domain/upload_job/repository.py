"""Upload Job Repository - JSON 기반 CRUD"""

import json
from datetime import datetime
from typing import Optional

from src.config import settings
from src.domain.upload_job.schemas import (
    UploadJobCreate,
    UploadJobUpdate,
    UploadPlatform,
    UploadStatus,
)


class UploadJobRepository:
    """Upload Job JSON Repository"""

    def __init__(self):
        self.data_file = settings.data_dir / "upload_jobs.json"
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
            json.dumps(data, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )

    def create(self, job: UploadJobCreate) -> dict:
        """새 업로드 작업 생성"""
        jobs = self._load()
        new_id = max((j["id"] for j in jobs), default=0) + 1
        now = datetime.utcnow().isoformat()

        new_job = {
            "id": new_id,
            **job.model_dump(),
            "platform": job.platform.value,
            "status": UploadStatus.PENDING.value,
            "uploaded_at": None,
            "platform_video_id": None,
            "platform_url": None,
            "error_message": None,
            "created_at": now,
            "updated_at": now,
        }

        # scheduled_at을 ISO format으로 변환
        if new_job["scheduled_at"]:
            new_job["scheduled_at"] = new_job["scheduled_at"].isoformat()

        jobs.append(new_job)
        self._save(jobs)
        return new_job

    def get_by_id(self, job_id: int) -> Optional[dict]:
        """ID로 작업 조회"""
        jobs = self._load()
        return next((j for j in jobs if j["id"] == job_id), None)

    def get_by_video_id(
        self, video_id: int, platform: Optional[UploadPlatform] = None
    ) -> list[dict]:
        """Video ID로 작업 조회"""
        jobs = self._load()
        result = [j for j in jobs if j["video_id"] == video_id]
        if platform:
            result = [j for j in result if j["platform"] == platform.value]
        return result

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[UploadStatus] = None,
        platform: Optional[UploadPlatform] = None,
    ) -> list[dict]:
        """작업 목록 조회"""
        jobs = self._load()

        # 상태 필터링
        if status:
            jobs = [j for j in jobs if j["status"] == status.value]

        # 플랫폼 필터링
        if platform:
            jobs = [j for j in jobs if j["platform"] == platform.value]

        # 페이징
        return jobs[skip : skip + limit]

    def get_pending_jobs(self) -> list[dict]:
        """대기 중인 작업 조회 (예약 시간이 지난 작업 포함)"""
        jobs = self._load()
        now = datetime.utcnow()

        pending = []
        for job in jobs:
            if job["status"] != UploadStatus.PENDING.value:
                continue

            # 예약 시간이 없거나, 예약 시간이 지난 경우
            if not job["scheduled_at"]:
                pending.append(job)
            else:
                scheduled = datetime.fromisoformat(job["scheduled_at"])
                if scheduled <= now:
                    pending.append(job)

        return pending

    def count(
        self,
        status: Optional[UploadStatus] = None,
        platform: Optional[UploadPlatform] = None,
    ) -> int:
        """작업 개수 조회"""
        jobs = self._load()

        if status:
            jobs = [j for j in jobs if j["status"] == status.value]
        if platform:
            jobs = [j for j in jobs if j["platform"] == platform.value]

        return len(jobs)

    def update(self, job_id: int, update_data: UploadJobUpdate) -> Optional[dict]:
        """작업 업데이트"""
        jobs = self._load()
        for i, j in enumerate(jobs):
            if j["id"] == job_id:
                # None이 아닌 값만 업데이트
                update_dict = update_data.model_dump(exclude_unset=True)

                # Enum 값을 문자열로 변환
                if "status" in update_dict and update_dict["status"]:
                    update_dict["status"] = update_dict["status"].value

                jobs[i] = {**j, **update_dict, "updated_at": datetime.utcnow().isoformat()}
                self._save(jobs)
                return jobs[i]
        return None

    def update_status(
        self,
        job_id: int,
        status: UploadStatus,
        platform_video_id: Optional[str] = None,
        platform_url: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> Optional[dict]:
        """작업 상태 업데이트"""
        jobs = self._load()
        for i, j in enumerate(jobs):
            if j["id"] == job_id:
                jobs[i]["status"] = status.value
                jobs[i]["updated_at"] = datetime.utcnow().isoformat()

                if platform_video_id:
                    jobs[i]["platform_video_id"] = platform_video_id
                if platform_url:
                    jobs[i]["platform_url"] = platform_url
                if error_message:
                    jobs[i]["error_message"] = error_message

                # 완료 시 uploaded_at 설정
                if status == UploadStatus.COMPLETED:
                    jobs[i]["uploaded_at"] = datetime.utcnow().isoformat()

                self._save(jobs)
                return jobs[i]
        return None

    def delete(self, job_id: int) -> bool:
        """작업 삭제"""
        jobs = self._load()
        filtered = [j for j in jobs if j["id"] != job_id]
        if len(filtered) < len(jobs):
            self._save(filtered)
            return True
        return False
