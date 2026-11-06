# 세컨드 브레인(듀얼 브레인) 검색 개선: 자체 호스팅 LLM 기준 설계

2026-11-06 · 사람과 **자체 호스팅 LLM**이 함께 읽는 문서입니다. LLM은 6절(지시문)과 5절(평가)부터 읽으면 됩니다.

## 0. 결론

1. **노트가 많지 않으면(약 20만 토큰, 문서 500쪽 이하) 검색 시스템이 필요 없을 수 있습니다.** Anthropic은 이 규모 미만이면 지식베이스 전체를 프롬프트에 넣는 편이 낫다고 권합니다.
2. 그보다 크면 **한국어 형태소 분석(Kiwi) + SQLite FTS5(BM25) + LLM 질의 확장**부터 시작합니다. 벡터와 GPU 없이 하루면 만들고, 이 저장소의 `code/`에 만들어 두었습니다.
3. 효과를 숫자로 확인한 뒤에 **임베딩(KURE 또는 BGE-M3)과 청크 문맥화(contextual retrieval), 재정렬**을 단계적으로 더합니다.
4. **qmd는 좋은 도구이지만 자체 호스팅 LLM을 쓰지 못합니다.** 문서에서 원격 LLM 설정을 찾지 못했고 모든 모델이 로컬 GGUF입니다. 그래서 "자체 LLM으로 바꾼다"는 목적에는 직접 만드는 쪽이 맞습니다. qmd는 비교 기준선이나 MCP 검색 도구로 병행하세요.
5. 무엇을 하든 **질문 20개 평가표**를 먼저 만드세요. 그것이 없으면 개선인지 알 수 없습니다.

## 1. 전제 (틀렸으면 알려 주세요)

- 노트는 마크다운이고 Git으로 관리하며, 한국어와 영어가 섞여 있다.
- LLM은 자체 호스팅 API(OpenAI 호환 형식으로 추정 `?`)로만 쓴다. 임베딩 API가 있는지는 모른다 `?`
- 작업 PC에는 GPU가 없다. 노트 내용은 외부로 보내지 않는다.
- 이미 Claude Code를 자체 LLM 게이트웨이로 쓰는 환경이 있으므로, 에이전트가 파일을 직접 grep·read 하는 방식은 지금도 가능하다.

## 2. 조사로 확인한 사실

