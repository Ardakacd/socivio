from pydantic import BaseModel, ConfigDict
from datetime import datetime

class YoutubeReportRequest(BaseModel):
    start_date: str
    end_date: str
    metrics: str
    dimensions: str
    filters: str
    ids: str = "channel==MINE"

class YoutubeReport(BaseModel):
    report: list[dict]
    ids: str

class YoutubeChannel(BaseModel):
    id: str
    title: str
    description: str
    connected_at: datetime
    model_config = ConfigDict(extra="forbid")

class YoutubeChannels(BaseModel):
    youtube_channels: list[YoutubeChannel]