from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # App
    app_env: str = "development"
    debug: bool = False
    secret_key: str = "dev-secret-key-change-in-production"

    # Data
    data_dir: Path = Path("data")

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"

    # YouTube
    youtube_credentials_file: Path = Path("data/credentials/youtube_credentials.json")
    youtube_token_file: Path = Path("data/credentials/youtube_token.json")

    # Instagram
    instagram_manual_upload: bool = True
    instagram_access_token: Optional[str] = None
    instagram_user_id: Optional[str] = None

    # Upload Settings
    max_video_size_mb: int = 500
    allowed_video_formats: list[str] = ["mp4", "mov", "avi", "mkv"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
