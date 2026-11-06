# 구축 가이드: 자체 호스팅 LLM으로 바로 실행하기

이 문서는 `code/` 폴더의 `ald_extract` 패키지(테스트 10개 통과)를 자체 호스팅 DeepSeek·비전 모델에 연결해 돌리는 절차입니다. 테스트는 가짜 LLM과 합성 PDF로 로직만 검증했고, 실제 자체 호스팅 모델의 정확도는 아직 측정 전입니다.

**GPU 없는 PC 기준입니다.** 키트는 순수 파이썬(CPU)과 API 호출만 쓰므로 GPU 없이 그대로 돕니다. 무거운 처리는 모두 LLM·비전 API가 하고, PC에서는 PDF 파싱과 검증만 합니다. GPU가 필요한 로컬 파서(PaddleOCR-VL, MinerU)는 쓰지 말고, 스캔본이 많을 때만 자체 호스팅 비전 모델로 페이지 이미지를 읽게 `parse_pdf`를 교체하세요. 대량 처리는 API 호출 수와 속도 제한이 병목이므로, 처음에는 `--no-figures`로 표·본문만 10편 돌려 시간과 호출량을 먼저 측정해 보길 권합니다.

## 0. 시작 전 확인 (5분)

- 자체 호스팅 텍스트 LLM의 **엔드포인트 주소, 모델명, API 키**: 주소가 `.../v1/chat/completions` 형태(OpenAI 호환)인지 확인합니다. DeepSeek은 OpenAI 형식을 지원합니다.
- 자체 호스팅 비전 모델의 **엔드포인트와 모델명**: 이미지를 `image_url`(base64 data URL)로 받는지 확인합니다. 안 받으면 `llm.py`의 `image_message`만 고칩니다.
- 이용 정책: 논문 PDF를 모델에 넣어도 되는지(출판사 약관 포함), 파이썬 패키지를 설치해도 되는지 확인합니다.
- Python 3.10 이상.

## 1. 설치

```
unzip ald_extract_kit.zip && cd ald_extract_kit
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q            # 외부 API 없이 10개 통과해야 정상
```

## 2. 환경 설정

```
cp .env.example .env
# .env 에 입력
ALD_LLM_BASE_URL=https://<LLM 서버 주소>/v1
ALD_LLM_MODEL=<모델명>
ALD_LLM_API_KEY=<키>
ALD_VLM_BASE_URL=https://<비전 서버 주소>/v1
ALD_VLM_MODEL=<비전 모델명>
ALD_VLM_API_KEY=<키>
ALD_FIG_SAMPLES=3
```

`.env`는 git에 올리지 마세요(키 유출 방지). 비전 변수를 비워 두면 그림 추출만 건너뜁니다.

## 3. 연결 점검 (본 작업 전에 반드시)

```
python - <<'PY'
from ald_extract.config import Config
from ald_extract.llm import OpenAICompatLLM
c = Config.from_env()
print(OpenAICompatLLM(c.llm).chat([{"role":"user","content":"JSON으로 {\"ok\":true} 만 출력"}], json_mode=True))
PY
```

- 오류가 `response_format`이면: 서버가 JSON 모드를 지원하지 않는 것입니다. `extract.py`의 `llm.chat(..., json_mode=True)`를 `json_mode=False`로 바꾸세요(파서가 코드 펜스와 잡설을 처리합니다).
- 인증 오류면 키와 헤더 형식(`Authorization: Bearer`)을 확인합니다. 게이트웨이가 다른 헤더를 쓰면 `llm.py`의 `headers`만 수정합니다.

## 4. 실행

```
ald-extract run ./papers/paper1.pdf        # 1편
ald-extract batch ./papers                 # 폴더 전체(한 편 실패해도 계속)
ald-extract batch ./papers --no-figures    # 그림 제외(빠름)
```

처리 순서는 보고서의 파이프라인 그림과 같습니다: 파싱 → 표·본문 구조화(자체 호스팅 DeepSeek, 논문 전체를 한 번에) → 그림 수치화(자체 호스팅 비전 모델 N회) → 검증 → 저장. 결과는 `data/records/<paper_id>.json`에 쌓입니다.

## 5. 검증 결과 읽는 법

각 수치는 `source.page`와 `source.quote`(원문 인용)를 달고 다니며, 검증 단계가 아래 순서로 점검합니다.

| 플래그 | 의미 | 조치 |
|---|---|---|
| `v:quote_not_found` | 모델이 쓴 근거 문장이 PDF 텍스트에 없음 (환각 의심) | 검토 큐에서 원문 확인, 대개 삭제 |
| `v:value_not_in_quote` | 값이 인용 문장 안에 없음 | 값 오독 가능성, 원문 대조 |
| `v:out_of_range` | 물리 범위 이탈 (예: GPC 0.005~1 nm/cycle 밖) | 단위 오류(Å↔nm) 우선 의심 |
| `v:figure_agrees` | 그림에서 읽은 값과 본문 값이 7% 이내 일치 | 신뢰도 가산 |
| `high_variance` (그림) | N회 반복 추출 간 편차 10% 초과 | 그 그림 값은 사람이 확인 |
| `no_valid_samples` (그림) | 비전 모델이 읽지 못함 | 수동 디지타이징(WebPlotDigitizer) |

