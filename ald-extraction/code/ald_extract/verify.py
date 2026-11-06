"""검증: (1) 근거 인용이 원문에 실제 존재하는가 (2) 값이 인용 안에 있는가
(3) 물리적 범위 (4) 단위 정규화 (5) 그림↔본문/표 교차 확인.
통과 못 한 항목은 confidence를 깎고 flags에 사유를 남겨 사람 검토 큐로 보낸다."""
import re
from difflib import SequenceMatcher

from .parse import ParsedPaper
from .schema import FigureData, Measurement, PaperRecord

# (이름 패턴) -> {단위: (정규 단위, 곱셈 계수)}
UNIT_RULES = {
    "growth_per_cycle": {"å/cycle": ("nm/cycle", 0.1), "a/cycle": ("nm/cycle", 0.1),
                         "å": ("nm/cycle", 0.1), "nm/cycle": ("nm/cycle", 1.0), "pm/cycle": ("nm/cycle", 0.001)},
    "thickness": {"å": ("nm", 0.1), "nm": ("nm", 1.0), "µm": ("nm", 1000.0), "um": ("nm", 1000.0)},
    "temperature": {"°c": ("C", 1.0), "c": ("C", 1.0), "k": ("C", None)},
}
# 정규 단위 기준 허용 범위 (벗어나면 경고, 삭제하지 않음)
RANGES = {"growth_per_cycle": (0.005, 1.0), "temperature": (-50.0, 1200.0), "thickness": (0.1, 5000.0)}


def _ws(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("−", "-").replace("–", "-")).strip().lower()


def quote_in_text(quote: str, text: str, fuzzy: float = 0.9) -> bool:
    q, t = _ws(quote), _ws(text)
    if not q:
        return False
    if q in t:
        return True
    # 표 행/줄바꿈 차이를 허용: 가장 비슷한 윈도우 찾기
    if len(q) > 400:
        q = q[:400]
    step = max(len(q) // 2, 20)
    best = 0.0
    for i in range(0, max(len(t) - len(q), 0) + 1, step):
        best = max(best, SequenceMatcher(None, q, t[i:i + len(q)]).ratio())
        if best >= fuzzy:
            return True
    return False


def value_in_quote(value: float, quote: str) -> bool:
    nums = re.findall(r"-?\d+(?:[.,]\d+)?(?:[eE][-+]?\d+)?", quote.replace("−", "-"))
    for n in nums:
        try:
            if abs(float(n.replace(",", ".")) - value) <= 1e-9 + 1e-6 * abs(value):
                return True
        except ValueError:
            pass
    return False


def normalize(m: Measurement) -> None:
    rules = UNIT_RULES.get(m.name)
    if not rules or m.value is None:
        return
    u = m.unit.strip().lower().replace(" ", "")
    if u in rules:
        canon, k = rules[u]
        m.norm_unit = canon
        m.norm_value = (m.value - 273.15) if k is None else m.value * k


def verify_measurement(m: Measurement, text: str) -> None:
    m.flags = [f for f in m.flags if not f.startswith("v:")]
    pen = 0.0
    if not quote_in_text(m.source.quote, text):
        m.flags.append("v:quote_not_found"); pen += 0.5
    elif m.value is not None and not value_in_quote(m.value, m.source.quote):
        m.flags.append("v:value_not_in_quote"); pen += 0.4
    normalize(m)
    if m.norm_value is not None and m.name in RANGES:
        lo, hi = RANGES[m.name]
        if not lo <= m.norm_value <= hi:
            m.flags.append("v:out_of_range"); pen += 0.3
    m.confidence = max(0.0, round(m.confidence - pen, 3))


def cross_check_figures(rec: PaperRecord, tol: float = 0.07) -> None:
    """본문/표의 값이 같은 단위의 그림 데이터와 일치하면 신뢰도 가산."""
    for p in rec.processes:
        for m in p.measurements:
            if m.value is None or m.source.method == "figure":
                continue
            for f in rec.figures:
                if _ws(f.y_unit) != _ws(m.unit):
                    continue
                for s in f.series:
                    if any(abs(pt.y - m.value) <= tol * abs(m.value) for pt in s.points):
                        if "v:figure_agrees" not in m.flags:
                            m.flags.append("v:figure_agrees")
                            m.confidence = min(1.0, round(m.confidence + 0.1, 3))


def verify_record(rec: PaperRecord, paper: ParsedPaper) -> list[dict]:
    text = paper.full_text()
    for p in rec.processes:                      # 1) 개별 검증 (flags 초기화 포함)
        for m in p.measurements:
            verify_measurement(m, text)
    cross_check_figures(rec)                     # 2) 그림 교차 확인은 검증 이후에
    queue = []
    for p in rec.processes:
        for m in p.measurements:
            bad = [f for f in m.flags if f.startswith("v:") and f != "v:figure_agrees"]
            if bad or m.confidence < 0.7:
                queue.append({"paper_id": rec.paper_id, "process": p.label, "measurement": m.name,
                              "value": m.value, "unit": m.unit, "page": m.source.page,
                              "quote": m.source.quote, "flags": bad, "confidence": m.confidence})
    for f in rec.figures:
        if f.flags:
            queue.append({"paper_id": rec.paper_id, "figure": f.label, "page": f.page,
                          "flags": f.flags, "confidence": 0.5})
    return queue
