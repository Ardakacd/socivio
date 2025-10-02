import logging
from fastapi import HTTPException, Depends
from models.accounts import ConnectedAccounts
from facebook.service import FacebookService, get_facebook_service
from youtube.service import YoutubeService, get_youtube_service

logger = logging.getLogger(__name__)


class AccountsService:
    def __init__(self, facebook_service: FacebookService, youtube_service: YoutubeService):
        self.facebook_service = facebook_service
        self.youtube_service = youtube_service

    async def get_connected_accounts(self, token: str) -> ConnectedAccounts:
        try:
            fb = await self.facebook_service.get_facebook_and_instagram_accounts(token)
            yt = await self.youtube_service.get_channels(token)

            return ConnectedAccounts(
                facebook_pages=fb.facebook_pages,
                instagram_accounts=fb.instagram_accounts,
                youtube_channels=yt.youtube_channels,
            )
        except HTTPException as e:
            logger.error(f"HTTP error during get_connected_accounts: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during get_connected_accounts: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to get connected accounts")


def get_accounts_service(
    facebook_service: FacebookService = Depends(get_facebook_service),
    youtube_service: YoutubeService = Depends(get_youtube_service),
) -> AccountsService:
    return AccountsService(facebook_service, youtube_service)


