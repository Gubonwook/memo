"""테스트용 합성 ALD 논문 PDF (표 + 그림 + 캡션 포함)."""
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def make(path):
    c = canvas.Canvas(str(path), pagesize=A4)
    W, H = A4
    c.setFont("Helvetica", 11)
    y = H - 60
    for line in [
        "Atomic layer deposition of Al2O3 using TMA and H2O",
        "Films were deposited on Si(100) at 250 C using TMA and H2O.",
        "The growth per cycle was 1.1 A/cycle at 250 C.",
        "A total of 200 cycles gave a thickness of 22.0 nm measured by XRR.",
    ]:
        c.drawString(60, y, line); y -= 18
    # 표 (선 그려서 pdfplumber가 인식하게)
    y -= 20
    rows = [["Temp (C)", "GPC (A/cycle)"], ["150", "0.95"], ["250", "1.10"]]
    x0, cw, rh = 60, 120, 20
    for i, r in enumerate(rows):
        for j, cell in enumerate(r):
            c.rect(x0 + j * cw, y - i * rh - rh, cw, rh)
            c.drawString(x0 + j * cw + 6, y - i * rh - 14, cell)
    y -= 3 * rh + 30
    # 그림: 사각 프레임 + 선
    fx, fy, fw, fh = 80, y - 150, 300, 150
    c.rect(fx, fy, fw, fh)
    c.line(fx + 10, fy + 20, fx + 290, fy + 120)
    c.drawString(fx, fy - 16, "Figure 1. GPC versus temperature.")
    c.save()
