from pydantic import BaseModel


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