from typing import List, Literal, Annotated, Union
from pydantic import BaseModel, Field


class WidgetBase(BaseModel):
    widget_id: str
    type: Literal["chart", "kpi"]


class ChartWidget(WidgetBase):
    type: Literal["chart"]
    chart_type: Literal["line", "bar", "scatter"]
    x: str
    y: str
    aggregation: str | None = None
    data: List[dict] = []       # ✅ REQUIRED


class KPIWidget(WidgetBase):
    type: Literal["kpi"]
    value: float
    metric: str
    format: str | None = None


Widget = Annotated[
    Union[KPIWidget, ChartWidget],
    Field(discriminator="type")
]


class DashboardResponse(BaseModel):
    dashboard_id: str
    dataset_id: str
    title: str
    widgets: List[Widget]


class DashboardCreateResponse(BaseModel):
    dashboard_id: str





