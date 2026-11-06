"""JSON 파일 저장소(원본 진실)와 사람 검토 큐. 그래프/CSV는 여기서 파생."""
import json
from pathlib import Path

from .schema import PaperRecord


class Store:
    def __init__(self, root: Path):
        self.root = Path(root)
        (self.root / "records").mkdir(parents=True, exist_ok=True)
        self.review_path = self.root / "review_queue.jsonl"

    def save(self, rec: PaperRecord, queue: list[dict]) -> Path:
        p = self.root / "records" / f"{rec.paper_id}.json"
        p.write_text(rec.model_dump_json(indent=2), encoding="utf-8")
        # 같은 논문의 이전 큐 항목은 교체
        keep = [l for l in self._read_queue() if l.get("paper_id") != rec.paper_id]
        with self.review_path.open("w", encoding="utf-8") as f:
            for item in keep + queue:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        return p

    def _read_queue(self) -> list[dict]:
        if not self.review_path.exists():
            return []
        return [json.loads(l) for l in self.review_path.read_text(encoding="utf-8").splitlines() if l.strip()]

    def load(self, paper_id: str) -> PaperRecord:
        return PaperRecord.model_validate_json((self.root / "records" / f"{paper_id}.json").read_text(encoding="utf-8"))

    def all(self) -> list[PaperRecord]:
        return [PaperRecord.model_validate_json(p.read_text(encoding="utf-8"))
                for p in sorted((self.root / "records").glob("*.json"))]
