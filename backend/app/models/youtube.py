from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional, Union
from models.projects import ProjectInsightResponse

class YoutubeReportRequest(BaseModel):
    start_date: str
    end_date: str
    metrics: str
    dimensions: str
    filters: str
    ids: str
    external_id: str


class YoutubeChannel(BaseModel):
    id: str
    external_id: str
    title: str
    description: str
    connected_at: datetime
    model_config = ConfigDict(extra="forbid")

class YoutubeChannels(BaseModel):
    youtube_channels: list[YoutubeChannel]

class ColumnHeader(BaseModel):
    name: str
    dataType: str
    columnType: str


class YoutubeAnalyticsResponse(BaseModel):
    kind: Optional[str] = None
    columnHeaders: List[ColumnHeader]
    rows: Optional[List[List[Union[str, int, float]]]] = None

class YoutubeReport(BaseModel):
    report: YoutubeAnalyticsResponse
    project: ProjectInsightResponse
    ids: str