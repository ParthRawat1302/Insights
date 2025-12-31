from pydantic import BaseModel
from typing import List, Optional

class Insight(BaseModel):
    type: str
    message: str

class InsightResponse(BaseModel):
    dataset_id: str
    insights: List[Insight]
    summary: Optional[str]
