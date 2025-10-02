from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    external_account_id: str = Field(min_length=1)


class Project(BaseModel):
    id: str
    external_account_id: str
    user_id: int


