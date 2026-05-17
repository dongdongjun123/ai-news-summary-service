# 백엔드 ↔ DB 연결 작업 계획

> 이 문서는 **DB 와 백엔드를 연결**하기 위한 사전 정리 + 설계안입니다.
> 구현 코드는 사용자가 "코드 짜라" 라고 명시한 다음에 작성합니다.

---

## 1. 지금까지 파악된 사실

### 1-1. DB

- DBMS: **PostgreSQL 18.3** (localhost:5432)
- 데이터베이스: `postgres`
- 스키마: `public`
- 적재 방식: pgAdmin import (CSV, `|` 구분)

#### 테이블 `public.news_articles`

| 컬럼 | 타입 | NULL | 비고 |
|---|---|---|---|
| `news_id` | `VARCHAR(50)` | NOT NULL | **PK** (`news_articles_pkey`) |
| `date` | `DATE` | NOT NULL | 기사 발행일 |
| `press` | `VARCHAR(50)` | NULL 허용 | 언론사명 |
| `title` | `TEXT` | NOT NULL | |
| `content` | `TEXT` | NOT NULL | 본문 풀텍스트 |
| `main_category` | `VARCHAR(20)` | NOT NULL | **FK** → `categories(name)` |
| `summary` | `TEXT` | NULL 허용 | 요약 결과 (지금은 비어 있음, 추후 KoBART 가 채울 자리) |

#### 인덱스

- `idx_news_category_date` : `(main_category, date DESC)`
  → 카테고리별 최신순 조회에 최적화됨

#### 제약

- PK: `news_id`
- FK: `main_category` → `public.categories(name)`

#### 테이블 `public.categories`

| 컬럼 | 타입 | NULL | 비고 |
|---|---|---|---|
| `name` | `VARCHAR(20)` | NOT NULL | **PK** (`categories_pkey`) |

- 단일 컬럼 (`name`) 만 존재. 별도 표시명/정렬값 없음.
- `news_articles.main_category` 의 FK 대상.
- API 응답은 단순 문자열 배열(`["정치", "경제", ...]`) 또는 객체 배열(`[{"name": "정치"}, ...]`) 중 선택. 프론트가 다루기 쉬운 쪽으로.

### 1-2. 프론트

- 위치: `ai-news-summary-service/front/`
- 스택: **Vue 3 (beta) + Vite + Pinia + Vue Router**
- 빌드: `vite`
- 즉 **SPA(클라이언트 사이드)** 구조 → 백엔드는 **REST JSON API** 가 자연스러움

### 1-3. 아직 확실하지 않은 것

- `categories` 테이블의 정확한 구조 (어떤 컬럼이 있는지, `name` 외에 표시명/순서가 있는지)
- 백엔드 언어/프레임워크 (아직 미정 상태로 보임)
- 운영 환경 (로컬 개발만 / Docker 사용 여부 / 배포 계획)

→ 이 셋은 본격 코드 들어가기 전에 결정 필요. (§3 참조)

---

## 2. DB 측 추가로 확인하면 좋은 것

코드 짜기 전에 짧게 확인해 두면 백엔드 설계가 더 깔끔해집니다.

1. **`categories` 테이블 구조**
   ```sql
   \d public.categories
   ```
   - `name` 외에 `display_name`, `sort_order` 같은 게 있으면 응답에 같이 노출
   - 현재 들어 있는 row 확인:
     ```sql
     SELECT * FROM public.categories ORDER BY name;
     ```

2. **데이터 분포** (API 페이지네이션 설계 참고)
   ```sql
   SELECT main_category, COUNT(*) FROM public.news_articles GROUP BY main_category;
   SELECT MIN(date), MAX(date) FROM public.news_articles;
   ```

3. **검색용 추가 인덱스 필요 여부**
   - 제목/본문 검색을 백엔드에서 지원할 거라면 GIN(pg_trgm) 인덱스 검토
   - 지금 단계에서는 굳이 안 만들어도 됨 (§4 의 검색 API 옵션 참고)

---

## 3. 백엔드 스택 선택지

현재 코드베이스에 이미 들어있는 자산을 고려하면:

