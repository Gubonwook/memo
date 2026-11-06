"""본문+표 → PaperRecord. 자체 호스팅 LLM(텍스트)에 전체 논문을 한 번에 넣고
스키마에 맞는 JSON을 받는다. 검증 실패 시 오류 메시지를 되먹여 재시도."""
import json

from pydantic import ValidationError

from .llm import LLM, parse_json
from .parse import ParsedPaper
from .schema import PaperRecord

SYSTEM = """당신은 ALD(원자층증착) 논문에서 실험 데이터를 추출하는 정밀한 추출기입니다.
규칙:
1. 논문에 명시된 값만 추출합니다. 추측·계산·보간 금지. 없으면 null 또는 빈 배열.
2. 모든 measurement에는 source.page(본문의 [[PAGE n]] 표지 기준)와 source.quote(원문에서 그대로 복사한 근거 문장 또는 표 행)를 채웁니다. quote는 절대 바꿔 쓰지 마세요.
3. 값의 단위는 논문에 쓰인 그대로 unit에 적습니다 (변환 금지).
4. 표에서 온 값은 source.method="table", ref에 "Table N". 본문 문장은 "text".
5. 그림(Fig.)에서만 읽을 수 있는 값은 여기서 추출하지 않습니다 (별도 단계).
6. 공정이 여러 개(온도·전구체 조건 다름)면 Process를 나누고 label로 구분합니다.
7. 출력은 아래 JSON 스키마를 따르는 JSON 객체 하나뿐입니다. 설명 문장 금지."""


def build_messages(paper: ParsedPaper) -> list[dict]:
    schema = json.dumps(PaperRecord.model_json_schema(), ensure_ascii=False)
    user = (f"JSON 스키마:\n{schema}\n\npaper_id는 \"{paper.paper_id}\" 로 설정하세요.\n\n"
            f"=== 논문 본문 ===\n{paper.full_text()}")
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


def extract_record(paper: ParsedPaper, llm: LLM, extractor_name: str = "", max_retries: int = 2) -> PaperRecord:
    messages = build_messages(paper)
    last_err = ""
    for attempt in range(max_retries + 1):
        raw = llm.chat(messages, temperature=0.0, json_mode=True)
        try:
            rec = PaperRecord.model_validate(parse_json(raw))
            rec.paper_id = paper.paper_id
            rec.extractor = extractor_name
            return rec
        except (ValidationError, ValueError) as e:
            last_err = str(e)[:1500]
            messages = messages + [
                {"role": "assistant", "content": raw},
                {"role": "user", "content": f"출력이 스키마 검증에 실패했습니다:\n{last_err}\n고쳐서 JSON만 다시 출력하세요."}]
    raise RuntimeError(f"스키마 검증 {max_retries + 1}회 실패: {last_err}")
