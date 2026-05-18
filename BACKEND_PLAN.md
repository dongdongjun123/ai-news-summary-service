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

## 4. API 설계 (현재 프론트 코드 기준)

> 프론트 코드를 직접 확인한 결과 다음 사실이 명확해짐.  
> 백엔드 API 는 **프론트가 실제로 호출하는 형태에 맞춤**.

### 4-1. 프론트가 실제로 부르는 API (`front/src/api/newsApi.js`)

| 함수 | 백엔드 경로 | 호출 시점 |
|---|---|---|
| `fetchNews()` | `GET /api/news` | (직접 호출 안 됨) |
| `fetchNewsByCategory(category)` | `GET /api/news?category=...` | `useNewsStore.loadNews()` → 페이지 로드/탭 변경/새로고침 |
| `fetchNewsById(id)` | `GET /api/news/{id}` | 모달 열 때 (※ 현 코드에는 호출이 없음 — §4-6 참조) |

### 4-2. 프론트 ↔ 백엔드 필드 매핑

| 프론트 필드 | 출처(DB) | 비고 |
|---|---|---|
| `id` | `news_articles.news_id` | DB는 `VARCHAR(50)`. 프론트 dummy 에선 number 였지만 string 그대로 사용 가능 (NewsCard 의 `:key`/클릭 핸들러 모두 type-agnostic) |
| `title` | `title` | 그대로 |
| `summary` | `summary` | 비어있으면(=NULL) **상세 조회 시 온디맨드 생성** (§8-1) |
| `category` | `main_category` | §4-3 정규화 참조 |
| `source` | `press` | 컬럼명 다름 → 응답에서 매핑 |
| `published_at` | `date` | DB 는 `DATE` 만 보관. NewsCard 의 `formatDate()` 는 `new Date("2026-04-01")` 로도 잘 파싱되므로 **그대로 문자열 전달 가능** |
| `content` | `content` | 상세 응답에서만 사용 |
| `url` | (없음) | 원문 URL 미보유. 응답에서 `null` 로 보냄 (프론트는 표시 안 함) |
| `thumbnail` | (없음) | 미보유. `null`. NewsCard 는 `v-if="news.thumbnail"` 으로 옵셔널 처리되어 안전 |
| `mention_trend` | `stat_summary` 결과 | 상세 응답에서만, 4주(=`recent_n=4`) |
| `related_keywords` | `stat_summary` 결과 | 상세 응답에서만, 8개 내외 |

### 4-3. 카테고리 정규화

프론트 카테고리 (NavBar 탭 / `useNewsStore.CATEGORIES`):
```
['전체', '정치', '경제', '사회', '문화', '국제', '지역', '스포츠', 'IT과학']
```

DB `categories(name)` 8개에는 `전체` 없음. 또한 IT 카테고리 표기는 DB/크롤러 측에서 `IT_과학` 형태로 들어갔을 가능성이 있음.

- 백엔드 처리
  - `?category=전체` 또는 파라미터 자체가 없으면 → 필터 없이 전체 반환
  - `?category=IT과학` 들어오면 DB 값과 정합 매핑 (`IT과학` ↔ `IT_과학`)
  - 그 외(`정치`/`경제`/...)는 그대로 일치
- DB 측에서 카테고리명을 실제로 어떤 문자열로 저장했는지 한 번만 확인:
  ```sql
  SELECT * FROM public.categories;
  SELECT DISTINCT main_category FROM public.news_articles;
  ```

### 4-4. 엔드포인트 (확정)

| 메서드 | 경로 | 설명 |
|---|---|---|
| `GET` | `/health` | 헬스체크 |
| `GET` | `/api/categories` | 카테고리 목록 (백엔드 단일 진실원) |
| `GET` | `/api/news?category=...` | 뉴스 목록 — **단순 배열** (페이지네이션 없음) |
| `GET` | `/api/news/{id}` | 상세 — content + summary(온디맨드) + `mention_trend` + `related_keywords` 까지 한 객체로 통합 |
| `POST` | `/api/news/{id}/summary` | 요약 강제 (재)생성. 운영/디버그용 |