| 후보 | 장점 | 단점 |
|---|---|---|
| **A. FastAPI (Python)** | `summarizer/` 의 KoBART(Python)와 같은 프로세스/패키지에서 바로 활용 가능. 비동기 라우팅 간단. SQLAlchemy/asyncpg 둘 다 가능 | Java/Node 익숙하면 신규 학습 비용 |
| **B. Spring Boot (Java)** | 정통적인 REST 백엔드, JPA 로 엔티티 매핑 깔끔 | KoBART(Python) 와 분리되어 RPC/HTTP 호출 필요 |
| **C. Express/NestJS (Node)** | 프론트(JS/TS) 와 언어 통일, 가벼움 | 요약 모델 추론을 Python 별도 서비스로 띄워야 함 |

**추천: A. FastAPI**
이유: 이미 `summarizer/test_summarize.py`에 Python KoBART 가 있고, 데이터 파이프라인(`data/*.py`)도 Python 이라 **언어/패키지 일관성**이 가장 큼. 요약 기능을 백엔드와 같은 서비스 안에서 처리할지, 별도 워커로 분리할지 선택의 폭이 가장 넓음.

> 사용자가 다른 스택을 원하면 §4 이후 설계는 그대로 두고 프레임워크만 바꿔서 적용합니다.

---

## 4. API 설계 (제안, 프레임워크 무관)

프론트가 "카테고리별 최신 뉴스 목록 + 상세 보기" 위주라고 가정.

### 4-1. 엔드포인트

| 메서드 | 경로 | 설명 |
|---|---|---|
| `GET` | `/api/categories` | 카테고리 전체 목록 (네비게이션/탭 용) |
| `GET` | `/api/news` | 뉴스 목록. 쿼리: `category`, `date_from`, `date_to`, `q`(검색), `page`, `size` |
| `GET` | `/api/news/{news_id}` | 단일 기사 상세 (본문 + 요약) |
| `GET` | `/api/news/{news_id}/summary` | 요약만 조회 (선택) |
| `POST` | `/api/news/{news_id}/summary` | 요약 생성/재생성 (관리자용, 인증 별도) |
| `GET` | `/api/stats` | 카테고리/날짜별 건수 (홈 통계 카드용) |

### 4-2. 응답 예시

`GET /api/news?category=정치&page=1&size=20`

```json
{
  "page": 1,
  "size": 20,
  "total": 1234,
  "items": [
    {
      "news_id": "01100611.20260401122708001",
      "date": "2026-04-01",
      "press": "서울신문",
      "title": "민주, ‘돈 봉투 살포’ 김관영 제명…",
      "main_category": "정치",
      "has_summary": false
    }
  ]
}
```

`GET /api/news/{news_id}`

```json
{
  "news_id": "01100611.20260401122708001",
  "date": "2026-04-01",
  "press": "서울신문",
  "title": "...",
  "content": "...",
  "main_category": "정치",
  "summary": null
}
```

### 4-3. 쿼리 매핑

- `category` → `WHERE main_category = $1`
- `date_from` / `date_to` → `WHERE date BETWEEN $a AND $b`
- `page`, `size` → `LIMIT/OFFSET` (정렬 기본 `date DESC, news_id DESC`)
- `q` (검색) — 1단계는 `title ILIKE '%' || $q || '%'` 정도로 시작, 데이터 커지면 GIN/pg_trgm 으로 업그레이드

> `idx_news_category_date` 가 이미 있어서 카테고리 + 날짜 범위 쿼리는 잘 받아줍니다.

---

## 5. 폴더/파일 구조 (FastAPI 안 기준 제안)

```
ai-news-summary-service/
├─ front/                        # 기존 Vue 프론트
├─ summarizer/                   # 기존 KoBART 모델 코드
├─ data/                         # 기존 데이터 파이프라인
├─ backend/                      # ← 신규
│   ├─ app/
│   │   ├─ main.py               # FastAPI 엔트리
│   │   ├─ core/
│   │   │   ├─ config.py         # DB URL / 환경변수 로딩 (.env)
│   │   │   └─ db.py             # 세션/엔진
│   │   ├─ models/
│   │   │   ├─ news.py           # news_articles 매핑
│   │   │   └─ category.py       # categories 매핑
│   │   ├─ schemas/              # Pydantic (응답 DTO)
│   │   ├─ repositories/         # 쿼리 계층
│   │   ├─ services/             # 비즈니스 로직 (요약 호출 등)
│   │   └─ routers/
│   │       ├─ news.py
│   │       ├─ categories.py
│   │       └─ stats.py
│   ├─ requirements.txt
│   └─ .env.example
└─ ...
```

