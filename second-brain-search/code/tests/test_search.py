import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sbsearch as sb

NOTES = {
 "adsorption.md": "---\nname: adsorption\ndescription: 전구체 흡착 에너지 계산 메모\naliases: [precursor adsorption, E_ads]\n---\n# 흡착\n전구체가 표면에 흡착하는 에너지를 MLIP로 계산했다. 기체 분자 에너지 오차가 크다.\n## 결과\nSevenNet으로 흡착에너지를 구했고 DFT와 비교했다.",
 "meeting.md": "---\nname: meeting-1105\ndescription: 11월 5일 주간 회의록\n---\n# 회의\n다음 주까지 논문 초안을 수정하기로 했다. 투고 저널은 아직 미정이다.",
 "home.md": "---\nname: home\ndescription: 집 구매 계획\n---\n# 대출\n생애최초 주택 구매 대출 한도를 알아보는 중이다.",
 "neb.md": "---\nname: neb\ndescription: NEB 반응 장벽 계산\naliases: [nudged elastic band, 전이상태]\n---\n# 설정\n반쪽반응의 전이상태를 찾기 위해 CI-NEB를 사용한다.",
}
QA = [
 {"q": "흡착에너지 계산", "gold": ["adsorption.md"]},        # 띄어쓰기 다름
 {"q": "전구체가 흡착되는 에너지", "gold": ["adsorption.md"]},  # 조사 변형
 {"q": "precursor adsorption", "gold": ["adsorption.md"]},      # 별칭(영문)
 {"q": "논문을 수정했나", "gold": ["meeting.md"]},               # 어미 변형
 {"q": "주택 대출 알아보기", "gold": ["home.md"]},
 {"q": "전이상태 탐색", "gold": ["neb.md"]},
]

def build(tmp_path, tok):
    root = tmp_path / "notes"; root.mkdir(exist_ok=True)
    for n, t in NOTES.items():
        (root / n).write_text(t, encoding="utf-8")
    idx = sb.Index(str(tmp_path / f"{tok.__name__}.sqlite"), tokenizer=tok)
    idx.index_dir(str(root))
    return idx

def ws(text): return text.lower().split()

def test_kiwi_tokenize_splits_particles():
    t = sb.tokenize("전구체가 흡착하는 에너지를")
    assert "전구체" in t and "에너지" in t and "가" not in t

def test_frontmatter_and_chunks():
    ch = sb.chunk_note("a.md", NOTES["adsorption.md"])
    assert len(ch) == 2 and "precursor adsorption" in ch[0].context

def test_kiwi_beats_whitespace(tmp_path):
    k = sb.evaluate(build(tmp_path, sb.tokenize), QA)
    w = sb.evaluate(build(tmp_path, ws), QA)
    print("kiwi", k, "whitespace", w)
    assert k["recall@5"] == 1.0
    assert k["recall@5"] > w["recall@5"]

def test_rrf_order():
    assert sb.rrf([[1, 2, 3], [3, 1, 9]])[:2] == [1, 3]

def test_expand_and_rerank_with_fake_llm(tmp_path):
    idx = build(tmp_path, sb.tokenize)
    calls = []
    def chat(prompt):
        calls.append(prompt)
        return "NEB\n전이상태\n반응 장벽" if "질의 확장" in prompt else "0"
    r = sb.search(idx, "에너지 장벽 어디 적었지", expand=sb.make_expand(chat), rerank=sb.make_rerank(chat))
    assert r and any("질의 확장" in c for c in calls) and any("관련 깊은" in c for c in calls)
    assert "neb.md" in [x["path"] for x in r]

def test_vector_path_with_fake_embed(tmp_path):
    root = tmp_path / "n"; root.mkdir()
    for n, t in NOTES.items(): (root / n).write_text(t, encoding="utf-8")
    vocab = ["흡착", "회의", "대출", "neb"]
    def embed(texts): return [[float(v in t.lower()) for v in vocab] for t in texts]
    idx = sb.Index(str(tmp_path / "v.sqlite")); idx.index_dir(str(root), embed)
    assert idx.vector(embed(["흡착"])[0])[0] is not None
    assert sb.search(idx, "흡착", embed=embed)[0]["path"] == "adsorption.md"

def test_llm_env_off(monkeypatch):
    monkeypatch.delenv("SB_LLM_BASE_URL", raising=False)
    assert sb.make_llm() is None and sb.make_embed() is None