**검색 품질을 올리는 요소 (Anthropic, [Contextual Retrieval](https://anthropic.com/research/contextual-retrieval))**

| 구성 | 검색 실패율(상위 20개) | 기준 대비 감소 |
|---|---|---|
| 기본 임베딩 | 5.7% | - |
| 청크에 문맥을 붙여 임베딩 | 3.7% | 35% |
| 위 + 문맥을 붙인 BM25 | 2.9% | 49% |
| 위 + 재정렬 | 1.9% | 67% |

- 청크마다 LLM이 50~100토큰의 "이 청크가 문서의 어디에서 무슨 얘기인지" 설명을 붙인 뒤 색인하는 방식입니다. 일회성 비용은 문서 100만 토큰당 약 $1.02(Claude 3 Haiku 기준, 800토큰 청크 가정)이고, 자체 LLM이면 호출 시간만 듭니다.
- 150개를 뽑아 재정렬한 뒤 20개를 넘겼을 때가 5개·10개보다 좋았습니다. 단, 이 수치는 Anthropic의 자체 데이터셋 결과이고 한국어 노트에서 같은 폭이 나온다는 보장은 없습니다.
- 한국어 문서 평가는 아래 임베딩 표를 보세요.

**한국어 임베딩 (MTEB-ko-retrieval 9개 과제 평균, [데이터다이내믹스 정리 글](https://www.data-dynamics.io/en/blog/embedding-model-guide)이 KURE 저장소 값을 인용한 것으로, 저는 KURE 원문을 열지 못했습니다)**

| 모델 | 유형 | nDCG@10 | Recall@10 |
|---|---|---|---|
| KURE-v2 | 토큰별 벡터(late-interaction) | 0.8160 | 0.8921 |
| KURE-v1 | 단일 벡터 | 0.7616 | 0.8629 |
| BGE-m3-ko | 단일 벡터 | 0.7547 | 0.8513 |
| BAAI/bge-m3 | 단일 벡터 | 0.7509 | 0.8588 |
| KoE5 | 단일 벡터 | 0.7337 | 0.8300 |

- 상용 API(text-embedding-3-large 등)는 이 표에 없어서 비교할 수 없습니다. CPU만 쓴다면 작은 모델이 현실적이고, KURE-v2는 토큰마다 벡터를 저장해 저장 공간과 구현이 달라집니다.
- [Qwen3-Embedding](https://github.com/QwenLM/Qwen3-Embedding)은 0.6B/4B/8B가 있고 100개 이상 언어를 지원하며, 질의 앞에 `Instruct: {작업}\nQuery:{질문}` 형식의 지시문을 붙이는 방식입니다(문서에는 불필요, 1~5% 개선이라고 설명). 재정렬 모델(Reranker)도 0.6B/4B/8B로 제공됩니다. 라이선스는 해당 페이지에 적혀 있지 않았습니다.

**한국어 키워드 검색**

- 조사와 어미가 붙어 있어서(예: "전구체가", "흡착하는") 어절 단위로 색인하면 "전구체"로 검색해도 놓칩니다. Kiwi로 형태소를 나눈 뒤 BM25에 넣는 방식이 [튜토리얼](https://langchain-opentutorial.gitbook.io/langchain-opentutorial/10-retriever/10-kiwi-bm25-retriever)에 있습니다. 단 이 튜토리얼은 문서 7개로 상위 1건만 본 정성 비교입니다.
- 이 저장소의 `code/`로 장난감 데이터(노트 4개, 질문 6개)에서 같은 비교를 직접 돌렸습니다. Kiwi는 recall@5 1.00, 어절 단위는 0.83이었습니다. 규모가 너무 작아 방향만 보여 주는 결과입니다.
- 대안으로 FTS5 `trigram` 토크나이저가 있으나 이번에는 시험하지 않았습니다.

**qmd ([tobi/qmd](https://github.com/tobi/qmd), 위키·README 확인)**

- `qmd search`(BM25), `qmd vsearch`(벡터), `qmd query`(BM25+벡터+질의 확장+재정렬). 기본 청크 약 900토큰·15% 겹침. MCP 서버 제공. MIT 라이선스.
- 모델은 모두 로컬 GGUF(임베딩 embeddinggemma-300M, 재정렬 qwen3-reranker-0.6b, 질의 확장 1.7B). `index.yml`로 모델을 `hf:` URI나 로컬 파일로 바꿀 수 있으나, **OpenAI 호환 원격 엔드포인트나 API 키 설정은 문서에 없습니다.**
- `QMD_EMBED_MODEL`로 Qwen3-Embedding 등을 쓰면 다국어를 지원하고, 바꾼 뒤에는 `qmd embed -f`로 다시 임베딩해야 합니다. 노트의 폴더별 설명을 붙이는 `qmd context` 기능도 있습니다.
- `QMD_FORCE_CPU=1`로 CPU 강제가 가능합니다. 단 CPU에서의 속도는 직접 측정하지 못했습니다.

**노트를 에이전트가 쓰기 좋게 구조화하는 방식 ([obsidian-wiki](https://github.com/Ar9av/obsidian-wiki), MIT)**

- 질의 시 본문보다 **제목·태그·요약을 먼저 읽고**, `index.md`·`log.md`·`hot.md`로 목차를 유지해 노트가 늘어도 비용이 거의 일정하다는 설계입니다. 저자는 38쪽 볼트에서 구조형 질문이 정확도 83% 대 44%(일반 에이전트)였다고 쓰지만, 조건당 n=2인 작은 실험이라 참고만 하세요.
- 선택적으로 QMD 의미 검색을 붙일 수 있고, 임베딩 없이 텍스트 검색만으로도 동작합니다.
- [brain-wiki](https://github.com/brain-wiki/brain-wiki)(Apache-2.0)는 검색 방식이 문서에 안 적혀 있고 알파 단계에 스타가 0개라서 지금은 참고용입니다.

## 3. 선택지 비교

| 선택지 | 설명 | 장점 | 단점 |
|---|---|---|---|
| **P. 구조화만** (인덱스 노트 + frontmatter) | 에이전트가 `index.md`를 먼저 읽고 grep으로 좁힘 | 코드 0줄, 자체 LLM 그대로 활용 | 노트가 수천 개를 넘으면 목차 유지가 부담 |
| **A. qmd 그대로** | 로컬 모델 하이브리드 검색 | 설치만 하면 하이브리드·MCP | 한국어 기본 모델 약함, 모델 다운로드(사내망에서 막힐 수 있음 `?`), 자체 LLM 못 씀 |
| **B. qmd + Qwen3-Embedding** | A에서 임베딩만 교체 | 설정 몇 줄로 한국어 개선 | 전체 재임베딩, CPU 속도 `?`, 자체 LLM 못 씀 |
| **C. 직접 만든 파이프라인** (`code/`) | Kiwi+FTS5+RRF, 질의 확장·재정렬은 자체 LLM | 자체 LLM·데이터 모두 사내에 머묾, 한국어 조절 가능 | 직접 유지보수, LLM 호출만큼 느림 |
| **D. C에 임베딩·문맥화 추가** | C + 벡터 + 청크 문맥 | 위 표의 개선 폭을 기대 | 임베딩 API 또는 CPU 모델 필요, 색인 시간 증가 |

## 4. 추천 로드맵

| 단계 | 할 일 | 기대 효과 | 확인 기준 |
|---|---|---|---|
| 0 (30분) | 평가용 질문 20개와 정답 노트 작성 (5절) | 기준선 확보 | 현재 방식의 recall@5 기록 |
| 1 (반나절) | 노트 정리: frontmatter 규약(아래), `index.md` 목차 | 에이전트가 더 정확히 찾음 | 같은 20개로 재측정 |
| 2 (하루) | `code/`로 Kiwi+FTS5 색인, 자체 LLM 질의 확장 | 조사·어미·동의어 문제 해소 | 1단계 대비 상승 여부 |
| 3 (2~3일) | 임베딩 추가(자체 API가 있으면 그것, 없으면 CPU에서 BGE-M3 계열 시험), RRF | 표현이 다른 같은 뜻 검색 | 한국어·영어·약어 질문별로 분해해 비교 |
| 4 (선택) | 청크 문맥화(LLM이 청크별 설명 생성), 재정렬 | Anthropic 보고 기준 추가 감소 | 호출 시간·품질 대비 이득이 있을 때만 유지 |
| 5 (선택) | MCP 서버로 감싸 Claude Code 등에서 호출 | 에이전트가 검색 도구로 사용 | 실제 업무 질문으로 확인 |

각 단계에서 올라가지 않으면 다음 단계로 가지 말고 원인(청크가 길다, 제목이 부실하다, 질문이 모호하다)을 먼저 보세요.

**노트 frontmatter 규약 (검색이 이 정보에 크게 의존합니다)**

```yaml
---
name: precursor-adsorption-mlip     # 파일 이름과 같은 영문 slug
description: 전구체 흡착 에너지를 MLIP로 계산한 메모 (한 줄 요약, 한·영 용어 병기)
aliases: [precursor adsorption, E_ads, 흡착 에너지]
tags: [mlip, ald]
---
```

- 한 노트에 한 주제, 섹션 제목은 구체적으로 씁니다("메모"보다 "SevenNet 모달별 오차").
- 약어는 풀어 쓴 형태를 한 번 적습니다(NEB → nudged elastic band, 전이상태 탐색).
- 긴 노트는 맨 위에 3~5줄 요약을 둡니다.

## 5. 평가 방법

1. 실제로 찾고 싶었던 질문 20개와 정답 노트를 `qa.json`에 적습니다: `[{"q": "흡착에너지 계산", "gold": ["adsorption.md"]}]`
2. 한국어, 영어, 약어·고유명사 질문을 섞고, 실제로 검색에 실패했던 사례를 꼭 넣습니다.
3. `python sbsearch.py eval qa.json --db sb.sqlite`로 recall@5와 MRR을 봅니다.
4. 방식을 바꿀 때마다 같은 질문으로 다시 돌리고, 질문 종류별로 나눠서 어디가 약한지 봅니다.

## 6. LLM에게 시킬 일 (자체 호스팅 LLM용 지시문)

```
너는 내 마크다운 노트 검색 개선을 돕는다.
제약: 노트 내용은 외부로 보내지 않는다. GPU 없음. LLM은 자체 호스팅 API(OpenAI 호환 추정).
노트는 한국어·영어 혼용, Git 관리.

할 일:
1. 첨부한 code/sbsearch.py를 읽고, 내 노트 폴더에 맞게 색인 대상·청크 크기를 조정하는 방법을 제안해라.
2. 내 노트 폴더 구조를 보고 4절의 frontmatter 규약에 맞지 않는 노트 목록과 보완할 description/aliases 초안을 만들어라.
   (내용을 지어내지 말고, 노트 본문에 있는 정보만 써라.)
3. 질문 20개 평가표(qa.json)의 후보 질문을 노트별로 제안해라. 정답은 내가 확정한다.
4. 모르는 것은 "확인 필요"라고 적고, 임의로 사실을 만들지 마라.
```

## 7. 코드 사용법 (`code/`)

```
pip install -r requirements.txt            # kiwipiepy
python sbsearch.py index ~/notes --db sb.sqlite
python sbsearch.py search "흡착 에너지 정리한 노트" --db sb.sqlite --no-llm
# 자체 LLM 질의 확장·재정렬을 켜려면 (OpenAI 호환 엔드포인트)
export SB_LLM_BASE_URL=https://llm.example.com/v1  SB_LLM_MODEL=<모델명>  SB_LLM_API_KEY=<키>
# 임베딩을 쓰려면 (선택)
export SB_EMBED_BASE_URL=...  SB_EMBED_MODEL=...  SB_EMBED_API_KEY=...
```

- 테스트 7개가 통과합니다(`python -m pytest code/tests`). 내용은 Kiwi 분해, 청크·frontmatter 파싱, Kiwi 대 어절 비교, RRF, 가짜 LLM을 쓴 질의 확장·재정렬, 가짜 임베딩 경로입니다.
- **실제 자체 LLM·임베딩 엔드포인트와 실제 노트로는 시험하지 않았습니다.** 엔드포인트 응답 형식이 OpenAI와 다르면 `_post` 부분을 고쳐야 합니다. 벡터 검색은 파이썬 순수 계산이라 노트 청크가 수만 개를 넘으면 느립니다(그 규모면 sqlite-vec 등 교체 필요, 이번에 시험하지 않음).
- LLM 재정렬은 후보 20개 요약을 한 번에 보내는 단순 방식이고, 출력 파싱이 틀리면 원래 순서를 유지합니다.

## 8. 확인이 필요한 것

- 노트는 어디에 있고(Obsidian, 이 저장소 등) 몇 개, 총 몇 토큰인가? 20만 토큰 미만이면 0번 결론으로 충분할 수 있습니다.
- 자체 임베딩 API가 있는가? 없다면 사내망에서 Hugging Face 모델 내려받기가 가능한가?
- "듀얼 브레인"이 위의 일반적인 세컨드 브레인(마크다운 지식베이스)이 맞는가? 검색에서 [multi-model dual-brain memory system](https://github.com/jihua3445/multi-model-dual-brain-memory-system)이라는 AI 에이전트 메모리 개념 프로젝트도 나왔는데 열어 보지는 않았습니다. 이쪽 구조라면 알려 주세요.
- qmd가 원격 LLM을 지원하는지 최신 버전에서 다시 확인이 필요합니다(이번에는 위키에서 찾지 못함).
- KURE 원문 저장소는 접속 제한으로 열지 못해, 임베딩 표는 2차 인용입니다.

## 출처 (2026-11-06 열람)

- [Anthropic, Contextual Retrieval](https://anthropic.com/research/contextual-retrieval)
- [tobi/qmd 저장소](https://github.com/tobi/qmd), [qmd 위키](https://github.com/tobi/qmd/wiki)
- [Qwen3-Embedding](https://github.com/QwenLM/Qwen3-Embedding)
- [임베딩 모델 선택 가이드(한국어 벤치마크 인용)](https://www.data-dynamics.io/en/blog/embedding-model-guide)
- [Kiwi BM25 튜토리얼](https://langchain-opentutorial.gitbook.io/langchain-opentutorial/10-retriever/10-kiwi-bm25-retriever)
- [obsidian-wiki](https://github.com/Ar9av/obsidian-wiki), [brain-wiki](https://github.com/brain-wiki/brain-wiki)
- 제목만 확인: [multi-model dual-brain memory system](https://github.com/jihua3445/multi-model-dual-brain-memory-system), [KURE](https://github.com/nlpai-lab/KURE)(접속 제한으로 미열람)
