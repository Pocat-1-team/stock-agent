# News Data Pipeline & Semantic Retrieval

기업 뉴스, 산업 이슈, 거시경제 기사 및 공시 기반 텍스트 데이터를 수집·정제·벡터화(Vectorization)하는 작업 공간입니다.

본 파트는 단순 뉴스 크롤링이 아니라, 국내외 다양한 뉴스 소스와 공시 데이터를 통합하여 투자 판단에 필요한 정성적(Qualitative) 정보를 장기적으로 추적·분석 가능한 형태로 구조화하는 것을 목표로 합니다.

수집 및 적재된 데이터는 이후:

- Qual Worker Agent
- Strategist & Synthesizer Agent
- Curator Agent
- Guardrail & Evaluator Agent

등에서 사용됩니다.

---

# 담당 범위

- 국내외 금융/경제 뉴스 수집
- 산업·섹터별 뉴스 파이프라인 구축
- 기사 본문 정제 및 중복 제거
- 뉴스 메타데이터 구조화
- 임베딩(Vector Embedding) 생성 및 저장
- Vector DB(Chroma) 기반 Semantic Search 구축
- 기업·섹터·이벤트 기반 뉴스 분류
- 감성(Sentiment) 및 이벤트(Event Type) 전처리
- PostgreSQL + Chroma 이중 저장 구조 관리

---

# 데이터 수집 전략

본 프로젝트는:

- 과거 3~5년의 뉴스 흐름을 기반으로 기업의 장기 투자 맥락(Context)을 분석하는 것을 목표로 합니다.
- 단순 실시간 속보 수집보다, 투자 의사결정에 의미 있는 정성 데이터의 누적과 구조화를 우선합니다.
- 특정 기업뿐 아니라 섹터·매크로·경쟁사 뉴스까지 함께 수집하여 산업 단위 분석이 가능하도록 설계합니다.
- 네이버 뉴스 단일 의존이 아니라, 다양한 국내외 경제/증권 뉴스 소스를 병렬적으로 활용합니다.
- 중복 기사 및 복제 기사 문제를 고려하여 제목·본문 유사도 기반 중복 제거 로직을 적용합니다.

예시:

| 종목코드 | 기업명 | 뉴스 유형 | 기사 예시 |
|---|---|---|---|
| 005930 | 삼성전자 | 산업 트렌드 | AI 서버 투자 확대 |
| 000660 | SK하이닉스 | 실적 기대 | HBM 수요 증가 |
| 035420 | NAVER | 규제 이슈 | 플랫폼 규제 논의 |

---

# 국내외 뉴스 소스

| 소스 (Source) | 수집 대상 | 수집 방식 | 비고 |
|---|---|---|---|
| 네이버 금융 | 국내 증권 뉴스 | Crawling | 종목별 뉴스 허브 |
| 한국경제 | 산업/기업 뉴스 | Crawling | 정성 분석 핵심 |
| 매일경제 | 시장/거시 뉴스 | Crawling | 경제 흐름 분석 |
| 연합뉴스 | 속보/정책 뉴스 | RSS/API | 이벤트 감지 |
| Investing.com | 글로벌 시장 뉴스 | Crawling/API | 해외 매크로 |
| Reuters | 글로벌 기업 뉴스 | API/RSS | 해외 산업 이슈 |
| Yahoo Finance | 미국 증시 뉴스 | API | 글로벌 Peer 분석 |

---

# 데이터 처리 흐름 (ETL Pipeline)

1. 사용자 관심 섹터 선택
2. 관련 기업 Universe 생성
3. 기업명·종목코드 기반 뉴스 수집
4. 기사 본문 정제 및 광고/불필요 문구 제거
5. 제목·본문 기반 중복 기사 제거
6. 기업·섹터·이벤트 태깅
7. 감성 분석(Sentiment Scoring)
8. 임베딩 생성
9. PostgreSQL + Chroma 저장
10. 이후 RAG 및 Agent 연결

---

# 핵심 스키마 구조

뉴스 데이터는:

- 정형 메타데이터 → PostgreSQL
- 비정형 본문 + 임베딩 → Chroma(Vector DB)

로 분리 저장합니다.

## PostgreSQL

### news_article

뉴스 메타데이터 저장용 테이블

| 컬럼명 | 타입 | 설명 |
|---|---|---|
| news_id | UUID | 뉴스 고유 ID |
| stock_code | VARCHAR(6) | 관련 종목 |
| company_name | VARCHAR(100) | 기업명 |
| source | VARCHAR(50) | 언론사 |
| title | TEXT | 기사 제목 |
| published_at | TIMESTAMP | 발행 시각 |
| url | TEXT | 원문 링크 |
| event_type | VARCHAR(50) | 이벤트 유형 |
| sentiment_score | DECIMAL(3,2) | 감성 점수 |
| created_at | TIMESTAMP | 수집 시각 |

---

## Chroma Vector Collection

### news_chunks


news_chunks/
├── id (UUID)
├── news_id
├── stock_code
├── title
├── body
├── chunk_index
├── published_at
├── embedding (vector)

# 뉴스 전처리 규칙

| 전처리 항목 | 설명 |
|---|---|
| HTML 제거 | 광고/스크립트 제거 |
| 본문 정제 | 기자 정보·불필요 문구 제거 |
| 기사 중복 제거 | 제목 및 본문 유사도 비교 |
| 날짜 표준화 | UTC/KST 통일 |
| 종목 태깅 | 기업명 → stock_code 매핑 |
| 감성 분석 | positive / neutral / negative |
| 이벤트 분류 | 실적/규제/M&A/수주/산업트렌드 등 |

---

# 권장 파일 구성

datas/news/
├── README.md
├── requirements.txt
├── config.py
├── crawl_naver_news.py
├── crawl_hankyung.py
├── crawl_maekyung.py
├── crawl_yonhap.py
├── crawl_edaily.py
├── preprocess_news.py
├── embed_news.py
├── save_to_chroma.py
├── save_to_postgres.py
└── utils/
    ├── db_manager.py
    ├── text_cleaner.py
    ├── deduplicator.py
    ├── embedding_manager.py
    └── ticker_mapper.py

---

# 협업 규칙

- main 브랜치 직접 수정 금지
- 개인 브랜치에서 작업 후 PR 생성
- 크롤링 대상 사이트 변경 시 팀 공유 필수
- robots.txt 및 요청 빈도 고려
- 기사 원문 무단 재배포 금지
- .env 및 로컬 캐시 데이터 커밋 금지
- 임베딩 모델 변경 시 Agent 담당과 협의 필수

---

# MVP 목표
초기 MVP 목표:

- 국내 주요 경제 뉴스 소스 연동
- 섹터 기반 뉴스 자동 수집
- 뉴스 메타데이터 구조화
- Chroma 기반 Semantic Search 구축
- Qual Agent의 뉴스 기반 정성 분석 연결
- 기업/섹터 뉴스 흐름 추적 가능 구조 확보
- 향후 확장 계획 (Phase 2+)
- 국내 언론사 커버리지 확대
- 실시간 뉴스 수집 주기 최적화
- 뉴스 중복 제거 고도화
- 이벤트 기반 뉴스 클러스터링
- 뉴스 요약 및 핵심 리스크 추출
- 멀티모달 데이터(이미지·PDF 리포트) 연결
- 뉴스 기반 이상 탐지(Event Spike Detection)