> 다른 스택을 고른 경우에는 폴더명만 바뀌고 계층 분리는 거의 동일.

---

## 6. DB 연결 설정 방침

- 접속 정보는 **`.env`** 에만 두고 코드/Git 에는 절대 포함하지 않음
  ```env
  DB_HOST=localhost
  DB_PORT=5432
  DB_NAME=postgres
  DB_USER=postgres
  DB_PASSWORD=...
  ```
- `.env` 는 `.gitignore` 에 추가 (이미 있다면 그대로 유지)
- 풀(Pool): 동시 요청 대비 `pool_size=5~10` 정도면 로컬 개발/시연용으로 충분
- 트랜잭션: 조회는 readonly, 요약 저장 같은 변경 작업만 트랜잭션
- 시간대(`TIMESTAMP` 안 쓰고 `DATE` 만 쓰므로 큰 이슈 없음)

---

## 7. CORS / 프론트 연동

- 개발 시: 백엔드 `http://localhost:8000`, 프론트 `http://localhost:5173`
- CORS 허용 origin 에 프론트 URL 등록
- 프론트 `vite.config` 의 `proxy` 로 `/api → :8000` 잡으면 CORS 우회 가능 (선호 시)

---

## 8. 기존 파이썬 모듈 활용 (summarizer / stat_summary)

이미 같은 저장소 안에 잘 분리된 두 모듈이 존재하므로, **백엔드는 이 둘을 호출만 한다**는 그림이 자연스럽다.

### 8-1. `summarizer/` — 본문 요약 (KoBART)

- 구성
  - `summarizer/main.py` — 이미 FastAPI 앱 (`POST /summarize/batch`)
  - `summarizer/model.py` — `load_model()`, `summarize(text)` 분리
  - `summarizer/requirements.txt` — fastapi, uvicorn, transformers, torch, sentencepiece
- **활용 방식 — A. 별도 마이크로서비스 (확정)**
  - 백엔드와 summarizer 를 각각 FastAPI 서버로 분리 운영
  - 로컬 개발 포트:
    - backend: `http://localhost:8000`
    - summarizer: `http://localhost:8001`
  - 책임 분리
    - **백엔드 (8000)** : DB 조회, 비즈니스 로직, API 응답
    - **summarizer (8001)** : KoBART 모델 로딩, 요약 생성만 담당
  - 백엔드는 `httpx` (또는 `requests`) 로 `POST http://localhost:8001/summarize/batch` 호출
  - 부팅
    - `uvicorn backend.app.main:app --port 8000 --reload`
    - `uvicorn summarizer.main:app --port 8001 --reload`
  - 환경변수에 summarizer URL 두기 (`SUMMARIZER_URL=http://localhost:8001`)
- 채우기 시점
  - **온디맨드 (확정)**: 상세 조회 시 `summary` 비어있으면 백엔드가 summarizer 호출 → 결과를 `news_articles.summary` 에 저장 후 응답
  - summarizer 호출은 시간이 걸릴 수 있으므로 백엔드는 timeout / 실패 처리 분기를 둠 (timeout 시 일단 본문만 응답하고 다음 조회에 다시 시도)
- DB 매핑
  - 입력: `news_articles.content`
  - 출력: `news_articles.summary` (TEXT, 이미 컬럼 존재)

### 8-2. `stat_summary/` — 통계/키워드/연관어/추이/인사이트

- 엔트리: `from stat_summary.analyzer import analyze_article_statistics`
- 입력
  - `article` (dict): `id`, `title`, `content`
  - `corpus_articles` (list[dict]): 같은 카테고리 최근 N개월 정도가 무난 (트렌드/언급량 계산용)
- 출력 dict (요약)
  - `statistics`: word_count / sentence_count / keyword_count / corpus_keyword_count
  - `core_keyword`, `related_terms`, `mention_trend`
  - `stat_analysis`, `ai_insights`, `model_info`
