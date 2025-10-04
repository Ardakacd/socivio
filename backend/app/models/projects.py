from pydantic import BaseModel, Field
from typing import Optional

class ProjectCreate(BaseModel):
    external_account_id: str = Field(min_length=1, description="External account ID")
    allow_insights: Optional[bool] = Field(default=False, description="Allow insights")
    allow_ai_replies: Optional[bool] = Field(default=False, description="Allow AI replies")


class Project(BaseModel):
    id: str
    external_account_id: str
    allow_insights: bool
    allow_ai_replies: bool


class ToggleProjectFlag(BaseModel):
    external_account_id: str
    allow: bool

