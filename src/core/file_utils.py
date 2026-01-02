import shutil
from pathlib import Path

from fastapi import UploadFile

from src.config import settings

UPLOAD_DIR = settings.data_dir / "uploads"


async def save_video_file(video_id: int, file: UploadFile) -> str:
    """
    영상 파일 저장

    Args:
        video_id: 영상 ID
        file: 업로드된 파일

    Returns:
        저장된 파일 경로
    """
    # 디렉토리 생성
    video_dir = UPLOAD_DIR / "videos" / str(video_id)
    video_dir.mkdir(parents=True, exist_ok=True)

    # 파일 확장자 추출
    file_ext = Path(file.filename).suffix if file.filename else ".mp4"

    # 파일 저장
    file_path = video_dir / f"video{file_ext}"

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return str(file_path)


async def save_thumbnail_file(video_id: int, file: UploadFile) -> str:
    """
    썸네일 파일 저장

    Args:
        video_id: 영상 ID
        file: 업로드된 파일

    Returns:
        저장된 파일 경로
    """
    thumbnail_dir = UPLOAD_DIR / "thumbnails" / str(video_id)
    thumbnail_dir.mkdir(parents=True, exist_ok=True)

    file_ext = Path(file.filename).suffix if file.filename else ".jpg"
    file_path = thumbnail_dir / f"thumbnail{file_ext}"

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return str(file_path)


def get_file_size(file_path: str) -> int:
    """
    파일 크기 조회

    Args:
        file_path: 파일 경로

    Returns:
        파일 크기 (bytes)
    """
    return Path(file_path).stat().st_size


def delete_video_files(video_id: int) -> None:
    """
    영상 관련 파일 삭제

    Args:
        video_id: 영상 ID
    """
    video_dir = UPLOAD_DIR / "videos" / str(video_id)
    thumbnail_dir = UPLOAD_DIR / "thumbnails" / str(video_id)

    if video_dir.exists():
        shutil.rmtree(video_dir)

    if thumbnail_dir.exists():
        shutil.rmtree(thumbnail_dir)
