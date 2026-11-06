# 세컨드 브레인(듀얼 브레인) 검색 개선: 조사 결과와 추천

2026-11-06 · 이 문서는 **다른 LLM(자체 호스팅 LLM)이 읽고 구현 계획을 세우거나 코드를 만들 수 있게** 쓴 조사 자료입니다. 코드는 들어 있지 않습니다.

---

## 0. 이 문서를 읽는 LLM에게 (규칙)

1. 문서를 **위에서 아래로 순서대로** 읽는다. 건너뛰지 않는다.
2. 이 문서에 **없는 사실을 지어내지 않는다.** 모르면 "확인 필요"라고 쓰고 사용자에게 묻는다.
3. `?` 표시가 붙은 것은 **확인되지 않은 것**이다. 사실처럼 말하지 않는다.
4. 한 번에 **한 가지 일만** 한다. 계획 → 사용자 확인 → 구현 순서를 지킨다.
5. 사용자의 노트 내용을 **외부 서비스로 보내지 않는다.** 허용된 자체 LLM 엔드포인트만 쓴다.
6. 답은 항상 **6절의 출력 양식**에 맞춘다.

---

## 1. 한 줄 요약

- 노트가 **약 20만 토큰(문서 500쪽) 이하**면 검색 시스템 없이 전체를 프롬프트에 넣는 편이 낫다 (Anthropic 권고).
- 그보다 크면 **① 노트 구조 정리 → ② 한국어 키워드 검색 + LLM 질의 확장 → ③ 임베딩 → ④ 재정렬** 순서로, 단계마다 점수를 재며 올린다.
- **어떤 방식이든 질문 20개 평가표를 먼저 만든다.**

---

## 2. 먼저 사용자에게 물어볼 것

LLM은 구현에 들어가기 전에 아래를 **전부** 사용자에게 묻고 답을 받는다.

| 번호 | 질문 | 답에 따라 달라지는 것 |
|---|---|---|
| Q1 | 노트는 어디에 있나? (Obsidian 폴더, Git 저장소, 그 외) | 도구 선택 |
| Q2 | 노트는 몇 개이고, 합치면 대략 몇 쪽(또는 몇 MB)인가? | 3절 결정표 |
| Q3 | 자체 LLM 외에 **임베딩 API**가 있나? | 임베딩 단계 가능 여부 |
| Q4 | 사내 PC에서 Hugging Face, pip, npm 다운로드가 되나? | 로컬 모델 사용 가능 여부 |
| Q5 | 지금 검색이 실패한 사례 3개는? (질문, 찾고 싶던 노트) | 평가표의 시작점 |
| Q6 | 검색은 사람이 쓰나, 에이전트(Claude Code 등)가 쓰나? | MCP 필요 여부 |
| Q7 | "듀얼 브레인"의 구조는? (마크다운 지식베이스인가, AI 에이전트 메모리 시스템인가) | 전체 설계 |

---

## 3. 결정표 (이 순서로 위에서부터 확인)

| 조건 | 추천 | 이유 |
|---|---|---|
| 노트 전체가 20만 토큰 이하 | **검색 없이 전체 넣기**, 또는 `index.md`(목차)만 정리 | Anthropic: 이 규모 미만이면 RAG 대신 전체 포함이 낫다 |
| 노트가 많고 에이전트가 쓴다 | **구조화(4-1) + 한국어 키워드 검색(4-5)** 부터 | 가장 싸고 효과를 바로 잴 수 있다 |
| 위로도 부족하고 임베딩 API가 있다 | **하이브리드(키워드+벡터)** 로 확장 | 표현이 달라도 같은 뜻을 찾는다 |
| 임베딩 API가 없고 다운로드가 된다 | **로컬 임베딩 모델**(4-6)을 CPU로 시험 | 속도는 직접 재야 한다 `?` |
| 임베딩도 다운로드도 안 된다 | **키워드 검색 + LLM 질의 확장**에서 멈춘다 | 억지로 벡터를 넣지 않는다 |
| 완성품을 바로 써 보고 싶다 | **qmd(4-3)** 를 비교 기준선으로 설치 | 자체 LLM은 못 쓰지만 설치가 쉽다 |

---