- 옵션 — **둘 다 OFF (확정)**
  - `use_llm=False` → rule-based 키워드 추출만 사용
  - `use_keybert=False` → 빈도/공기 기반 연관어만 사용
  - 사유: 백엔드-DB-프론트 연결 + 기본 분석 API 안정화 우선. 큰 모델 다운로드/추론 부담 없이 시작.
  - 추후 확장 계획: 동작 안정화 후, **`use_keybert=True` 만 먼저 켜서** 연관어 품질 개선
- 활용 방식
  - 백엔드 내부에서 **직접 import 호출**. 결과는 보통 **DB에 저장하지 않고 매 요청 계산** (캐시 도입은 추후 검토)
  - 코퍼스 조회는 백엔드 쿼리로 한 번 더 가져온 뒤 함수에 dict 리스트로 전달
- 의존성: `stat_summary/requirements_stat.txt` 별도 존재

### 8-3. 책임 분리 요약

| 모듈 | 역할 | 결과 저장 위치 |
|---|---|---|
| `summarizer/` | 본문 → 요약 1문단 | DB `news_articles.summary` |
| `stat_summary/` | 본문/코퍼스 → 분석 카드용 데이터 | DB에 저장 X (필요 시 캐시) |
| backend | DB ↔ HTTP API, 위 두 모듈 호출 | — |

### 8-4. API 매핑 (§4 보강)

| 엔드포인트 | 내부 처리 |
|---|---|
| `GET /api/news/{news_id}` | DB row 반환. `summary` 가 비어 있고 정책이 "온디맨드" 면 그 자리에서 생성 후 저장 |
| `POST /api/news/{news_id}/summary` | 강제 (재)생성. 관리자/디버그용 |
| `GET /api/news/{news_id}/stats` | 기사 + 코퍼스 조회 → `analyze_article_statistics(...)` → JSON 응답 (프론트 `StatCards.vue` 에 매핑) |

---

## 9. 진행 순서 제안

1. **사용자 확인 사항**
   - ✅ 백엔드 스택: **FastAPI**
   - ✅ 요약 채우기 정책: **요청 시 생성 (온디맨드)**
   - ✅ `categories` 테이블 구조 확인 — `name VARCHAR(20)` 단일 컬럼
   - ✅ 요약 서비스 형태: **A. 별도 서비스** (backend 8000, summarizer 8001)
   - ✅ `stat_summary` 옵션: `use_llm=False`, `use_keybert=False` (rule-based 우선, 안정화 후 KeyBERT 확장)
2. **백엔드 골격 (포트 8000)**
   - `backend/` 폴더 생성 + 의존성 설치 + `.env` 로 DB / summarizer URL 설정
   - `/health`, `/api/categories` 부터 동작 확인
3. **읽기 API**
   - `/api/news` 목록 (필터/페이지네이션)
   - `/api/news/{news_id}` 상세 — `summary` 온디맨드 생성 분기 포함
4. **요약 클라이언트**
   - `summarizer (8001)` 호출 클라이언트 (`httpx` 권장)
   - timeout / 실패 처리 / 재시도 정책 정의
5. **분석 API**
   - `/api/news/{news_id}/stats` — `stat_summary.analyzer` 직접 import 호출
   - 코퍼스 조회 쿼리 정의 (예: 같은 카테고리 최근 90일)
6. **프론트 연동**
   - 기존 `front/src/api/newsApi.js` 를 백엔드 엔드포인트에 맞춰 정리
   - `StatCards.vue` 가 `/api/news/{id}/stats` 응답 구조에 맞도록 매핑

---

## 10. 결정 대기 항목 (Action Items)

- [x] **백엔드 스택**: FastAPI
- [x] **요약(`summary`) 처리 정책**: 요청 시 생성 (온디맨드)
- [x] **`categories` 테이블**: `name VARCHAR(20)` PK 단일 컬럼 (별도 표시명/정렬 없음)
- [x] **요약 서비스 형태**: A. 별도 서비스
  - backend: `http://localhost:8000`
  - summarizer: `http://localhost:8001`
- [x] **`stat_summary` 옵션**: `use_llm=False`, `use_keybert=False` (rule-based, 안정화 후 KeyBERT 확장 검토)

모든 결정 사항 확정됨. 사용자의 코드 작성 신호를 받으면 §5 / §8 / §9 골격대로 바로 코드 진입 가능.
