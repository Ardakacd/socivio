from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Union
from datetime import datetime
from models.projects import ProjectInsightResponse


class FacebookPage(BaseModel):
    id: str
    external_id: str
    name: str
    access_token: Optional[str] = None
    connected_at: datetime
    model_config = ConfigDict(extra="forbid")

class UserFacebookPages(BaseModel):
    facebook_pages: list[FacebookPage]

class PageInsightRequest(BaseModel):
    page_id: str
    external_id: str
    metrics: List[str]
    period:Optional[str] = "day"     
    since: Optional[str] = None  
    until: Optional[str] = None 

class InstagramAccount(BaseModel):
    id: str
    external_id: str
    name: str
    connected_at: datetime

class InstagramAccounts(BaseModel):
    instagram_accounts: list[InstagramAccount]

class InstagramInsightRequest(BaseModel):
    instagram_id: str
    external_id: str
    metrics: List[str]
    period: Optional[str] = "day"
    since: Optional[str] = None
    until: Optional[str] = None

class FacebookAndInstagramAccounts(BaseModel):
    facebook_pages: list[FacebookPage]
    instagram_accounts: list[InstagramAccount]

class FacebookInsightValue(BaseModel):
    value: Union[int, float, dict]
    end_time: Optional[datetime] = None

class FacebookInsightData(BaseModel):
    name: str
    period: str
    values: List[FacebookInsightValue]
    title: Optional[str] = None
    description: Optional[str] = None
    id: Optional[str] = None  

class FacebookPageInsightsResponse(BaseModel):
    data: List[FacebookInsightData]
    project: ProjectInsightResponse

class InstagramInsightValue(BaseModel):
    value: Union[int, float, dict]
    end_time: Optional[datetime] = None

class InstagramInsightData(BaseModel):
    name: str
    period: str
    values: List[InstagramInsightValue]
    title: Optional[str] = None
    description: Optional[str] = None

class InstagramInsightsResponse(BaseModel):
    data: List[InstagramInsightData]
    project: ProjectInsightResponse