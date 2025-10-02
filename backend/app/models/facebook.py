from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class FacebookPage(BaseModel):
    id: str
    name: str
    access_token: Optional[str] = None
    connected_at: datetime
    model_config = ConfigDict(extra="forbid")

class UserFacebookPages(BaseModel):
    facebook_pages: list[FacebookPage]

class PageInsightRequest(BaseModel):
    page_id: str
    metrics: List[str]
    period:Optional[str] = "day"     
    since: Optional[str] = None  
    until: Optional[str] = None 

class InstagramAccount(BaseModel):
    id: str
    name: str
    connected_at: datetime

class InstagramAccounts(BaseModel):
    instagram_accounts: list[InstagramAccount]

class FacebookAndInstagramAccounts(BaseModel):
    facebook_pages: list[FacebookPage]
    instagram_accounts: list[InstagramAccount]