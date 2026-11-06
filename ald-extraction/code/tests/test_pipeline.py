import json
from pathlib import Path

import pytest

from ald_extract.config import Config, Endpoint
from ald_extract.evaluate import evaluate
from ald_extract.export import to_csv, to_cypher
from ald_extract.extract import extract_record
from ald_extract.figures import ensemble, extract_figures
from ald_extract.llm import FakeLLM, parse_json
from ald_extract.parse import parse_pdf
from ald_extract.schema import PaperRecord
from ald_extract.store import Store
from ald_extract.verify import quote_in_text, verify_record, value_in_quote
from ald_extract.cli import run_one
from make_pdf import make


@pytest.fixture(scope="module")
def pdf(tmp_path_factory):
    p = tmp_path_factory.mktemp("pdf") / "demo.pdf"
    make(p)
    return p


GOOD = {"paper_id": "x", "title": "ALD Al2O3", "processes": [{
    "label": "P1", "material": "Al2O3", "substrate": "Si(100)", "deposition_temp_c": 250, "cycles": 200,
    "precursors": [{"name": "TMA"}], "coreactants": [{"name": "H2O"}],
    "measurements": [
        {"name": "growth_per_cycle", "value": 1.1, "unit": "A/cycle",
         "source": {"page": 1, "quote": "The growth per cycle was 1.1 A/cycle at 250 C.", "method": "text"}},
        {"name": "thickness", "value": 22.0, "unit": "nm",
         "source": {"page": 1, "quote": "gave a thickness of 22.0 nm measured by XRR", "method": "text"}},
        {"name": "growth_per_cycle", "value": 9.9, "unit": "A/cycle",   # 환각: 원문에 없음
         "source": {"page": 1, "quote": "growth per cycle was 9.9 A/cycle", "method": "text"}}]}]}


def test_parse(pdf):
    p = parse_pdf(pdf)
    assert "growth per cycle" in p.pages[0]
    assert len(p.tables_md) == 1 and "0.95" in p.tables_md[0][1]
    assert "0.95" not in p.pages[0]                 # 표는 본문에서 분리
    assert len(p.figures) == 1 and p.figures[0].png[:4] == b"\x89PNG"
    assert "[[PAGE 1]]" in p.full_text()


def test_extract_retry_on_bad_json(pdf):
    p = parse_pdf(pdf, with_figures=False)
    outs = iter(["not json at all", json.dumps({"processes": "oops"}), "```json\n" + json.dumps(GOOD) + "\n```"])
    llm = FakeLLM(lambda m: next(outs))
    rec = extract_record(p, llm, "fake")
    assert rec.paper_id == "demo" and len(llm.calls) == 3
    assert len(rec.processes[0].measurements) == 3


def test_extract_gives_up(pdf):
    p = parse_pdf(pdf, with_figures=False)
    with pytest.raises(RuntimeError):
        extract_record(p, FakeLLM(lambda m: "garbage"), max_retries=1)


def test_verify_flags_hallucination(pdf):
    p = parse_pdf(pdf, with_figures=False)
    rec = PaperRecord.model_validate(GOOD); rec.paper_id = "demo"
    q = verify_record(rec, p)
    ms = rec.processes[0].measurements
    assert ms[0].confidence == 1.0 and ms[0].norm_unit == "nm/cycle" and ms[0].norm_value == pytest.approx(0.11)
    assert "v:quote_not_found" in ms[2].flags and ms[2].confidence < 0.7
    assert len(q) == 1 and q[0]["value"] == 9.9


def test_value_and_quote_helpers():
    assert value_in_quote(1.1, "GPC was 1.1 A/cycle")
    assert not value_in_quote(1.1, "GPC was 11 A/cycle")
    assert quote_in_text("growth  per\ncycle", "The Growth per cycle was")


def test_figure_ensemble_median_and_spread():
    s = lambda ys: {"x_label": "T", "x_unit": "C", "y_label": "GPC", "y_unit": "A/cycle",
                    "series": [{"name": "Al2O3", "points": [[150, ys[0]], [250, ys[1]]]}]}
    fd = ensemble([s([0.95, 1.10]), s([0.97, 1.12]), s([0.96, 1.30])], "Fig. 1", 1, "cap")
    pts = fd.series[0].points
    assert pts[0].y == pytest.approx(0.96) and pts[1].y == pytest.approx(1.12)
    assert pts[1].spread > 0.10 and "high_variance" in fd.flags


def test_figure_all_failed_flagged(pdf):
    p = parse_pdf(pdf)
    fds = extract_figures(p.figures, FakeLLM(lambda m: "cannot read"), n_samples=2)
    assert fds[0].flags == ["no_valid_samples"]


def test_end_to_end_store_export_eval(pdf, tmp_path):
    vlm_out = json.dumps({"x_label": "T", "x_unit": "C", "y_label": "GPC", "y_unit": "A/cycle",
                          "series": [{"name": "Al2O3", "points": [[150, 0.95], [250, 1.10]]}]})
    cfg = Config(llm=Endpoint("u", "m"), vlm=Endpoint("u", "v"), fig_samples=2, data_dir=tmp_path / "d")
    store = Store(cfg.data_dir)
    rec = run_one(pdf, cfg, store, llm=FakeLLM(lambda m: json.dumps(GOOD)), vlm=FakeLLM(lambda m: vlm_out))
    assert rec.figures[0].series[0].points[1].y == 1.10
    assert "v:figure_agrees" in rec.processes[0].measurements[0].flags      # 그림과 본문 일치
    loaded = store.load("demo")
    assert loaded.processes[0].measurements[0].value == 1.1
    assert len(store._read_queue()) == 1
    to_csv(store.all(), tmp_path / "o.csv")
    assert "growth_per_cycle" in (tmp_path / "o.csv").read_text(encoding="utf-8-sig")
    cy = to_cypher(store.all())
    assert any("MERGE (pa:Paper" in s for s in cy) and any("Precursor" in s for s in cy)
    # 평가: gold는 환각 행 제외
    gold = PaperRecord.model_validate(GOOD); gold.paper_id = "demo"
    gold.processes[0].measurements.pop()
    r = evaluate(loaded, gold)
    assert r["recall"] == 1.0 and r["precision"] == pytest.approx(2 / 3, abs=1e-3)
    assert r["recall_by_method"]["text"] == 1.0


def test_parse_json_variants():
    assert parse_json('앞말 {"a": 1} 뒷말') == {"a": 1}
    assert parse_json('```json\n[1,2]\n```') == [1, 2]