```
ald-extract review      # 신뢰도 0.7 미만·플래그 항목만 JSONL로 출력
```

사람은 이 큐만 보면 됩니다. 전수 확인이 아니라 의심 항목만 확인하는 구조입니다.

## 6. 정확도 측정 (자체 호스팅 모델을 믿기 전에)

1. 논문 20~30편을 골라, 손으로 `PaperRecord` 형식 JSON(`gold/<paper_id>.json`)을 만듭니다. 처음엔 표의 핵심 값(GPC, 두께, 온도, 사이클)부터 시작하세요.
2. `ald-extract batch`로 같은 논문을 추출합니다(파일명 stem = `paper_id`).
3. 비교:

```
ald-extract eval ./gold
```

출력의 `micro_precision / micro_recall / micro_f1`과 `recall_by_method`(text/table/figure별)를 봅니다. 일치 기준은 측정 이름 + 값(상대오차 1% 이내) + 단위입니다. 보고서의 우선순위 전략대로 표·본문 값(T1)을 먼저 올리고, 그림(T3)은 따로 평가하세요.

모델·프롬프트·파서를 바꿀 때마다 같은 gold로 다시 돌려 점수가 오르는지 확인하는 것이 개선의 기본 루프입니다.

## 7. 데이터베이스로 내보내기

```
ald-extract export-csv out.csv           # 엑셀/판다스 분석용
ald-extract export-cypher out.cypher     # Neo4j 그래프용
cypher-shell -u neo4j -p <pw> -f out.cypher
```

`export.py`가 만드는 그래프는 보고서의 스키마와 같습니다: Paper-REPORTS→Process, Process-USES→Precursor/CoReactant, -DEPOSITED_ON→Substrate, -DEPOSITS→Material, -HAS→Measurement(값·단위·페이지·인용·신뢰도). JSON이 원본이고 CSV·그래프는 언제든 재생성하는 파생 뷰입니다. Neo4j에 바로 밀어 넣으려면 `pip install -e ".[neo4j]"` 후 `export.push_neo4j`를 쓰세요.

예시 질의(온도별 GPC):

```
MATCH (p:Process)-[:USES]->(:Precursor {id:'tma'}), (p)-[:HAS]->(m:Measurement {name:'growth_per_cycle'})
WHERE m.confidence >= 0.7
RETURN p.temp_c, m.norm_value ORDER BY p.temp_c
```

## 8. 내 환경에 맞게 고칠 곳

| 상황 | 고칠 파일·위치 |
|---|---|
| 엔드포인트가 OpenAI 호환이 아님 | `llm.py` `OpenAICompatLLM.chat` 교체 |
| 스캔 PDF·복잡한 표가 많음 | `parse.py` `parse_pdf`를 자체 호스팅 비전 모델/PaddleOCR-VL/MinerU로 교체 (같은 `ParsedPaper` 반환) |
| ASD·특정 공정 항목 추가 | `schema.py`(필드)와 `verify.py`의 `UNIT_RULES`, `RANGES` |
| 전구체 이름 표기 불일치 | `export.py` `canon()`을 동의어 사전으로 확장 |
| 논문이 너무 길어 컨텍스트 초과 | `extract.py`에서 섹션 단위로 나눠 호출 후 병합 |
| 텍스트 모델이 이미지도 받는 변종(v4.1-flash 등) | 그림용 `vlm` 엔드포인트를 그 모델로 지정 |

## 9. 문제 해결

- 스키마 검증이 3회 실패: 모델이 JSON 외 설명을 섞거나 필드를 어긴 것입니다. 오류 메시지가 자동으로 되먹여지므로 모델 출력이 너무 불안정하면 `temperature=0`, 더 큰 모델 사용을 확인하세요.
- 값은 맞는데 `quote_not_found`가 많음: PDF 텍스트 추출이 줄바꿈·하이픈 분리를 만든 경우입니다. 검증은 공백·줄바꿈 차이는 허용하지만 하이픈 분리 단어는 못 잡을 수 있습니다.
- 그림이 하나도 안 잡힘: 현재 파서는 `Fig. N`/`Figure N`으로 시작하는 캡션 위쪽의 이미지·벡터 객체를 그림으로 잘라냅니다. 캡션이 그림 아래가 아닌 레이아웃이면 `parse.py`의 `_figures_on_page`를 조정합니다.
- 속도가 느림: 그림 반복 횟수(`ALD_FIG_SAMPLES`)를 줄이거나 `--no-figures`로 먼저 표·본문만 돌립니다.

## 10. 아직 확인되지 않은 것

- 자체 호스팅 DeepSeek의 정확한 버전과 JSON 모드 지원 여부, 자체 호스팅 비전 모델의 이름과 이미지 입력 방식
- 자체 호스팅 모델의 ALD 논문 추출 정확도 (6번의 gold 평가로 처음 알 수 있음)
- 비전 모델의 그래프 수치 판독 정확도 (일반 VLM은 DePlot보다 낫다는 보고가 있으나 자체 호스팅 모델은 별도 측정 필요)
- 실제 논문 PDF(2단 조판, 병합 셀)에서 기본 파서(pdfplumber)가 충분한지
