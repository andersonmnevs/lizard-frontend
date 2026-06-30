from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class HideItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    hide_num: str
    processed_at: str
    class_name: str = Field(serialization_alias="class")
    yield_pct: Optional[float] = None
    area: Optional[float] = None
    op: str


class HideListResponse(BaseModel):
    items: list[HideItem]
    total: int
    page: int
    limit: int


class HideDetail(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    hide_num: str
    op: str
    processed_at: str
    class_name: str = Field(serialization_alias="class")
    yield_pct: Optional[float] = None
    area: Optional[float] = None
    image_available: bool = False
    prev_hide_id: Optional[int] = None
    next_hide_id: Optional[int] = None
