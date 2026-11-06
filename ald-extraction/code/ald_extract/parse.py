"""PDF → 페이지별 텍스트 + 표(마크다운) + 그림 후보(캡션 위치 이미지 크롭).
기본은 pdfplumber(순수 파이썬). 스캔본/복잡한 표는 PaddleOCR-VL/MinerU 같은
로컬 파서를 parse_pdf 대신 끼워 넣으면 된다 (같은 ParsedPaper 반환)."""
import io
import re
from dataclasses import dataclass, field
from pathlib import Path

import pdfplumber

CAPTION_RE = re.compile(r"^(Fig(?:ure)?\.?\s*\d+[a-z]?)[.:\s]", re.I)


@dataclass
class FigureCrop:
    page: int
    label: str
    caption: str
    png: bytes


@dataclass
class ParsedPaper:
    paper_id: str
    pages: list[str] = field(default_factory=list)       # 페이지별 본문
    tables_md: list[tuple[int, str]] = field(default_factory=list)
    figures: list[FigureCrop] = field(default_factory=list)

    def full_text(self) -> str:
        """LLM 입력용: 페이지 표지 + 본문 + 표(마크다운)."""
        out = []
        for i, t in enumerate(self.pages, 1):
            out.append(f"\n[[PAGE {i}]]\n{t}")
            for p, md in self.tables_md:
                if p == i:
                    out.append(f"\n[[TABLE on PAGE {i}]]\n{md}")
        return "\n".join(out)


def table_to_md(rows: list[list]) -> str:
    rows = [[(c or "").replace("\n", " ").strip() for c in r] for r in rows if r]
    if not rows:
        return ""
    w = max(len(r) for r in rows)
    rows = [r + [""] * (w - len(r)) for r in rows]
    lines = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * w]
    lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(lines)


def _crop_png(page, bbox, scale: float = 2.0) -> bytes:
    img = page.crop(bbox).to_image(resolution=int(72 * scale)).original
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def parse_pdf(path: str | Path, paper_id: str | None = None, with_figures: bool = True) -> ParsedPaper:
    path = Path(path)
    paper = ParsedPaper(paper_id=paper_id or path.stem)
    with pdfplumber.open(path) as pdf:
        for pno, page in enumerate(pdf.pages, 1):
            tables = page.find_tables()
            table_boxes = [t.bbox for t in tables]
            for t in tables:
                md = table_to_md(t.extract())
                if md:
                    paper.tables_md.append((pno, md))
            # 표 영역은 본문에서 제외해 중복 입력 방지
            body = page
            if table_boxes:
                def not_in_table(obj, boxes=table_boxes):
                    cx, cy = (obj["x0"] + obj["x1"]) / 2, (obj["top"] + obj["bottom"]) / 2
                    return not any(b[0] <= cx <= b[2] and b[1] <= cy <= b[3] for b in boxes)
                body = page.filter(not_in_table)
            paper.pages.append(body.extract_text() or "")
            if with_figures:
                paper.figures += _figures_on_page(page, pno)
    return paper


def _figures_on_page(page, pno: int) -> list[FigureCrop]:
    """캡션 줄(Fig. N)을 찾고, 그 위쪽의 이미지/벡터 객체 영역을 그림으로 크롭."""
    found = []
    lines = page.extract_text_lines()
    for ln in lines:
        m = CAPTION_RE.match(ln["text"].strip())
        if not m:
            continue
        cap_top = ln["top"]
        objs = [o for o in (page.images + page.rects + page.curves + page.lines)
                if o["bottom"] <= cap_top + 1 and o["top"] >= 0]
        if not objs:
            continue
        top = min(o["top"] for o in objs)
        # 위쪽 다른 캡션/본문과 섞이지 않게: 직전 텍스트 줄 아래에서 시작
        prev = [l for l in lines if l["bottom"] <= top + 1 and l is not ln]
        x0 = max(0, min(o["x0"] for o in objs) - 4)
        x1 = min(page.width, max(o["x1"] for o in objs) + 4)
        bbox = (x0, max(0, top - 4), x1, min(page.height, cap_top + ln["bottom"] - ln["top"]))
        if (bbox[2] - bbox[0]) < 50 or (bbox[3] - bbox[1]) < 40:
            continue
        found.append(FigureCrop(pno, m.group(1), ln["text"].strip(), _crop_png(page, bbox)))
    return found
