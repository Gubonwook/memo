"""환경변수 기반 설정. 키는 코드에 쓰지 말고 환경변수/.env로만 둔다."""
import os
from dataclasses import dataclass, field
from pathlib import Path


def load_dotenv(path: str = ".env") -> None:
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


@dataclass
class Endpoint:
    base_url: str = ""
    model: str = ""
    api_key: str = ""

    @property
    def ready(self) -> bool:
        return bool(self.base_url and self.model)


@dataclass
class Config:
    llm: Endpoint = field(default_factory=Endpoint)
    vlm: Endpoint = field(default_factory=Endpoint)
    fig_samples: int = 3
    data_dir: Path = Path("./data")

    @classmethod
    def from_env(cls) -> "Config":
        load_dotenv()
        g = os.environ.get
        return cls(
            llm=Endpoint(g("ALD_LLM_BASE_URL", ""), g("ALD_LLM_MODEL", ""), g("ALD_LLM_API_KEY", "")),
            vlm=Endpoint(g("ALD_VLM_BASE_URL", ""), g("ALD_VLM_MODEL", ""), g("ALD_VLM_API_KEY", "")),
            fig_samples=int(g("ALD_FIG_SAMPLES", "3")),
            data_dir=Path(g("ALD_DATA_DIR", "./data")),
        )
