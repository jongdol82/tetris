# 테트리스

회원가입/로그인, 점수 저장, 전체 랭킹을 지원하는 브라우저 테트리스 게임입니다.

## 스택

| 영역 | 기술 |
|------|------|
| 프론트엔드 | HTML + Vanilla JS (Canvas API) |
| 백엔드 | FastAPI + SQLite |
| 인증 | JWT (Bearer Token) |

## 기능

- 회원가입 / 로그인
- 테트리스 게임 (고스트 피스, 레벨업, 배경음악)
- 게임 종료 시 점수 자동 저장
- 전체 최고 점수 및 달성자 표시
- 다크 / 라이트 모드 토글 (설정 기억)

## 조작키

| 키 | 동작 |
|----|------|
| `← →` | 좌우 이동 |
| `↑` | 회전 |
| `↓` | 빠른 낙하 |
| `Space` | 즉시 낙하 |
| `P` | 일시정지 / 재개 |
| `M` | 음소거 토글 |

## 실행 방법

### 백엔드

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

서버가 `http://localhost:8000` 에서 실행됩니다.

### 프론트엔드

`tetris.html` 을 브라우저에서 직접 열면 됩니다.

## API

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/auth/register` | 회원가입 |
| POST | `/auth/login` | 로그인 (JWT 발급) |
| GET | `/auth/me` | 내 정보 조회 |
| POST | `/games/record` | 게임 점수 저장 |
| GET | `/games/top-score` | 전체 최고 점수 조회 |
| GET | `/games/my-records` | 내 최근 10개 기록 |
