from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class OpSummary(BaseModel):
    op: str
    last_updated: Optional[str] = None
    total_hides: int
    avg_yield: Optional[float] = None
    predominant_class: Optional[str] = None


class ClassDistribution(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    class_name: str = Field(serialization_alias="class")
    count: int
    pct: float


class OpDetail(BaseModel):
    op: str
    total_hides: int
    avg_area: Optional[float] = None
    avg_yield: Optional[float] = None
    class_distribution: list[ClassDistribution] = []


class OpListResponse(BaseModel):
    items: list[OpSummary]
    total: int
    page: int
    limit: int
    pages: int


class DashboardPeriod(BaseModel):
    total_hides: int
    avg_yield: Optional[float] = None


class RecentOp(BaseModel):
    op: str
    date: str
    total_hides: int


class DashboardResponse(BaseModel):
    today: DashboardPeriod
    week: DashboardPeriod
    today_class_distribution: list[ClassDistribution] = []
    recent_ops: list[RecentOp] = []
