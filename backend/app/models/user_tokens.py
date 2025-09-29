from typing import Union, Optional
from pydantic import BaseModel
from db.models.user_tokens import PlatformType


class TokenRequest(BaseModel):
    code: str

class YoutubeTokenRequest(TokenRequest):
    pass

class FacebookTokenRequest(TokenRequest):
    pass

class YoutubeToken(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int

class FacebookToken(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None   # always None for Facebook
    expires_in: int

class CreateUserToken(BaseModel):
    user_id: int
    tokens: Union[YoutubeToken, FacebookToken]
    platform: PlatformType