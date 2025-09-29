from pydantic import BaseModel, ConfigDict
from typing import List, Optional



class FacebookPage(BaseModel):
    id: str
    name: str

    model_config = ConfigDict(extra="forbid")

class UserFacebookPages(BaseModel):
    facebook_pages: list[FacebookPage]

class PageInsightRequest(BaseModel):
    page_id: str
    metrics: List[str]
    period:Optional[str] = "day"     
    since: Optional[str] = None  
    until: Optional[str] = None 
