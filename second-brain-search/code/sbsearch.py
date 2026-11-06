"""마크다운 노트 하이브리드 검색 (참조 구현).

- 색인: 노트를 제목/헤딩 단위 청크로 자르고, 각 청크 앞에 '제목 > 헤딩 + description + tags' 문맥을 붙임
- 키워드: SQLite FTS5(BM25). 텍스트는 Kiwi 형태소로 쪼갠 뒤 저장 (조사·어미 때문에 놓치는 검색 방지)
- 벡터(선택): OpenAI 호환 /embeddings 엔드포인트. 없으면 건너뜀
- 질의 확장·재정렬(선택): OpenAI 호환 /chat/completions 엔드포인트 (자체 호스팅 LLM)
- 융합: RRF (Reciprocal Rank Fusion)
외부로 나가는 호출은 환경변수로 지정한 엔드포인트뿐입니다.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import struct
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

_KIWI = None
KEEP_TAGS = ("N", "V", "XR", "SL", "SN", "SH", "MM")


def _kiwi():
    global _KIWI
    if _KIWI is None:
        from kiwipiepy import Kiwi
        _KIWI = Kiwi()
    return _KIWI


def tokenize(text: str) -> list[str]:
    """형태소 중 내용어만 남김. 영문은 소문자."""
    out = []
    for t in _kiwi().tokenize(text):
        if t.tag.startswith(KEEP_TAGS):
            out.append(t.form.lower())
    return out


# ---------- 노트 파싱 ----------
FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    m = FM_RE.match(text)
    if not m:
        return {}, text
    meta: dict = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            meta[k.strip()] = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
        else:
            meta[k.strip()] = v.strip("'\"")
    return meta, text[m.end():]


@dataclass
class Chunk:
    path: str
    heading: str
    body: str
    context: str  # 색인에만 쓰는 문맥(제목·description·태그·별칭)


def chunk_note(path: str, text: str, max_chars: int = 900) -> list[Chunk]:
    meta, body = parse_frontmatter(text)
    title = meta.get("name") or Path(path).stem
    ctx_bits = [title]
    for key in ("description", "aliases", "tags"):
        v = meta.get(key)
        if v:
            ctx_bits.append(" ".join(v) if isinstance(v, list) else str(v))
    ctx = " | ".join(ctx_bits)

    sections: list[tuple[str, list[str]]] = [("", [])]
    for line in body.splitlines():
        if re.match(r"^#{1,4}\s", line):
            sections.append((line.lstrip("# ").strip(), []))
        else:
            sections[-1][1].append(line)

    chunks: list[Chunk] = []
    for heading, lines in sections:
        text_ = "\n".join(lines).strip()
        if not text_:
            continue
        # 너무 긴 섹션은 문단 단위로 다시 자름
        buf = ""
        for para in re.split(r"\n\s*\n", text_):
            if buf and len(buf) + len(para) > max_chars:
                chunks.append(Chunk(path, heading, buf.strip(), f"{ctx} > {heading}"))
                buf = ""
            buf += para + "\n\n"
        if buf.strip():
            chunks.append(Chunk(path, heading, buf.strip(), f"{ctx} > {heading}"))
    if not chunks and ctx:
        chunks.append(Chunk(path, "", "", ctx))
    return chunks


# ---------- 저장소 ----------
def _pack(v: list[float]) -> bytes:
    return struct.pack(f"{len(v)}f", *v)


def _unpack(b: bytes) -> list[float]:
    return list(struct.unpack(f"{len(b) // 4}f", b))


class Index:
    def __init__(self, db_path: str = "sbsearch.sqlite", tokenizer: Callable[[str], list[str]] = tokenize):
        self.db = sqlite3.connect(db_path)
        self.tok = tokenizer
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS chunks(
              id INTEGER PRIMARY KEY, path TEXT, heading TEXT, body TEXT, context TEXT, vec BLOB);
            CREATE VIRTUAL TABLE IF NOT EXISTS fts USING fts5(toks, tokenize='unicode61');
            """
        )

    def clear(self):
        self.db.executescript("DELETE FROM chunks; DELETE FROM fts;")

    def add_chunks(self, chunks: Iterable[Chunk], embed: Callable[[list[str]], list[list[float]]] | None = None):
        chunks = list(chunks)
        vecs = embed([f"{c.context}\n{c.body}" for c in chunks]) if embed and chunks else [None] * len(chunks)
        for c, v in zip(chunks, vecs):
            cur = self.db.execute(
                "INSERT INTO chunks(path,heading,body,context,vec) VALUES(?,?,?,?,?)",
                (c.path, c.heading, c.body, c.context, _pack(v) if v else None),
            )
            toks = " ".join(self.tok(f"{c.context}\n{c.body}"))
            self.db.execute("INSERT INTO fts(rowid,toks) VALUES(?,?)", (cur.lastrowid, toks))
        self.db.commit()

    def index_dir(self, root: str, embed=None, pattern: str = "**/*.md"):
        self.clear()
        for p in sorted(Path(root).glob(pattern)):
            if any(part.startswith(".") for part in p.relative_to(root).parts):
                continue
            self.add_chunks(chunk_note(str(p.relative_to(root)), p.read_text(encoding="utf-8")), embed)

    # --- 검색 ---
    def bm25(self, query: str, k: int = 30) -> list[int]:
        toks = list(dict.fromkeys(self.tok(query)))
        if not toks:
            return []
        q = " OR ".join('"' + t.replace('"', "") + '"' for t in toks)
        rows = self.db.execute(
            "SELECT rowid FROM fts WHERE fts MATCH ? ORDER BY bm25(fts) LIMIT ?", (q, k)
        ).fetchall()
        return [r[0] for r in rows]

    def vector(self, qvec: list[float], k: int = 30) -> list[int]:
        import math

        def norm(v):
            n = math.sqrt(sum(x * x for x in v)) or 1.0
            return [x / n for x in v]

        qn = norm(qvec)
        scored = []
        for rid, blob in self.db.execute("SELECT id, vec FROM chunks WHERE vec IS NOT NULL"):
            v = norm(_unpack(blob))
            scored.append((sum(a * b for a, b in zip(qn, v)), rid))
        scored.sort(reverse=True)
        return [rid for _, rid in scored[:k]]

    def get(self, rid: int) -> dict:
        r = self.db.execute("SELECT path,heading,body FROM chunks WHERE id=?", (rid,)).fetchone()
        return {"id": rid, "path": r[0], "heading": r[1], "body": r[2]}