> **삭제된 항목 (현재 프론트가 안 쓰는 것)**
> - `q` (검색), `date_from`/`date_to` (날짜 필터) — UI 없음
> - `page` / `size` — 페이지네이션 UI 없음 (목록은 단순 배열로 응답)
> - `GET /api/news/{id}/summary` — 별도 요약 조회 UI 없음 (`/api/news/{id}` 응답에 포함됨)
> - `GET /api/stats` — `StatCards.vue` 가 `store.totalCount` 로 자체 계산 (서버 통계 API 불필요)
> - `GET /api/news/{id}/stats` — `mention_trend/related_keywords` 가 상세 응답에 통합되어 별도 호출 불필요

### 4-5. 응답 예시

`GET /api/news?category=정치`

```json
[
  {
    "id": "01100611.20260401122708001",
    "title": "민주, ‘돈 봉투 살포’ 김관영 제명…",
    "summary": null,
    "category": "정치",
    "source": "서울신문",
    "published_at": "2026-04-01",
    "url": null,
    "thumbnail": null
  }
]
```

`GET /api/news/{id}`

```json
{
  "id": "01100611.20260401122708001",
  "title": "...",
  "summary": "AI가 생성한 한 단락 요약...",
  "content": "본문 풀텍스트...",
  "category": "정치",
  "source": "서울신문",
  "published_at": "2026-04-01",
  "url": null,
  "thumbnail": null,
  "mention_trend": [80, 120, 90, 160],
  "related_keywords": ["김관영", "민주당", "전북지사", "돈봉투", "경선", "제명", "윤리감찰", "지방선거"]
}
```

`GET /api/categories`

```json
["정치", "경제", "사회", "문화", "국제", "지역", "스포츠", "IT과학"]
```
> `전체` 는 프론트 측에서만 다루는 UI 토큰이므로 응답에 넣지 않음.

### 4-6. 프론트가 살짝 바꿔야 하는 부분 (코드 작업 단계에서 함께 진행)

> 현재 프론트는 더미 JSON 기준이라 **목록 한 번 받으면 모달까지 그 객체로 다 그림**.  
> 백엔드 연결 시 상세는 별도 호출이 자연스러우므로 아래 3가지가 필요함.

1. **모달 열 때 상세 조회** — `NewsGrid.vue` 의 `@click="selectedNews = item"` 을 `await fetchNewsById(item.id)` 결과로 교체  
   (목록 응답에는 `summary/content/mention_trend/related_keywords` 가 없음)
2. **`newsApi.js` 의 더미 import 제거** → 주석 처리된 `BASE_URL` + `fetch(...)` 활성화
3. **카테고리 파라미터 처리** — `'전체'` 일 때 쿼리에 안 붙이도록 (이미 그렇게 되어 있음, 확인만)

추가로 미사용 정리(선택):
- `stores/counter.js` 등 안 쓰는 파일
- `data/dummy_news.json` (백엔드 붙으면 불필요)

### 4-7. 쿼리/정렬 정책

- `category` → `WHERE main_category = $1` (`전체`는 필터 없음)
- 정렬 기본: `date DESC, news_id DESC`
- 인덱스 `idx_news_category_date` 활용 자동 적용됨
- 페이지네이션 미적용 — 한 카테고리 데이터 양이 많아지면 그때 도입 (기본 limit 만 걸어두는 것은 §9 참고)

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

### 8-4. 엔드포인트별 내부 처리