## 4. 후보 카탈로그

모든 후보는 같은 양식입니다: **무엇 / 장점 / 단점 / 자체 LLM 사용 / 한국어 / 라이선스**.

### 4-1. 노트 구조화 (코드 불필요, 모든 방식의 기반)

- **무엇:** 노트마다 frontmatter(`description`, `aliases`, `tags`)를 쓰고, 폴더별 `index.md`(제목+한 줄 요약 목록)를 둔다.
- **근거:** [obsidian-wiki](https://github.com/Ar9av/obsidian-wiki)는 질의 때 본문보다 **제목·태그·요약을 먼저 읽는** 설계로 노트가 늘어도 비용이 거의 일정하다고 설명한다. 저자의 실험(38쪽 볼트)은 구조형 질문 정확도 83% 대 44%였으나 **조건당 n=2라 참고용**이다.
- **장점:** 비용 0, 어떤 LLM과도 동작, 이후 모든 검색 방식의 품질을 올린다.
- **단점:** 정리 작업이 사람 손(또는 LLM 초안 + 사람 확인)을 탄다.
- **자체 LLM:** 사용 가능. **한국어:** 문제 없음.

### 4-2. obsidian-wiki 방식 (참고 설계)

- **무엇:** 에이전트가 노트를 "한 번 정리해 연결된 위키로 만들어 두는" 프레임워크. `index.md`, `log.md`, `hot.md`, `[[위키링크]]`, 근거 표시(추출/추정/모호), 중복·깨진 링크 점검(lint) 포함.
- **장점:** 검색이 아니라 **정리 쪽에서 해결**한다. 임베딩이 필요 없고, 텍스트 검색만으로 동작한다고 문서에 적혀 있다.
- **단점:** 39개 스킬 규모라 처음엔 무겁다. 자체 LLM이 약하면 "위키 자동 정리"가 부정확할 수 있다 (제 추정).
- **라이선스:** MIT. **스타:** 약 3.6k. 그대로 쓰기보다 **구조 아이디어를 가져오는 것**을 추천.

### 4-3. qmd (완성형 로컬 검색 CLI)

- **무엇:** [tobi/qmd](https://github.com/tobi/qmd). 마크다운 폴더를 색인해 `qmd search`(BM25), `qmd vsearch`(벡터), `qmd query`(BM25+벡터+질의 확장+재정렬)를 제공. MCP 서버 포함.
- **장점:** 설치만 하면 하이브리드 검색과 MCP. 폴더별 설명(`qmd context`)과 컬렉션 관리. MIT.
- **단점:** 모든 모델이 **로컬 GGUF**이고, **OpenAI 호환 원격 LLM 설정은 문서에 없다.** 기본 임베딩(embeddinggemma-300M)은 영어 중심. 기본 청크 약 900토큰·15% 겹침.
- **자체 LLM:** **쓸 수 없음** (최신 버전은 재확인 필요 `?`).
- **한국어:** `QMD_EMBED_MODEL`을 Qwen3-Embedding 등으로 바꾸면 다국어. 바꾼 뒤 `qmd embed -f`로 전체 재임베딩. `QMD_FORCE_CPU=1`로 CPU 강제 가능(속도 미측정 `?`).
- **용도:** 비교 기준선 또는 에이전트용 MCP 검색 도구.

### 4-4. 노트 앱 플러그인 (Obsidian을 쓴다면)

[비교 글](https://unabyss.com/blog/best-ai-plugins-for-obsidian) 기준 (Khoj는 이 글에 없어 **미확인**):

| 플러그인 | 검색 | 자체 LLM | 가격/라이선스 | 비고 |
|---|---|---|---|---|
| Smart Connections | 로컬 임베딩, 설치 시 색인 | 글에 언급 없음 `?` | 핵심 무료, Pro 월 $30 | 관련 노트 찾기에 강함. 채팅은 분리됨 |
| Copilot for Obsidian | 글에 설명 없음 | 직접 API 키·로컬 모델 지원, OpenAI 호환 엔드포인트 언급 없음 `?` | 무료 + Plus 월 $14.99 | 데스크톱 에이전트 기능 |
| Local GPT | 선택 텍스트 작업 위주 | **Ollama 또는 OpenAI 호환 엔드포인트 가능** | MIT | 검색 도구는 아님 |

- **장점:** 설치만 하면 됨. **단점:** 회사 보안 정책상 플러그인 설치·유료 구독이 허용되는지 확인 필요. 한국어 품질은 확인하지 못함 `?`.

### 4-5. 한국어 키워드 검색 (BM25 + 형태소 분석)

- **문제:** "전구체가", "흡착하는"처럼 조사·어미가 붙어 어절 단위 색인은 "전구체"를 못 찾는다.
- **방법:** 색인과 질의 모두 형태소 분석기(Kiwi, `kiwipiepy`)로 쪼갠 단어를 BM25에 넣는다. [튜토리얼](https://langchain-opentutorial.gitbook.io/langchain-opentutorial/10-retriever/10-kiwi-bm25-retriever)이 있으나 **문서 7개로 상위 1건만 본 정성 비교**다.
- **저장소 후보:** SQLite FTS5(내장, 추가 설치 없음). 대안인 `trigram` 토크나이저는 이번에 시험하지 않았다 `?`.
- **장점:** 가볍고 GPU·임베딩 불필요, 고유명사·약어에 강함. **단점:** 표현이 다른 같은 뜻은 못 찾는다.
- **자체 LLM 결합:** 질문을 LLM이 동의어·영문 병기 검색어 3개로 바꿔 함께 검색(질의 확장).

### 4-6. 임베딩 모델 (벡터 검색용)

한국어 검색 벤치마크(MTEB-ko-retrieval 9개 과제 평균, [정리 글](https://www.data-dynamics.io/en/blog/embedding-model-guide)이 KURE 저장소 값을 인용한 것. **KURE 원문은 열지 못함**):

| 모델 | 유형 | nDCG@10 | Recall@10 |
|---|---|---|---|
| KURE-v2 | 토큰별 벡터 | 0.8160 | 0.8921 |
| KURE-v1 | 단일 벡터 | 0.7616 | 0.8629 |
| BGE-m3-ko | 단일 벡터 | 0.7547 | 0.8513 |
| BAAI/bge-m3 | 단일 벡터 | 0.7509 | 0.8588 |
| KoE5 | 단일 벡터 | 0.7337 | 0.8300 |

- KURE-v2는 토큰마다 벡터를 저장해 저장 공간과 구현이 다르다. 단일 벡터 모델이 다루기 쉽다.
- [Qwen3-Embedding](https://github.com/QwenLM/Qwen3-Embedding): 0.6B/4B/8B, 100개 이상 언어, 질의 앞에 `Instruct: {작업}\nQuery:{질문}` 지시문을 붙이는 방식(문서에는 불필요, 1~5% 개선이라고 설명). 라이선스는 해당 페이지에 없음.
- text-embedding-3-large 같은 상용 API는 위 표에 없어 **비교 불가**하며, 노트를 외부로 보내므로 이 환경에서는 제외.
- **CPU만 있을 때의 속도는 어느 모델도 측정하지 못했다 `?`.** 작은 모델부터 시험한다.

### 4-7. 재정렬(reranker)

- 후보 몇 십 개를 질문과 함께 읽고 순서를 다시 매기는 단계.
- [dragonkue/bge-reranker-v2-m3-ko](https://huggingface.co/dragonkue/bge-reranker-v2-m3-ko): 한국어 최적화, 약 0.6B, Apache-2.0. 금융 분야 한국어 벤치마크(AutoRAG)에서 top-k 1 F1 0.9123으로 비교 모델 중 1위(bge-reranker-v2-m3 0.8772). **분야가 다르고 CPU 속도는 모른다 `?`.**
- Qwen3 Reranker(0.6B/4B/8B)와 KURE-Reranker-base도 있다(후자는 검색 결과 제목만 확인).
- **자체 LLM으로 재정렬**하는 방법: 후보 20개의 제목·요약을 LLM에 보여 주고 관련 순서를 번호로 답하게 한다. 약한 LLM에는 "번호만 쉼표로" 같이 형식을 엄격히 고정한다.

### 4-8. 청크 문맥화 (Contextual Retrieval)

[Anthropic 글](https://anthropic.com/research/contextual-retrieval) 수치 (상위 20개 안에서 정답을 놓치는 비율, 기준 5.7%):

| 구성 | 실패율 | 감소 |
|---|---|---|
| 문맥 붙인 임베딩 | 3.7% | 35% |
| + 문맥 붙인 BM25 | 2.9% | 49% |
| + 재정렬 | 1.9% | 67% |

- **방법:** 청크마다 LLM이 "이 청크가 문서의 어느 부분에서 무엇에 대한 것인지" 50~100토큰 설명을 만들어 청크 앞에 붙인 뒤 색인.
- **주의:** Anthropic 자체 데이터와 Claude 3 Haiku 기준. 한국어 노트에서 같은 폭이라는 보장 없음. 자체 LLM이 약하면 설명이 부정확할 수 있고, **청크 수만큼 LLM 호출**이 필요해 색인이 오래 걸린다.
- **싼 대안:** LLM 없이 `노트 제목 > 섹션 제목 + description + tags`를 청크 앞에 붙이는 방법. 이것만으로도 문맥 일부를 준다 (제 추정, 효과는 직접 측정할 것).

### 4-9. 벡터 저장소

- 청크가 수천 개 이하이면 **SQLite에 벡터를 BLOB으로 저장하고 전부 비교**해도 되는 규모일 가능성이 크다 (제 추정, 직접 측정 필요).
- ChromaDB: 가장 쉽게 시작. 단, 인덱스가 전부 메모리에 올라가고 쓰기는 한 프로세스만 안전. ([비교 글](https://www.actian.com/blog/developer/comparing-embedded-vector-databases/), 이 글을 낸 회사가 경쟁 제품을 판매하므로 참고만)
- LanceDB: 텍스트·임베딩을 한 테이블에 저장, 하이브리드 검색 지원. 동시 쓰기가 많으면 실패할 수 있음.
- sqlite-vec: 이름만 알고 이번에 확인하지 못함 `?`.

### 4-10. 지식 그래프 방식 (GraphRAG, LightRAG)

- LightRAG는 청크마다 LLM으로 개체·관계를 뽑아 그래프를 만들고, 새 데이터는 기존 그래프에 합친다. GraphRAG는 새 데이터가 들어오면 그래프를 다시 만든다. ([설명 글](https://www.ai-bites.net/lightrag-simple-and-efficient-rival-to-graphrag/))
- 논문 결과는 **저자들의 자체 평가**(GPT-4o-mini, 청크 1200 고정)이고 수치는 그림에만 있다.
- **이 환경에서는 비추천 (제 판단):** 청크마다 LLM 호출이 필요해 색인 비용이 크고, 약한 LLM이 개체·관계를 잘못 뽑으면 그래프 전체가 오염된다. 위 단계로 해결이 안 될 때만 검토.

### 4-11. 마크다운 + 지식 그래프 MCP (Basic Memory)

- [Basic Memory](https://docs.basicmemory.com/technical/technical-information): 마크다운 파일이 원본이고 로컬 SQLite가 색인(전문 검색 + 의미 검색). 노트에 `[category] 관찰`과 `[[관계]]` 형식을 쓴다. MCP 도구 `search_notes`, `build_context`, `read_note`, `write_note`. 로컬 전용, 원격 서버·계정 불필요.
- **주의: 라이선스가 AGPL-3.0이다.** 회사 환경에서 사용 가능한지 확인 필요.
- 의미 검색에 어떤 임베딩 모델을 쓰는지, 원격 LLM을 쓸 수 있는지는 확인하지 못함 `?`.

### 4-12. 같은 이름의 다른 프로젝트 (주의)

"dual brain"으로 검색하면 AI 에이전트의 메모리 구조를 다루는 개념 프로젝트([multi-model dual-brain memory system](https://github.com/jihua3445/multi-model-dual-brain-memory-system))가 나온다. **열어 보지 않았다.** 사용자의 듀얼 브레인이 이쪽 구조이면 이 문서의 가정이 달라지므로 Q7을 반드시 묻는다.

---

## 5. 부품별 추천 요약

| 부품 | 1순위 | 대안 | 비고 |
|---|---|---|---|
| 노트 구조 | frontmatter + index.md | obsidian-wiki 아이디어 | 모든 단계의 기반 |
| 키워드 검색 | Kiwi + SQLite FTS5 | qmd `search` | 한국어는 형태소 분석 필수 |
| 질의 확장 | 자체 LLM | qmd 내장(로컬 1.7B) | 약한 LLM이면 3개 이하로 제한 |
| 임베딩 | 자체 임베딩 API가 있으면 그것 | BGE-M3 계열, KURE-v1, Qwen3-Embedding-0.6B | CPU 속도 직접 측정 |
| 융합 | RRF(순위 합산) | 점수 가중합 | RRF는 점수 정규화가 필요 없어 단순 |
| 재정렬 | 자체 LLM 번호 정렬 | bge-reranker-v2-m3-ko | 마지막 단계에 추가 |
| 청크 문맥 | 제목·description 붙이기 | LLM 문맥화 | LLM 문맥화는 호출량이 큼 |
| 에이전트 연결 | MCP | 직접 CLI 호출 | Q6 답에 따라 |

---

## 6. LLM이 쓸 출력 양식

계획이나 제안을 말할 때 **항상 아래 양식**을 쓴다.

```
[현재 단계] 번호와 이름
[목표] 한 문장
[할 일] 1. ... 2. ... (최대 5개, 각 한 줄)
[완료 기준] 숫자로 (예: 평가표 recall@5 0.7 이상)
[사용자에게 확인할 것] 질문 목록 (없으면 "없음")
[확인되지 않은 가정] 목록 (없으면 "없음")
```

---

## 7. 단계별 계획

각 단계는 **직전 단계의 점수를 넘지 못하면 다음으로 가지 않고** 원인을 먼저 본다.

| 단계 | 할 일 | 완료 기준 |
|---|---|---|
| 0. 평가표 | 질문 20개와 정답 노트 목록 작성 (8절) | 현재 방식의 점수 기록 |
| 1. 구조화 | frontmatter 규약 적용, 폴더별 `index.md` | 같은 20개로 점수 재측정 |
| 2. 키워드 검색 | Kiwi + FTS5 색인, LLM 질의 확장 | 1단계 대비 상승 |
| 3. 벡터 | 임베딩 추가, RRF로 합침 | 질문 종류별(한국어/영어/약어) 점수 비교 |
| 4. 재정렬·문맥화 | 필요할 때만 추가 | 속도 대비 이득이 있을 때만 유지 |
| 5. 에이전트 연결 | MCP 등으로 노출 | 실제 업무 질문으로 확인 |

**frontmatter 규약:**

```yaml
---
name: 영문-slug
description: 한 줄 요약 (한·영 용어 병기)
aliases: [영문 풀네임, 약어, 한글 별칭]
tags: [주제1, 주제2]
---
```

- 한 노트에 한 주제. 섹션 제목은 구체적으로("메모"보다 "SevenNet 모달별 오차").
- 약어는 풀어 쓴 형태를 한 번 적는다(NEB → nudged elastic band, 전이상태 탐색).
- 긴 노트는 맨 위에 3~5줄 요약.

---

## 8. 평가 방법

1. 실제로 찾고 싶었던 질문 20개를 만든다. 한국어·영어·약어를 섞고, **지금 검색이 실패했던 사례를 꼭 넣는다.**
2. 질문마다 정답 노트(1~3개)를 사람이 정한다. **LLM이 정답을 정하지 않는다.**
3. 각 방식으로 상위 5개를 뽑아, 정답이 **5위 안에 들어간 질문의 비율(recall@5)** 과 정답이 몇 위인지 표로 적는다.
4. 방식을 바꿀 때마다 같은 질문으로 다시 하고, 질문 종류별로 나눠 약한 곳을 본다.

---

## 9. 약한 LLM에게 일을 시키는 요령 (사용자용)

일반적인 실무 요령이며 **이번 조사에서 출처를 확인한 것은 아닙니다.**

- 한 번에 **하나의 작업**만 준다. "검색 시스템 만들어줘" 대신 "5번 단계의 색인 스크립트만 작성해줘".
- **출력 양식을 고정**한다(6절). 번호·표·JSON처럼 확인하기 쉬운 형식으로.
- **좋은 예시와 나쁜 예시**를 하나씩 보여 준다.
- 긴 문서를 한꺼번에 주지 말고 **필요한 절만** 붙여 준다.
- 결과는 **직접 실행해서 확인**한다. 그럴듯하지만 틀린 설정이 나올 수 있다.
- 출처 링크나 수치를 말하면 **원문과 대조**한다. 문서에 없는 모델·옵션 이름이 나오면 의심한다.
- 계획 단계에서 사람이 승인한 뒤에만 구현하게 한다.

---

## 10. 붙여 넣을 지시문 (짧게 나눔)

**지시문 1: 파악**
```
이 문서의 0절 규칙을 지켜라. 2절의 Q1~Q7 질문을 나에게 하나씩 물어라.
내가 모두 답하면 3절 결정표로 어떤 줄에 해당하는지 말해라. 구현은 하지 마라.
```

**지시문 2: 노트 정리 초안**
```
내가 주는 노트 1개를 읽고 7절 frontmatter 규약에 맞는 description, aliases, tags 초안을 써라.
노트 본문에 있는 정보만 써라. 없는 내용을 추가하지 마라. 모르면 "확인 필요".
```

**지시문 3: 평가 질문 후보**
```
내가 주는 노트 목록의 제목과 description을 보고 8절 기준으로 질문 후보를 노트당 1개씩 써라.
정답 노트는 정하지 마라. 내가 정한다.
```

**지시문 4: 계획 작성**
```
3절에서 고른 줄과 7절 단계표를 바탕으로, 6절 양식으로 다음 단계 계획 하나만 써라.
완료 기준은 숫자로 써라.
```

---

## 11. 확인하지 못한 것

- qmd 최신 버전의 원격 LLM 지원 여부 (위키에는 없음)
- KURE 저장소 원문과 KURE-Reranker 상세 (접속 제한 또는 제목만 확인), 한국어 임베딩 표는 2차 인용
- 모든 로컬 모델의 **CPU 속도**
- Khoj, sqlite-vec 상세
- Smart Connections·Copilot의 자체 LLM 연결 방식과 한국어 품질
- Basic Memory의 임베딩 모델과 원격 LLM 사용 여부
- 자체 LLM의 정확한 성능: "다소 약함"이라는 사용자 설명만 있음
- 문서의 수치(Anthropic 67% 감소 등)는 해당 출처의 자체 실험이고 이 환경에서 재현하지 않았다

---

## 출처 (2026-11-06 열람)

- [Anthropic, Contextual Retrieval](https://anthropic.com/research/contextual-retrieval)
- [tobi/qmd](https://github.com/tobi/qmd), [qmd 위키](https://github.com/tobi/qmd/wiki)
- [Qwen3-Embedding](https://github.com/QwenLM/Qwen3-Embedding)
- [임베딩 모델 선택 가이드(한국어 벤치마크 인용)](https://www.data-dynamics.io/en/blog/embedding-model-guide)
- [dragonkue/bge-reranker-v2-m3-ko](https://huggingface.co/dragonkue/bge-reranker-v2-m3-ko)
- [Kiwi BM25 튜토리얼](https://langchain-opentutorial.gitbook.io/langchain-opentutorial/10-retriever/10-kiwi-bm25-retriever)
- [obsidian-wiki](https://github.com/Ar9av/obsidian-wiki), [brain-wiki](https://github.com/brain-wiki/brain-wiki)
- [Obsidian AI 플러그인 비교](https://unabyss.com/blog/best-ai-plugins-for-obsidian)
- [Basic Memory 기술 문서](https://docs.basicmemory.com/technical/technical-information)
- [LightRAG 설명](https://www.ai-bites.net/lightrag-simple-and-efficient-rival-to-graphrag/)
- [임베디드 벡터 DB 비교(Actian)](https://www.actian.com/blog/developer/comparing-embedded-vector-databases/)
- 제목만 확인: [multi-model dual-brain memory system](https://github.com/jihua3445/multi-model-dual-brain-memory-system), [KURE](https://github.com/nlpai-lab/KURE)(미열람), [KURE-Reranker-base](https://huggingface.co/nlpai-lab/KURE-Reranker-base)