def rrf(rankings: list[list[int]], k: int = 60) -> list[int]:
    score: dict[int, float] = {}
    for ranking in rankings:
        for rank, rid in enumerate(ranking):
            score[rid] = score.get(rid, 0.0) + 1.0 / (k + rank + 1)
    return [rid for rid, _ in sorted(score.items(), key=lambda x: -x[1])]


def search(
    idx: Index,
    query: str,
    n: int = 5,
    expand: Callable[[str], list[str]] | None = None,
    embed: Callable[[list[str]], list[list[float]]] | None = None,
    rerank: Callable[[str, list[dict]], list[int]] | None = None,
    pool: int = 20,
) -> list[dict]:
    queries = [query] + (expand(query) if expand else [])
    rankings = [idx.bm25(q) for q in queries]
    if embed:
        rankings += [idx.vector(embed([q])[0]) for q in queries[:1]]  # 원 질문만 벡터 검색
    fused = rrf(rankings)[:pool]
    cands = [idx.get(r) for r in fused]
    if rerank and cands:
        order = rerank(query, cands)
        cands = [cands[i] for i in order if 0 <= i < len(cands)] or cands
    # 같은 노트의 청크는 가장 높은 것 하나만 남김
    seen, out = set(), []
    for c in cands:
        if c["path"] in seen:
            continue
        seen.add(c["path"])
        out.append(c)
    return out[:n]


