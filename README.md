# Video Upload Automation

YouTube & Instagram 영상 자동 업로드 시스템

## 프로젝트 구조

```
video-upload-automation/
├── frontend/          # Next.js 15 + React 19 프론트엔드
├── src/               # FastAPI 백엔드
│   ├── api/          # API 엔드포인트
│   ├── domain/       # 도메인 로직 (Video, Script, Post, UploadJob)
│   ├── integrations/ # 외부 API 통합 (OpenAI, YouTube, Instagram)
│   ├── workers/      # 백그라운드 Worker
│   └── core/         # 공통 유틸리티
└── data/             # JSON 데이터 저장소
```

## 주요 기능

### 백엔드 (FastAPI)
- ✅ Video 도메인: 영상 업로드 및 관리
- ✅ Script 도메인: 영상 대본 관리
- ✅ Post 도메인: AI 바디글 생성 (OpenAI GPT)
- ✅ Upload Job 도메인: 업로드 작업 스케줄링
- ✅ YouTube Data API v3 통합
- ✅ Instagram Graph API 통합
- ✅ 백그라운드 Worker (자동 업로드 처리)

### 프론트엔드 (Next.js)
- ✅ 대시보드 (통계 및 빠른 작업)
- ✅ 영상 관리 (목록, 업로드)
- 🔄 스크립트 작성
- 🔄 AI 포스트 생성
- 🔄 업로드 작업 관리

## 설치 및 실행

### 백엔드 실행

```bash
# 의존성 설치
uv sync

# 환경변수 설정
cp .env.example .env
# .env 파일을 열어서 OpenAI API 키 등 설정

# 서버 실행
uv run uvicorn src.main:app --reload

# API 문서 확인
open http://localhost:8000/docs
```

### 프론트엔드 실행

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 브라우저에서 확인
open http://localhost:3000
```

### Worker 실행 (선택사항)

```bash
# 백그라운드 업로드 Worker 실행
python -m src.workers.upload_worker
```

## API 워크플로우

### 1. 영상 업로드
```bash
POST /api/v1/videos/
Content-Type: multipart/form-data

- title: 영상 제목
- video_file: 영상 파일
- thumbnail_file: 썸네일 (선택)
```

### 2. 스크립트 작성
```bash
POST /api/v1/scripts/
{
  "video_id": 1,
  "content": "영상 대본 내용..."
}
```

### 3. AI 바디글 생성
```bash
POST /api/v1/posts/generate
{
  "video_id": 1,
  "script_id": 1,
  "platform": "youtube",
  "generate_hashtags": true,
  "hashtag_count": 10
}
```

### 4. 업로드 작업 생성
```bash
POST /api/v1/upload-jobs/
{
  "video_id": 1,
  "post_id": 1,
  "platform": "youtube",
  "scheduled_at": "2026-01-04T10:00:00Z"  // 예약 (선택)
}
```

### 5. 업로드 실행
```bash
POST /api/v1/upload-jobs/1/execute?force=false
```

## 환경변수 (.env)

```env
# App
APP_ENV=development
DEBUG=true
SECRET_KEY=your-secret-key

# Data
DATA_DIR=data

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4o-mini

# YouTube
YOUTUBE_CREDENTIALS_FILE=data/credentials/youtube_credentials.json
YOUTUBE_TOKEN_FILE=data/credentials/youtube_token.json

# Instagram
INSTAGRAM_ACCESS_TOKEN=your-instagram-access-token
INSTAGRAM_USER_ID=your-instagram-user-id

# Upload
MAX_VIDEO_SIZE_MB=500
ALLOWED_VIDEO_FORMATS=["mp4","mov","avi","mkv"]
```

## YouTube API 설정

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성
3. YouTube Data API v3 활성화
4. OAuth 2.0 클라이언트 ID 생성
5. `youtube_credentials.json` 다운로드
6. `data/credentials/` 디렉토리에 저장

## Instagram API 설정

1. [Facebook Developers](https://developers.facebook.com/) 접속
2. 앱 생성 및 Instagram Graph API 활성화
3. Access Token 발급
4. `.env`에 토큰 및 User ID 설정

## 기술 스택

### 백엔드
- FastAPI (Python 3.14)
- OpenAI API (GPT-4o-mini)
- Google YouTube Data API v3
- Instagram Graph API
- JSON 파일 기반 데이터 저장

### 프론트엔드
- Next.js 15
- React 19
- TypeScript
- Tailwind CSS
- Axios
- date-fns

## 개발 상태

- [x] Phase 1: 기본 인프라
- [x] Phase 2: Video 도메인
- [x] Phase 3: Script & Post 도메인, OpenAI 통합
- [x] Phase 4-5: YouTube/Instagram 통합, Upload Job, Worker
- [x] Phase 6: 프론트엔드 기본 구조

## 라이선스

MIT

## 작성자

Claude Code + @eunsecc
