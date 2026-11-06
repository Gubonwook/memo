"""정답(gold) 레코드와 추출 결과 비교. gold는 PaperRecord와 같은 JSON 형식.
매칭 기준: 같은 paper, measurement 이름 + (정규화) 값이 rel_tol 이내 + 단위 일치."""
from .schema import PaperRecord


def _items(rec: PaperRecord):
    for p in rec.processes:
        for m in p.measurements:
            if m.value is not None:
                yield m


def _match(a, b, rel_tol: float) -> bool:
    if a.name != b.name:
        return False
    av, bv = (a.norm_value, b.norm_value) if a.norm_value is not None and b.norm_value is not None else (a.value, b.value)
    if av is None or bv is None:
        return False
    if abs(av - bv) > rel_tol * max(abs(bv), 1e-12):
        return False
    if av is a.value and a.unit.strip().lower() != b.unit.strip().lower():
        return False
    return True


def evaluate(pred: PaperRecord, gold: PaperRecord, rel_tol: float = 0.01) -> dict:
    g, p = list(_items(gold)), list(_items(pred))
    used, tp = set(), 0
    by_method: dict[str, list[int]] = {}
    for gm in g:
        hit = next((i for i, pm in enumerate(p) if i not in used and _match(pm, gm, rel_tol)), None)
        by_method.setdefault(gm.source.method, [0, 0])[1] += 1
        if hit is not None:
            used.add(hit); tp += 1
            by_method[gm.source.method][0] += 1
    prec = tp / len(p) if p else 0.0
    rec = tp / len(g) if g else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return {"paper_id": gold.paper_id, "gold": len(g), "pred": len(p), "tp": tp,
            "precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4),
            "recall_by_method": {k: round(v[0] / v[1], 4) for k, v in by_method.items()},
            "missed": [f"{m.name}={m.value} {m.unit}" for i, m in enumerate(g)
                       if not any(_match(pm, m, rel_tol) for pm in p)]}


def evaluate_many(preds: list[PaperRecord], golds: list[PaperRecord], rel_tol: float = 0.01) -> dict:
    pm = {r.paper_id: r for r in preds}
    rows = [evaluate(pm.get(g.paper_id, PaperRecord(paper_id=g.paper_id)), g, rel_tol) for g in golds]
    tp = sum(r["tp"] for r in rows)
    ng, npred = sum(r["gold"] for r in rows), sum(r["pred"] for r in rows)
    prec, rec = (tp / npred if npred else 0), (tp / ng if ng else 0)
    return {"papers": rows, "micro_precision": round(prec, 4), "micro_recall": round(rec, 4),
            "micro_f1": round(2 * prec * rec / (prec + rec), 4) if prec + rec else 0.0}
