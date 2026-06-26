from pydantic import BaseModel
from typing import Optional


class OpSummary(BaseModel):
    op: str
    last_updated: Optional[str] = None
    total_hides: int
    avg_yield: Optional[float] = None
    predominant_class: Optional[str] = None


class ClassDistribution(BaseModel):
    class_name: str
    count: int
    pct: float


class OpDetail(BaseModel):
    op: str
    total_hides: int
    avg_area: Optional[float] = None
    avg_yield: Optional[float] = None
    class_distribution: list[ClassDistribution] = []
