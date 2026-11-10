#!/usr/bin/env python3
"""ALD 공정 온도 창 DB: MD <-> Excel 변환.

원본은 data/ald_window_db.md 입니다. 엑셀에서 고치고 싶으면 xlsx를 만들어 편집한 뒤
다시 MD로 돌려 커밋하세요. 계산기는 MD를 자동으로 읽고, 엑셀·CSV는 '파일 불러오기'로 읽습니다.

  python tools/sync_db.py md2xlsx   # data/ald_window_db.md  -> data/ald_window_db.xlsx
  python tools/sync_db.py xlsx2md   # data/ald_window_db.xlsx -> data/ald_window_db.md
  python tools/sync_db.py check     # 두 파일의 행 수와 필수값 확인

필요 패키지: openpyxl
"""
import re
import sys
from datetime import date
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parent.parent
MD = ROOT / "data" / "ald_window_db.md"
XLSX = ROOT / "data" / "ald_window_db.xlsx"

PROC_COLS = ["id", "박막", "분류", "전구체", "전구체 화학식", "반응물", "방식", "창 하한 (°C)", "창 상한 (°C)",
             "GPC (Å/cy)", "분해 시작 (°C)", "소스 온도 (°C)", "상태", "신뢰도", "출처", "메모", "숨김"]
SUB_COLS = ["id", "기판", "분류", "표면", "허용 온도 (°C)", "주의 온도 (°C)", "주의 이유", "산화제에 산화",
            "H₂O에 산화", "할라이드 부식", "플라즈마 손상", "TMA 셀프클리닝", "산화 영향", "신뢰도", "메모", "숨김"]
PROC_REQ = ["박막", "전구체", "반응물", "창 하한 (°C)", "창 상한 (°C)"]
SUB_REQ = ["기판", "허용 온도 (°C)"]

# 엑셀 드롭다운 (열 이름: 허용값)
PROC_LISTS = {"분류": "산화물,질화물,금속,황화물,기타", "방식": "열,플라즈마", "상태": "액체,고체,기체",
              "신뢰도": "높음,중간,낮음", "숨김": "Y"}
SUB_LISTS = {"분류": "반도체,절연체,금속,고분자,2D,기타", "표면": "OH,H,semi,metal,polymer,inert",
             "산화제에 산화": "Y", "H₂O에 산화": "Y", "할라이드 부식": "Y", "플라즈마 손상": "Y",
             "TMA 셀프클리닝": "Y", "신뢰도": "높음,중간,낮음", "숨김": "Y"}

GUIDE = """이 파일은 ALD 공정 온도 창 계산기의 원본 DB입니다. 표 두 개(공정, 기판)를 고치고 저장하면, 계산기가 다음에 열릴 때 읽거나 ‘파일 불러오기’로 넣을 수 있습니다.

## 작성 규칙

- 한 행이 공정 하나(또는 기판 하나)입니다. 표의 머리행 이름은 바꾸지 마세요.
- 새 행은 id를 비워 두면 됩니다. 박막·전구체·반응물·방식이 같은 기존 행이 있으면 그 행을 덮어씁니다.
- 방식: 열 / 플라즈마 · 신뢰도: 높음 / 중간 / 낮음 · 상태: 액체 / 고체 / 기체
- 기판 표면: OH / H / semi / metal / polymer / inert (OH 종단, H 종단, 자연산화막 반도체, 도전체, 고분자, 반응 사이트 부족)
- 예/아니오 칸(산화, 할라이드 등)은 Y 또는 빈칸, 숨김에 Y를 넣으면 그 행(기본 공정 포함)을 계산기에서 숨깁니다.
- 칸 안에 | 문자를 쓰려면 \\| 로 적으세요. 모르는 값은 비워 두세요(추정값 금지)."""