| 엔드포인트 | 내부 처리 |
|---|---|
| `GET /api/news` | DB 조회 (`main_category` 필터 + 정렬 + limit) → 목록 필드만 매핑 |
| `GET /api/news/{id}` | 1) DB row 로드 → 2) `summary` 가 NULL 이면 summarizer(:8001) 호출 후 `news_articles.summary` 업데이트 → 3) 같은 카테고리 코퍼스 로드 → 4) `analyze_article_statistics(use_llm=False, use_keybert=False, recent_n=4, top_n=8)` 호출 → 5) 응답 객체에 `mention_trend`/`related_keywords` 까지 합쳐 반환 |
| `POST /api/news/{id}/summary` | 강제 (재)생성. 운영/디버그용 |

> `stat_summary` 호출 부담을 줄이기 위해 응답에는 필요한 두 필드(`mention_trend`, `related_keywords`)만 추려서 전달. 내부 dict 의 나머지(`core_keyword`, `ai_insights` 등)는 일단 보류하고 추후 필요 시 노출.

---

## 9. 진행 순서 제안

1. **사용자 확인 사항 (전부 확정)**
   - ✅ 백엔드 스택: **FastAPI**
   - ✅ 요약 채우기 정책: **요청 시 생성 (온디맨드)**
   - ✅ `categories` 테이블 구조 확인 — `name VARCHAR(20)` 단일 컬럼
   - ✅ 요약 서비스 형태: **A. 별도 서비스** (backend 8000, summarizer 8001)
   - ✅ `stat_summary` 옵션: `use_llm=False`, `use_keybert=False`
2. **백엔드 골격 (포트 8000)**
   - `backend/` 폴더 생성 + 의존성 설치 + `.env` (DB / `SUMMARIZER_URL`)
   - `/health`, `/api/categories` 동작 확인
3. **목록 API**
   - `GET /api/news?category=...` (단순 배열, `date DESC` 정렬, 기본 limit)
   - 카테고리 정규화 (`전체` 무필터, `IT과학` ↔ `IT_과학`)
4. **요약 클라이언트**
   - `httpx` 로 `POST :8001/summarize/batch` 호출 모듈
   - timeout / 실패 시 `summary=None` 채로 응답하는 분기
5. **상세 API**
   - `GET /api/news/{id}`
   - `summary` 온디맨드 분기 + `stat_summary.analyzer` 직접 호출
   - 응답에 `mention_trend`, `related_keywords` 통합
6. **프론트 연결**
   - `newsApi.js` 의 더미 import 제거 + 실 fetch 활성화
   - `NewsGrid.vue` 의 모달 클릭 시 `fetchNewsById(item.id)` 호출 추가
   - 카테고리 `전체` 처리는 기존 코드 그대로 사용
7. **확인 후 정리(선택)**
   - `dummy_news.json`, 미사용 store/파일 정리

---

## 10. 결정 대기 항목 (Action Items)

- [x] **백엔드 스택**: FastAPI
- [x] **요약(`summary`) 처리 정책**: 요청 시 생성 (온디맨드)
- [x] **`categories` 테이블**: `name VARCHAR(20)` PK 단일 컬럼 (별도 표시명/정렬 없음)
- [x] **요약 서비스 형태**: A. 별도 서비스
  - backend: `http://localhost:8000`
  - summarizer: `http://localhost:8001`
- [x] **`stat_summary` 옵션**: `use_llm=False`, `use_keybert=False` (rule-based, 안정화 후 KeyBERT 확장 검토)

모든 결정 사항 확정됨. 사용자의 코드 작성 신호를 받으면 §4·§5·§8·§9 골격대로 바로 코드 진입 가능.

### 진입 시 코드 작업 1행 요약

> backend(:8000) 한 개를 새로 만들고, summarizer(:8001) 는 그대로 띄운 뒤,  
> `/api/categories`, `/api/news`, `/api/news/{id}` 세 엔드포인트가 §4 응답 스키마대로 동작하도록 구현.  
> 프론트는 `newsApi.js` 활성화 + `NewsGrid.vue` 의 모달 클릭에 `fetchNewsById` 호출만 추가.