# ---------- 자체 호스팅 LLM 연결 (OpenAI 호환) ----------
def _post(url: str, payload: dict, key: str, timeout: int = 60) -> dict:
    req = urllib.request.Request(
        url, json.dumps(payload).encode(), {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def make_llm(post=_post):
    base, model, key = os.environ.get("SB_LLM_BASE_URL", ""), os.environ.get("SB_LLM_MODEL", ""), os.environ.get("SB_LLM_API_KEY", "")
    if not base or not model:
        return None

    def chat(prompt: str) -> str:
        r = post(base.rstrip("/") + "/chat/completions", {"model": model, "temperature": 0,
                 "messages": [{"role": "user", "content": prompt}]}, key)
        return r["choices"][0]["message"]["content"]

    return chat


def make_expand(chat) -> Callable[[str], list[str]]:
    def expand(q: str) -> list[str]:
        out = chat(
            "노트 검색용 질의 확장. 아래 질문의 동의어, 영문/한글 병기 용어, 약어 풀이를 포함한 검색어 3개를 "
            f"한 줄에 하나씩, 설명 없이 출력.\n질문: {q}"
        )
        return [l.strip("-• \t") for l in out.splitlines() if l.strip()][:3]

    return expand


def make_rerank(chat) -> Callable[[str, list[dict]], list[int]]:
    def rerank(q: str, cands: list[dict]) -> list[int]:
        listing = "\n".join(f"[{i}] {c['path']} / {c['heading']}: {c['body'][:200]}" for i, c in enumerate(cands))
        out = chat(
            f"질문: {q}\n아래 후보를 질문과 관련 깊은 순서로 번호만 쉼표로 나열. 설명 금지.\n{listing}"
        )
        nums = [int(x) for x in re.findall(r"\d+", out)]
        seen = list(dict.fromkeys(nums))
        return seen + [i for i in range(len(cands)) if i not in seen]

    return rerank


def make_embed(post=_post):
    base, model, key = os.environ.get("SB_EMBED_BASE_URL", ""), os.environ.get("SB_EMBED_MODEL", ""), os.environ.get("SB_EMBED_API_KEY", "")
    if not base or not model:
        return None

    def embed(texts: list[str]) -> list[list[float]]:
        out = []
        for i in range(0, len(texts), 32):
            r = post(base.rstrip("/") + "/embeddings", {"model": model, "input": texts[i:i + 32]}, key)
            out += [d["embedding"] for d in r["data"]]
        return out

    return embed


# ---------- 평가 ----------
def evaluate(idx: Index, qa: list[dict], k: int = 5, **kw) -> dict:
    """qa: [{'q': 질문, 'gold': [정답 노트 경로, ...]}]"""
    hit, rr = 0, 0.0
    for item in qa:
        res = [r["path"] for r in search(idx, item["q"], n=k, **kw)]
        ranks = [res.index(g) + 1 for g in item["gold"] if g in res]
        if ranks:
            hit += 1
            rr += 1.0 / min(ranks)
    return {f"recall@{k}": hit / len(qa), "mrr": rr / len(qa), "n": len(qa)}


def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["index", "search", "eval"])
    ap.add_argument("arg", help="index: 노트 폴더 / search: 질문 / eval: qa.json 경로")
    ap.add_argument("--db", default="sbsearch.sqlite")
    ap.add_argument("--notes", help="eval/search 시 색인을 새로 만들 때 노트 폴더")
    ap.add_argument("-n", type=int, default=5)
    ap.add_argument("--no-llm", action="store_true", help="LLM 질의 확장·재정렬 끄기")
    a = ap.parse_args()

    idx = Index(a.db)
    embed = make_embed()
    chat = None if a.no_llm else make_llm()
    kw = {"embed": embed, "expand": make_expand(chat) if chat else None, "rerank": make_rerank(chat) if chat else None}
    if a.cmd == "index":
        idx.index_dir(a.arg, embed)
        print("색인 완료:", idx.db.execute("SELECT count(*) FROM chunks").fetchone()[0], "청크")
    elif a.cmd == "search":
        for r in search(idx, a.arg, n=a.n, **kw):
            print(f"{r['path']}  # {r['heading']}\n    {r['body'][:120].replace(chr(10), ' ')}")
    else:
        qa = json.loads(Path(a.arg).read_text(encoding="utf-8"))
        print(json.dumps(evaluate(idx, qa, k=a.n, **kw), ensure_ascii=False))


if __name__ == "__main__":
    main()
