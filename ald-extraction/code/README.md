# ald-extract — 자체 호스팅 LLM 기반 ALD 논문 데이터 추출 키트

PDF → (본문·표·그림 파싱) → 자체 호스팅 LLM 구조화 추출 → 자체 호스팅 비전 모델 그림 수치화(N회 앙상블)
→ 검증(인용·값·범위·단위·그림교차) → JSON 저장 → CSV / Neo4j(Cypher) → gold 평가.

## 설치
    python -m venv .venv && source .venv/bin/activate
    pip install -e ".[dev]"          # Neo4j 푸시는 .[neo4j]
    cp .env.example .env             # 엔드포인트/모델명/키 입력
    pytest -q                        # 목업 테스트 (외부 API 없이 통과해야 함)

## 실행
    ald-extract run paper.pdf              # 1편
    ald-extract batch ./pdfs               # 폴더 전체
    ald-extract review                     # 사람 검토 큐
    ald-extract export-csv out.csv
    ald-extract export-cypher out.cypher   # cypher-shell -f out.cypher
    ald-extract eval ./gold                # gold/*.json (PaperRecord 형식) 대비 정확도

## 환경에 맞게 고칠 곳
- 엔드포인트가 OpenAI 호환이 아니면 `ald_extract/llm.py`의 `OpenAICompatLLM.chat`만 교체.
- 모델이 `response_format`을 지원하지 않으면 `json_mode=False`로 (프롬프트가 JSON만 요구하고, 파서가 펜스/잡설을 처리).
- 스캔본·복잡한 표가 많으면 `parse.py`의 `parse_pdf`를 자체 호스팅 비전 모델 또는 로컬 파서(PaddleOCR-VL/MinerU)로 교체. 같은 `ParsedPaper`만 반환하면 됨.
- 그림용 비전모델이 이미지를 못 받는 형식이면 `llm.image_message` 수정.
- 단위 규칙·범위는 `verify.py`의 `UNIT_RULES` / `RANGES`에 ALD 측정 항목을 추가.

## 한계 (정직하게)
- 자체 호스팅 모델의 실제 정확도는 측정 전입니다. 먼저 gold 20~30편으로 `eval`을 돌려 보세요.
- 합성 PDF·가짜 LLM으로 로직만 검증했습니다. 실제 논문 레이아웃(2단 조판, 병합 셀)은 파서 보강이 필요할 수 있습니다.
- 그림 수치는 근사값이며 spread/플래그를 반드시 확인하세요.
