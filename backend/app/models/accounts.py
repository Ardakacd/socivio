from pydantic import BaseModel
from typing import List
from .facebook import FacebookPage, InstagramAccount
from .youtube import YoutubeChannel


class ConnectedAccounts(BaseModel):
    facebook_pages: List[FacebookPage]
    instagram_accounts: List[InstagramAccount]
    youtube_channels: List[YoutubeChannel]


