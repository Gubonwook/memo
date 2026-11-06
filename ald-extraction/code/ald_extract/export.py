"""파생 뷰: CSV(분석용), Cypher(Neo4j 그래프). JSON 저장소에서 언제든 재생성 가능."""
import csv
import re
from pathlib import Path

from .schema import PaperRecord


def to_csv(records: list[PaperRecord], path: Path) -> None:
    cols = ["paper_id", "process", "material", "substrate", "deposition_temp_c", "cycles", "precursors",
            "coreactants", "measurement", "value", "unit", "norm_value", "norm_unit", "condition",
            "page", "method", "ref", "confidence", "flags", "quote"]
    with Path(path).open("w", newline="", encoding="utf-8-sig") as f:   # utf-8-sig: 엑셀 한글 호환
        w = csv.DictWriter(f, cols)
        w.writeheader()
        for r in records:
            for p in r.processes:
                for m in p.measurements:
                    w.writerow({"paper_id": r.paper_id, "process": p.label, "material": p.material,
                                "substrate": p.substrate, "deposition_temp_c": p.deposition_temp_c,
                                "cycles": p.cycles, "precursors": ";".join(x.name for x in p.precursors),
                                "coreactants": ";".join(x.name for x in p.coreactants),
                                "measurement": m.name, "value": m.value, "unit": m.unit,
                                "norm_value": m.norm_value, "norm_unit": m.norm_unit, "condition": m.condition,
                                "page": m.source.page, "method": m.source.method, "ref": m.source.ref,
                                "confidence": m.confidence, "flags": ";".join(m.flags), "quote": m.source.quote})


def canon(name: str) -> str:
    """이름 정규화(간이): 공백/하이픈/대소문자 제거. 실제 운영에선 동의어 사전으로 확장."""
    return re.sub(r"[\s\-_()]+", "", name).lower()


def _q(s) -> str:
    return "'" + str(s).replace("\\", "\\\\").replace("'", "\\'") + "'"


def to_cypher(records: list[PaperRecord]) -> list[str]:
    st = []
    for r in records:
        st.append(f"MERGE (pa:Paper {{id:{_q(r.paper_id)}}}) SET pa.title={_q(r.title)}, pa.doi={_q(r.doi)}")
        for p in r.processes:
            pid = f"{r.paper_id}:{p.label}"
            st.append(f"MERGE (pr:Process {{id:{_q(pid)}}}) SET pr.temp_c={p.deposition_temp_c if p.deposition_temp_c is not None else 'null'}, "
                      f"pr.cycles={p.cycles if p.cycles is not None else 'null'}, pr.asd={str(p.is_area_selective).lower()} "
                      f"WITH pr MATCH (pa:Paper {{id:{_q(r.paper_id)}}}) MERGE (pa)-[:REPORTS]->(pr)")
            for x in p.precursors:
                st.append(f"MERGE (n:Precursor {{id:{_q(canon(x.name))}}}) SET n.name={_q(x.name)} "
                          f"WITH n MATCH (pr:Process {{id:{_q(pid)}}}) MERGE (pr)-[:USES]->(n)")
            for x in p.coreactants:
                st.append(f"MERGE (n:CoReactant {{id:{_q(canon(x.name))}}}) SET n.name={_q(x.name)}, n.plasma={str(x.plasma).lower()} "
                          f"WITH n MATCH (pr:Process {{id:{_q(pid)}}}) MERGE (pr)-[:USES]->(n)")
            if p.substrate:
                st.append(f"MERGE (n:Substrate {{id:{_q(canon(p.substrate))}}}) SET n.name={_q(p.substrate)} "
                          f"WITH n MATCH (pr:Process {{id:{_q(pid)}}}) MERGE (pr)-[:DEPOSITED_ON]->(n)")
            if p.material:
                st.append(f"MERGE (n:Material {{id:{_q(canon(p.material))}}}) SET n.name={_q(p.material)} "
                          f"WITH n MATCH (pr:Process {{id:{_q(pid)}}}) MERGE (pr)-[:DEPOSITS]->(n)")
            for i, m in enumerate(p.measurements):
                mid = f"{pid}:{m.name}:{i}"
                st.append(f"MERGE (m:Measurement {{id:{_q(mid)}}}) SET m.name={_q(m.name)}, "
                          f"m.value={m.value if m.value is not None else 'null'}, m.unit={_q(m.unit)}, "
                          f"m.norm_value={m.norm_value if m.norm_value is not None else 'null'}, m.norm_unit={_q(m.norm_unit)}, "
                          f"m.page={m.source.page if m.source.page is not None else 'null'}, m.method={_q(m.source.method)}, "
                          f"m.quote={_q(m.source.quote)}, m.confidence={m.confidence} "
                          f"WITH m MATCH (pr:Process {{id:{_q(pid)}}}) MERGE (pr)-[:HAS]->(m)")
    return st


def push_neo4j(statements: list[str], uri: str, user: str, password: str) -> None:
    from neo4j import GraphDatabase          # pip install neo4j
    with GraphDatabase.driver(uri, auth=(user, password)) as drv, drv.session() as s:
        for stmt in statements:
            s.run(stmt)
