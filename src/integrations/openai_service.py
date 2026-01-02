"""OpenAI API 통합 서비스"""

from openai import AsyncOpenAI

from src.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class OpenAIService:
    """OpenAI API 서비스"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    async def generate_post_content(
        self, script: str, platform: str = "youtube"
    ) -> str:
        """
        스크립트로부터 SNS 포스트 바디글 생성

        Args:
            script: 영상 대본
            platform: SNS 플랫폼 (youtube, instagram)

        Returns:
            생성된 바디글
        """
        # 플랫폼별 프롬프트 구성
        platform_instructions = {
            "youtube": """
YouTube 영상 설명란에 적합한 바디글을 작성해주세요.
- 영상의 핵심 내용을 요약
- 시청자의 흥미를 유발하는 문구
- 해시태그는 제외 (별도로 관리됨)
- 3-5문단으로 구성
- 친근하고 자연스러운 톤
""",
            "instagram": """
Instagram 게시물에 적합한 바디글을 작성해주세요.
- 영상의 핵심 메시지를 간결하게 전달
- 감정을 자극하는 문구
- 해시태그는 제외 (별도로 관리됨)
- 2-3문단으로 구성
- 짧고 임팩트 있는 문장
""",
        }

        instructions = platform_instructions.get(platform, platform_instructions["youtube"])

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"""당신은 SNS 콘텐츠 전문가입니다.
영상 대본을 바탕으로 매력적인 포스트 바디글을 작성합니다.
{instructions}""",
                    },
                    {
                        "role": "user",
                        "content": f"다음 영상 대본을 바탕으로 {platform} 바디글을 작성해주세요:\n\n{script}",
                    },
                ],
                temperature=0.7,
                max_tokens=1000,
            )

            content = response.choices[0].message.content
            logger.info(f"OpenAI post content generated for platform: {platform}")
            return content.strip()

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def generate_hashtags(
        self, script: str, platform: str = "youtube", count: int = 10
    ) -> list[str]:
        """
        스크립트로부터 해시태그 생성

        Args:
            script: 영상 대본
            platform: SNS 플랫폼
            count: 생성할 해시태그 개수

        Returns:
            생성된 해시태그 리스트
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"""당신은 SNS 마케팅 전문가입니다.
영상 대본을 분석하여 {platform}에 적합한 해시태그를 생성합니다.
- 트렌디하고 검색량이 높은 키워드 선택
- 영상 내용과 직접적으로 연관된 태그
- # 기호 포함하여 출력
- 각 태그는 줄바꿈으로 구분""",
                    },
                    {
                        "role": "user",
                        "content": f"다음 영상 대본을 바탕으로 {count}개의 해시태그를 생성해주세요:\n\n{script}",
                    },
                ],
                temperature=0.8,
                max_tokens=300,
            )

            content = response.choices[0].message.content
            # 해시태그 파싱 (줄바꿈으로 구분)
            hashtags = [
                tag.strip()
                for tag in content.strip().split("\n")
                if tag.strip().startswith("#")
            ]
            logger.info(f"OpenAI hashtags generated: {len(hashtags)} tags")
            return hashtags[:count]

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