def split_row(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", s)]


def read_md(path):
    """MD 안의 표를 머리행으로 구분해 (공정 행들, 기판 행들)을 돌려준다."""
    tables, block = [], []
    for line in path.read_text(encoding="utf-8").splitlines() + [""]:
        if line.lstrip().startswith("|"):
            block.append(line)
        elif block:
            tables.append(block)
            block = []
    procs, subs = [], []
    for t in tables:
        head = split_row(t[0])
        body = [l for l in t[1:] if not re.match(r"^\s*\|?\s*:?-{2,}", l)]
        rows = [dict(zip(head, split_row(l) + [""] * len(head))) for l in body]
        if "박막" in head and "전구체" in head:
            procs += rows
        elif "기판" in head:
            subs += rows
    return procs, subs


def md_table(cols, rows):
    esc = lambda v: str(v if v is not None else "").replace("|", "\\|").replace("\n", " ")
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    out += ["| " + " | ".join(esc(r.get(c, "")) for c in cols) + " |" for r in rows]
    return "\n".join(out)


def write_md(path, procs, subs):
    text = (f"# ALD 공정 온도 창 DB\n\n내보낸 날짜: {date.today().isoformat()}\n\n{GUIDE}\n\n"
            f"## 공정\n\n{md_table(PROC_COLS, procs)}\n\n## 기판\n\n{md_table(SUB_COLS, subs)}\n")
    path.write_text(text, encoding="utf-8")


def read_xlsx(path):
    wb = load_workbook(path, data_only=True)
    out = {}
    for name in ("공정", "기판"):
        if name not in wb.sheetnames:
            out[name] = []
            continue
        ws = wb[name]
        rows = list(ws.iter_rows(values_only=True))
        head = [str(h).strip() if h is not None else "" for h in rows[0]] if rows else []
        data = []
        for r in rows[1:]:
            if not any(v not in (None, "") for v in r):
                continue
            d = {}
            for h, v in zip(head, r):
                if isinstance(v, float) and v.is_integer():
                    v = int(v)
                d[h] = "" if v is None else str(v).strip()
            data.append(d)
        out[name] = data
    return out["공정"], out["기판"]


def write_xlsx(path, procs, subs):
    wb = Workbook()
    base = Font(name="Arial", size=10)
    head_font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
    head_fill = PatternFill("solid", fgColor="0D6C8A")
    req_fill = PatternFill("solid", fgColor="FFF2CC")

    def sheet(ws, cols, rows, req, lists):
        ws.append(cols)
        for r in rows:
            vals = []
            for c in cols:
                v = r.get(c, "")
                if re.fullmatch(r"-?\d+(\.\d+)?", str(v)) and "GPC" not in c:
                    v = float(v) if "." in str(v) else int(v)
                vals.append(v)
            ws.append(vals)
        for cell in ws[1]:
            cell.font, cell.fill = head_font, head_fill
            cell.alignment = Alignment(vertical="center", wrap_text=True)
            if cell.value in req:
                cell.value = f"{cell.value}"
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.font = base
        for i, c in enumerate(cols, start=1):
            letter = ws.cell(row=1, column=i).column_letter
            ws.column_dimensions[letter].width = 44 if c in ("메모", "출처", "산화 영향") else max(9, min(22, len(c) * 2 + 2))
            if c in req:
                for r in range(2, 1001):
                    ws.cell(row=r, column=i).fill = req_fill if ws.cell(row=r, column=i).value in (None, "") else PatternFill()
            if c in lists:
                dv = DataValidation(type="list", formula1=f'"{lists[c]}"', allow_blank=True)
                dv.error, dv.errorTitle = f"허용값: {lists[c]}", "입력값 확인"
                ws.add_data_validation(dv)
                dv.add(f"{letter}2:{letter}1000")
        ws.freeze_panes = "C2"
        ws.auto_filter.ref = ws.dimensions

    ws = wb.active
    ws.title = "공정"
    sheet(ws, PROC_COLS, procs, PROC_REQ, PROC_LISTS)
    sheet(wb.create_sheet("기판"), SUB_COLS, subs, SUB_REQ, SUB_LISTS)

    g = wb.create_sheet("사용법")
    lines = [
        ("ALD 공정 온도 창 DB · 엑셀 편집용", True),
        ("원본은 data/ald_window_db.md 입니다. 여기서 고친 뒤 'python tools/sync_db.py xlsx2md'로 MD에 반영해 커밋하세요.", False),
        ("이 엑셀을 계산기의 '데이터 관리 > 파일 불러오기'에 바로 넣어도 됩니다.", False),
        ("", False),
        ("편집 규칙", True),
        ("· 공정·기판 시트의 머리행 이름은 바꾸지 마세요. 시트 이름(공정, 기판)도 그대로 두세요.", False),
        ("· 노란 칸은 필수값입니다: 공정 = 박막·전구체·반응물·창 하한·창 상한 / 기판 = 기판·허용 온도.", False),
        ("· 새 행은 id를 비워 두세요. 박막·전구체·반응물·방식이 같은 행이 있으면 그 행을 덮어씁니다.", False),
        ("· 방식·신뢰도·상태·표면·Y 칸은 드롭다운에서 고릅니다. 숨김 = Y이면 계산기에서 그 행을 숨깁니다.", False),
        ("· 온도는 °C 숫자만, GPC는 '0.9–1.1'처럼 범위 텍스트도 됩니다. 모르는 값은 비워 두세요.", False),
        ("· 출처 칸에 DOI나 실험 번호를 적어 두면 계산기 판정 화면에 같이 표시됩니다.", False),
        ("", False),
        ("기판 '표면' 값", True),
        ("OH = OH 종단(산화물) · H = H 종단(HF-last) · semi = 자연산화막 반도체(Ge, III-V)", False),
        ("metal = 금속·질화물 도전체 · polymer = 고분자 · inert = 반응 사이트 부족(2D 기저면)", False),
        ("", False),
        ("예시 행: 공정 시트의 b01 (Al₂O₃ · TMA + H₂O · 100–300 °C)", False),
    ]
    for text, bold in lines:
        g.append([text])
        g.cell(row=g.max_row, column=1).font = Font(name="Arial", size=11 if bold else 10, bold=bold)
    g.column_dimensions["A"].width = 110
    wb.save(path)


def check(procs, subs, label):
    bad_p = [r.get("id") or r.get("박막") for r in procs
             if r.get("숨김", "").upper() != "Y" and any(not str(r.get(c, "")).strip() for c in PROC_REQ)]
    bad_s = [r.get("id") or r.get("기판") for r in subs
             if r.get("숨김", "").upper() != "Y" and any(not str(r.get(c, "")).strip() for c in SUB_REQ)]
    print(f"{label}: 공정 {len(procs)}행, 기판 {len(subs)}행", end="")
    print(f" · 필수값 누락 공정 {bad_p} 기판 {bad_s}" if bad_p or bad_s else " · 필수값 이상 없음")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "md2xlsx":
        p, s = read_md(MD)
        write_xlsx(XLSX, p, s)
        check(p, s, f"{MD.name} → {XLSX.name}")
    elif cmd == "xlsx2md":
        p, s = read_xlsx(XLSX)
        write_md(MD, p, s)
        check(p, s, f"{XLSX.name} → {MD.name}")
    elif cmd == "check":
        if MD.exists():
            check(*read_md(MD), MD.name)
        if XLSX.exists():
            check(*read_xlsx(XLSX), XLSX.name)
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
