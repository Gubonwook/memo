"""ALD 논문 추출 스키마. 모든 수치는 근거(page, quote)를 달고 다닌다."""
from typing import Literal, Optional
from pydantic import BaseModel, Field


class Source(BaseModel):
    page: Optional[int] = None
    quote: str = ""                       # 논문 원문 그대로의 근거 문장/표 행
    method: Literal["text", "table", "figure", "derived"] = "text"
    ref: str = ""                         # 예: "Table 2", "Fig. 3b"


class Measurement(BaseModel):
    name: str                             # growth_per_cycle, thickness, resistivity, ...
    value: Optional[float] = None
    unit: str = ""
    condition: str = ""                   # 예: "at 250 C", "after anneal"
    method_of_measurement: str = ""       # XRR, ellipsometry, XPS ...
    source: Source = Field(default_factory=Source)
    norm_value: Optional[float] = None    # 정규화 값 (verify에서 채움; 원본 value/unit은 보존)
    norm_unit: str = ""
    confidence: float = 1.0               # 0~1, verify 단계에서 조정
    flags: list[str] = Field(default_factory=list)   # 검증 경고


class Precursor(BaseModel):
    name: str
    role: Literal["metal", "ligand", "other"] = "metal"
    pulse_s: Optional[float] = None
    purge_s: Optional[float] = None
    source_temp_c: Optional[float] = None


class CoReactant(BaseModel):
    name: str                             # H2O, O3, NH3 plasma ...
    plasma: bool = False
    pulse_s: Optional[float] = None
    purge_s: Optional[float] = None


class Process(BaseModel):
    label: str = "P1"                     # 한 논문 내 공정 구분자
    material: str = ""                    # 형성 박막 (예: Al2O3)
    precursors: list[Precursor] = Field(default_factory=list)
    coreactants: list[CoReactant] = Field(default_factory=list)
    substrate: str = ""
    surface_treatment: str = ""           # ASD라면 passivation/inhibitor 등
    is_area_selective: bool = False
    deposition_temp_c: Optional[float] = None
    reactor_pressure_torr: Optional[float] = None
    cycles: Optional[int] = None
    supercycle: str = ""                  # 예: "1x(TMIn+H2O) : 4x(...)"
    measurements: list[Measurement] = Field(default_factory=list)
    notes: str = ""


class FigurePoint(BaseModel):
    x: float
    y: float
    spread: float = 0.0                   # 반복 추출 간 상대 편차 (불확실성)
    n: int = 1


class FigureSeries(BaseModel):
    name: str
    points: list[FigurePoint] = Field(default_factory=list)


class FigureData(BaseModel):
    label: str                            # "Fig. 3"
    page: Optional[int] = None
    caption: str = ""
    x_label: str = ""
    x_unit: str = ""
    y_label: str = ""
    y_unit: str = ""
    series: list[FigureSeries] = Field(default_factory=list)
    n_samples: int = 0
    flags: list[str] = Field(default_factory=list)


class PaperRecord(BaseModel):
    paper_id: str
    title: str = ""
    doi: str = ""
    year: Optional[int] = None
    processes: list[Process] = Field(default_factory=list)
    figures: list[FigureData] = Field(default_factory=list)
    extractor: str = ""                   # 모델 이름/버전 기록 (재현성)
    schema_version: str = "0.1"
