from pydantic import BaseModel
from typing import Optional


class Hide(BaseModel):
    id: int
    hide_num: str
    op: str
    processed_at: str
    class_name: str
    yield_pct: Optional[float] = None
    area: Optional[float] = None
    image_available: bool = False
    prev_hide_id: Optional[int] = None
    next_hide_id: Optional[int] = None
