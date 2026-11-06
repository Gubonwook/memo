"""사용법:
  ald-extract run  paper.pdf [--no-figures]
  ald-extract batch ./pdfs
  ald-extract export-csv out.csv
  ald-extract export-cypher out.cypher
  ald-extract review            # 사람 검토 큐 출력
  ald-extract eval ./gold_dir   # gold/*.json 과 data/records 비교
"""
import argparse
import json
import sys
from pathlib import Path

from .config import Config
from .evaluate import evaluate_many
from .export import to_csv, to_cypher
from .extract import extract_record
from .figures import extract_figures
from .llm import OpenAICompatLLM
from .parse import parse_pdf
from .schema import PaperRecord
from .store import Store
from .verify import verify_record


def run_one(pdf: Path, cfg: Config, store: Store, llm=None, vlm=None, with_figures: bool = True) -> PaperRecord:
    llm = llm or OpenAICompatLLM(cfg.llm)
    paper = parse_pdf(pdf, with_figures=with_figures and (vlm is not None or cfg.vlm.ready))
    rec = extract_record(paper, llm, extractor_name=cfg.llm.model)
    if paper.figures and (vlm is not None or cfg.vlm.ready):
        rec.figures = extract_figures(paper.figures, vlm or OpenAICompatLLM(cfg.vlm), cfg.fig_samples)
    queue = verify_record(rec, paper)
    store.save(rec, queue)
    print(f"[{rec.paper_id}] 공정 {len(rec.processes)}개, 그림 {len(rec.figures)}개, 검토 필요 {len(queue)}건")
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="ald-extract")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run"); r.add_argument("pdf"); r.add_argument("--no-figures", action="store_true")
    b = sub.add_parser("batch"); b.add_argument("dir"); b.add_argument("--no-figures", action="store_true")
    sub.add_parser("review")
    c = sub.add_parser("export-csv"); c.add_argument("out")
    y = sub.add_parser("export-cypher"); y.add_argument("out")
    e = sub.add_parser("eval"); e.add_argument("gold_dir")
    a = ap.parse_args(argv)
    cfg = Config.from_env()
    store = Store(cfg.data_dir)

    if a.cmd in ("run", "batch"):
        if not cfg.llm.ready:
            print("ALD_LLM_BASE_URL / ALD_LLM_MODEL 이 설정되지 않았습니다 (.env 확인)", file=sys.stderr)
            return 2
        pdfs = [Path(a.pdf)] if a.cmd == "run" else sorted(Path(a.dir).glob("*.pdf"))
        for p in pdfs:
            try:
                run_one(p, cfg, store, with_figures=not a.no_figures)
            except Exception as ex:                       # 한 편 실패가 배치를 멈추지 않게
                print(f"[{p.name}] 실패: {ex}", file=sys.stderr)
    elif a.cmd == "review":
        for item in store._read_queue():
            print(json.dumps(item, ensure_ascii=False))
    elif a.cmd == "export-csv":
        to_csv(store.all(), Path(a.out)); print("저장:", a.out)
    elif a.cmd == "export-cypher":
        Path(a.out).write_text(";\n".join(to_cypher(store.all())) + ";\n", encoding="utf-8"); print("저장:", a.out)
    elif a.cmd == "eval":
        golds = [PaperRecord.model_validate_json(p.read_text(encoding="utf-8")) for p in sorted(Path(a.gold_dir).glob("*.json"))]
        print(json.dumps(evaluate_many(store.all(), golds), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
