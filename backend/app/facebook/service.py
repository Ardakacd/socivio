import logging
from fastapi import  HTTPException
from .adapter import FacebookAdapter
from utils.jwt import get_user_id_from_token
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_async_db
from fastapi import Depends
from models.user_tokens import FacebookTokenRequest
from models.facebook import UserFacebookPages, PageInsightRequest, InstagramAccounts, FacebookAndInstagramAccounts, InstagramInsightRequest, InstagramInsightsResponse, FacebookPageInsightsResponse
# Configure logging
logger = logging.getLogger(__name__)

class FacebookService:
    def __init__(self, facebook_adapter: FacebookAdapter):
        self.facebook_adapter = facebook_adapter

    async def init_process(
        self,
        facebook_token: FacebookTokenRequest,
        token: str) -> bool:
        """
        Returns True if facebook tokens are requested successfully, False otherwise.
        """
        
        try:
            user_id = get_user_id_from_token(token)
            
            return await self.facebook_adapter.init_process(facebook_token, user_id)

        except HTTPException as e:
            logger.error(f"HTTP error during request facebook tokens: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during request facebook tokens: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to request facebook tokens")

    async def get_facebook_pages(self, token: str) -> UserFacebookPages:
        try:
            user_id = get_user_id_from_token(token)
            
            return await self.facebook_adapter.get_facebook_pages(user_id)

        except HTTPException as e:
            logger.error(f"HTTP error during getting user pages: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during getting user pages: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to getting user pages")


    async def get_facebook_page_insights(
        self,
        page_insight_request: PageInsightRequest,
        token: str
    ) -> FacebookPageInsightsResponse:
        try:
            user_id = get_user_id_from_token(token)
            
            return await self.facebook_adapter.get_facebook_page_insights(page_insight_request, user_id)
        except HTTPException as e:
            logger.error(f"HTTP error during getting page insights: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during getting page insights: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to getting page insights")

    async def get_instagram_accounts(self, token: str) -> InstagramAccounts:
        try:
            user_id = get_user_id_from_token(token)
            return await self.facebook_adapter.get_instagram_accounts(user_id)
        except HTTPException as e:
            logger.error(f"HTTP error during getting instagram accounts: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during getting instagram accounts: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to getting instagram accounts")

    async def get_facebook_and_instagram_accounts(self, token: str) -> FacebookAndInstagramAccounts:
        try:
            user_id = get_user_id_from_token(token)
            return await self.facebook_adapter.get_facebook_and_instagram_accounts(user_id)
        except HTTPException as e:
            logger.error(f"HTTP error during getting facebook and instagram accounts: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during getting facebook and instagram accounts: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to getting facebook and instagram accounts")

    async def get_instagram_insights(
        self,
        insight_request: InstagramInsightRequest,
        token: str
    ) -> InstagramInsightsResponse:
        try:
            user_id = get_user_id_from_token(token)
            return await self.facebook_adapter.get_instagram_insights(insight_request, user_id)
        except HTTPException as e:
            logger.error(f"HTTP error during getting instagram insights: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during getting instagram insights: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to getting instagram insights")



   
def get_facebook_service(db: AsyncSession = Depends(get_async_db)) -> FacebookService:
    facebook_adapter = FacebookAdapter(db)
    return FacebookService(facebook_adapter)
