from pydantic import BaseModel
from db.models.user_tokens import PlatformType

class YoutubeTokenRequest(BaseModel):
    code: str

class YoutubeToken(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int

class CreateUserToken(BaseModel):
    user_id: int
    tokens: YoutubeToken
    platform: PlatformType