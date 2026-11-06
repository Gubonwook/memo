"""그림 → 수치. 자체 호스팅 비전 모델을 같은 그림에 N회 반복 호출하고,
점별 중앙값으로 병합, 반복 간 편차를 불확실성(spread)으로 저장한다.
비전 모델 출력은 '근거가 약한 파생 증거'이므로 verify 단계에서 반드시 교차 확인한다."""
import statistics
from collections import defaultdict

from .llm import LLM, image_message, parse_json
from .parse import FigureCrop
from .schema import FigureData, FigurePoint, FigureSeries

PROMPT = """이 그림은 ALD 논문의 Figure입니다. 캡션: "{caption}"
그림의 데이터 점을 읽어 아래 JSON만 출력하세요 (설명 금지):
{{"x_label": str, "x_unit": str, "y_label": str, "y_unit": str,
  "series": [{{"name": str, "points": [[x, y], ...]}}]}}
규칙: 축 눈금을 기준으로 읽고, 로그축이면 실제 값으로 변환합니다.
데이터 점이 보이지 않거나 읽을 수 없으면 "series": [] 로 두세요. 추측으로 점을 만들지 마세요."""


def _norm(s: str) -> str:
    return "".join(ch for ch in s.lower() if ch.isalnum())


def extract_once(fig: FigureCrop, vlm: LLM, temperature: float) -> dict | None:
    try:
        raw = vlm.chat(image_message(PROMPT.format(caption=fig.caption), fig.png),
                       temperature=temperature, max_tokens=4096)
        d = parse_json(raw)
        return d if isinstance(d, dict) else None
    except Exception:
        return None


def ensemble(samples: list[dict], label: str, page: int, caption: str,
             rel_tol: float = 0.05, spread_flag: float = 0.10) -> FigureData:
    fd = FigureData(label=label, page=page, caption=caption, n_samples=len(samples))
    if not samples:
        fd.flags.append("no_valid_samples")
        return fd
    ref = samples[0]
    fd.x_label, fd.x_unit = ref.get("x_label", ""), ref.get("x_unit", "")
    fd.y_label, fd.y_unit = ref.get("y_label", ""), ref.get("y_unit", "")
    # 시리즈 이름으로 정렬
    by_series: dict[str, list[list[tuple[float, float]]]] = defaultdict(list)
    names: dict[str, str] = {}
    for s in samples:
        for ser in s.get("series", []):
            key = _norm(str(ser.get("name", "")))
            names.setdefault(key, str(ser.get("name", "")))
            pts = []
            for p in ser.get("points", []):
                try:
                    pts.append((float(p[0]), float(p[1])))
                except (TypeError, ValueError, IndexError):
                    continue
            by_series[key].append(pts)
    for key, runs in by_series.items():
        base = max(runs, key=len)                # 가장 점이 많은 실행을 기준 x로
        xs = [p[0] for p in base]
        span = (max(xs) - min(xs)) if len(xs) > 1 else (abs(xs[0]) or 1.0)
        tol = max(span * rel_tol, 1e-12)
        merged = []
        for bx, by in base:
            ys = [by]
            for run in runs:
                if run is base:
                    continue
                near = min(run, key=lambda p: abs(p[0] - bx), default=None)
                if near and abs(near[0] - bx) <= tol:
                    ys.append(near[1])
            med = statistics.median(ys)
            spread = (max(ys) - min(ys)) / abs(med) if med else (max(ys) - min(ys))
            merged.append(FigurePoint(x=bx, y=med, spread=round(spread, 4), n=len(ys)))
        fd.series.append(FigureSeries(name=names[key], points=merged))
        if len(runs) < len(samples):
            fd.flags.append(f"series_missing_in_some_runs:{names[key]}")
    if any(p.spread > spread_flag for s in fd.series for p in s.points):
        fd.flags.append("high_variance")
    return fd


def extract_figures(figs: list[FigureCrop], vlm: LLM, n_samples: int = 3) -> list[FigureData]:
    out = []
    for f in figs:
        samples = []
        for i in range(n_samples):
            d = extract_once(f, vlm, temperature=0.0 if i == 0 else 0.3)
            if d and d.get("series"):
                samples.append(d)
        fd = ensemble(samples, f.label, f.page, f.caption)
        fd.n_samples = n_samples
        out.append(fd)
    return out
