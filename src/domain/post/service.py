"""Post Service - AI 바디글 생성 비즈니스 로직"""

from typing import Optional

from src.core.exceptions import NotFoundError
from src.domain.post.repository import PostRepository
from src.domain.post.schemas import (
    Platform,
    PostCreate,
    PostGenerateRequest,
    PostListResponse,
    PostResponse,
    PostUpdate,
)
from src.domain.script.repository import ScriptRepository
from src.integrations.openai_service import OpenAIService


class PostService:
    """Post 비즈니스 로직"""

    def __init__(
        self,
        repository: PostRepository,
        script_repository: ScriptRepository,
        openai_service: OpenAIService,
    ):
        self.repository = repository
        self.script_repository = script_repository
        self.openai_service = openai_service

    async def create_post(self, post_data: PostCreate) -> PostResponse:
        """포스트 생성"""
        post = self.repository.create(post_data)
        return PostResponse(**post)

    async def generate_post(
        self, generate_request: PostGenerateRequest
    ) -> PostResponse:
        """
        AI를 사용하여 포스트 생성

        Args:
            generate_request: 포스트 생성 요청

        Returns:
            생성된 포스트

        Raises:
            ResourceNotFoundError: 스크립트를 찾을 수 없는 경우
        """
        # 스크립트 조회
        script = self.script_repository.get_by_id(generate_request.script_id)
        if not script:
            raise NotFoundError(
                f"Script ID {generate_request.script_id} not found"
            )

        # OpenAI로 바디글 생성
        content = await self.openai_service.generate_post_content(
            script=script["content"], platform=generate_request.platform.value
        )

        # 해시태그 생성 (선택적)
        hashtags = []
        if generate_request.generate_hashtags:
            hashtags = await self.openai_service.generate_hashtags(
                script=script["content"],
                platform=generate_request.platform.value,
                count=generate_request.hashtag_count,
            )

        # 포스트 생성
        post_data = PostCreate(
            video_id=generate_request.video_id,
            script_id=generate_request.script_id,
            platform=generate_request.platform,
            content=content,
            hashtags=hashtags,
        )

        return await self.create_post(post_data)

    async def get_post_by_id(self, post_id: int) -> PostResponse:
        """포스트 상세 조회"""
        post = self.repository.get_by_id(post_id)
        if not post:
            raise NotFoundError(f"Post ID {post_id} not found")
        return PostResponse(**post)

    async def get_posts_by_video_id(
        self, video_id: int, platform: Optional[Platform] = None
    ) -> list[PostResponse]:
        """Video ID로 포스트 목록 조회"""
        posts = self.repository.get_by_video_id(video_id, platform)
        return [PostResponse(**p) for p in posts]

    async def list_posts(
        self, skip: int = 0, limit: int = 100, platform: Optional[Platform] = None
    ) -> PostListResponse:
        """포스트 목록 조회"""
        posts = self.repository.get_all(skip, limit, platform)
        total = self.repository.count(platform)
        return PostListResponse(total=total, posts=[PostResponse(**p) for p in posts])

    async def update_post(self, post_id: int, update_data: PostUpdate) -> PostResponse:
        """포스트 업데이트"""
        post = self.repository.update(post_id, update_data)
        if not post:
            raise NotFoundError(f"Post ID {post_id} not found")
        return PostResponse(**post)

    async def delete_post(self, post_id: int) -> None:
        """포스트 삭제"""
        success = self.repository.delete(post_id)
        if not success:
            raise NotFoundError(f"Post ID {post_id} not found")
