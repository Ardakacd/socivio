import logging
from typing import List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from models.user_tokens import FacebookTokenRequest, PlatformType
from user_tokens.adapter import UserTokenAdapter
from models.facebook import UserFacebookPages, FacebookPage, PageInsightRequest, InstagramAccounts, InstagramAccount, FacebookAndInstagramAccounts

logger = logging.getLogger(__name__)


class FacebookAdapter:
    """
    Facebook adapter for facebook operations.
    
    This adapter provides async interface for facebook operations
    with proper error handling and session management.
    """

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.user_token_adapter = UserTokenAdapter(self.db_session)
    
    
    async def init_process(self, facebook_token: FacebookTokenRequest, user_id: int) -> bool:
        """
        Create a new Facebook project and wait until it is fully created.
        
        Returns:
            bool: True if project is created successfully, False otherwise.
        """
        try:
            user_tokens = await self.user_token_adapter.request_facebook_tokens(facebook_token, user_id)
            if not user_tokens:
                raise HTTPException(status_code=404, detail="Facebook tokens not found")
            
            return True

        except HTTPException:
            logger.error(f"HTTP error while creating project for user_id={user_id}: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while creating project for user_id={user_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to create project")

    async def get_facebook_pages(self, user_id: str, is_instagram: bool = False) -> UserFacebookPages:
        try:
            user_tokens = await self.user_token_adapter.get_tokens_by_user_id(user_id, PlatformType.facebook)
            pages: list[FacebookPage] = []

            for token in user_tokens:
                user_access_token = token.access_token
            
                url = "https://graph.facebook.com/v21.0/me/accounts"
                params = {"access_token": user_access_token}

                async with httpx.AsyncClient() as client:
                    resp = await client.get(url, params=params)
                    data = resp.json()

                if "data" in data:
                    pages.extend([FacebookPage(id=page["id"], name=page["name"], connected_at=token.created_at, access_token=page["access_token"] if is_instagram else None) for page in data["data"]])
            
            return UserFacebookPages(facebook_pages=pages)

        except HTTPException as e:
            logger.error(f"HTTP error during get_facebook_pages: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"FacebookAdapter.get_facebook_pages: Unexpected error {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to fetch Facebook pages")


    async def get_page_insights(
        self,
        page_insight_request: PageInsightRequest,
        user_id: str
    ):
        try:
            user_tokens = await self.user_token_adapter.get_tokens_by_user_id(user_id, PlatformType.facebook)
            if not user_tokens:
                raise HTTPException(status_code=404, detail="Facebook tokens not found")

            user_access_token = user_tokens.access_token

            url_pages = "https://graph.facebook.com/v21.0/me/accounts"
            async with httpx.AsyncClient() as client:
                resp_pages = await client.get(url_pages, params={"access_token": user_access_token})
                pages_data = resp_pages.json()

            if "data" not in pages_data:
                logger.error(f"Failed to fetch pages: {pages_data}")
                raise HTTPException(status_code=400, detail="Failed to fetch pages")

            page_info = next((p for p in pages_data["data"] if p["id"] == page_insight_request.page_id), None)
            if not page_info:
                raise HTTPException(status_code=404, detail="Page not found or not accessible")

            page_access_token = page_info["access_token"]

            url_insights = f"https://graph.facebook.com/v21.0/{page_insight_request.page_id}/insights"
            params = {
                "metric": ",".join(page_insight_request.metrics),
                "period": page_insight_request.period,
                "access_token": page_access_token,
            }
            if page_insight_request.since:
                params["since"] = page_insight_request.since
            if page_insight_request.until:
                params["until"] = page_insight_request.until

            async with httpx.AsyncClient() as client:
                resp_insights = await client.get(url_insights, params=params)
                insights_data = resp_insights.json()

            if "data" not in insights_data:
                logger.error(f"Failed to fetch insights for page {page_insight_request.page_id}: {insights_data}")
                raise HTTPException(status_code=400, detail="Failed to fetch page insights")

            return insights_data["data"]

        except HTTPException as e:
            logger.error(f"HTTP error during get_page_insights: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"FacebookAdapter.get_page_insights: Unexpected error {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to fetch page insights")

    async def get_instagram_accounts(self, user_id: str) -> InstagramAccounts:
        try:
            pages = await self.get_facebook_pages(user_id, is_instagram=True)
            instagram_accounts: InstagramAccounts  = []
            for page in pages.facebook_pages:
                url = f"https://graph.facebook.com/v21.0/{page.id}"
                params = {
                    "fields": "connected_instagram_account",
                    "access_token": page.access_token,
                }

                async with httpx.AsyncClient() as client:
                    resp = await client.get(url, params=params)
                    resp = resp.json()
                
                if "connected_instagram_account" in resp:
                    instagram_accounts.append(InstagramAccount(id=resp["connected_instagram_account"]["id"], name=resp["connected_instagram_account"]["name"], connected_at=page.connected_at))
            return InstagramAccounts(instagram_accounts=instagram_accounts)
        except HTTPException as e:
            logger.error(f"HTTP error during get_instagram_accounts: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"FacebookAdapter.get_instagram_accounts: Unexpected error {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to fetch instagram accounts")

    async def get_facebook_and_instagram_accounts(self, user_id: str) -> FacebookAndInstagramAccounts:
        try:
            pages_response = await self.get_facebook_pages(user_id, is_instagram=True)
            pages = pages_response.facebook_pages

            instagram_accounts: list[InstagramAccount] = []
            for page in pages:
                url = f"https://graph.facebook.com/v21.0/{page.id}"
                params = {
                    "fields": "connected_instagram_account{name,username}",
                    "access_token": page.access_token,
                }
                async with httpx.AsyncClient() as client:
                    resp = await client.get(url, params=params)
                    resp_json = resp.json()
                if "connected_instagram_account" in resp_json and resp_json["connected_instagram_account"]:
                    ig = resp_json["connected_instagram_account"]
                    instagram_accounts.append(InstagramAccount(
                        id=ig.get("id", ""),
                        name=ig.get("username") or ig.get("name") or "",
                        connected_at=page.connected_at
                    ))

            return FacebookAndInstagramAccounts(
                facebook_pages=pages,
                instagram_accounts=instagram_accounts
            )
        except HTTPException as e:
            logger.error(f"HTTP error during get_facebook_and_instagram_accounts: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"FacebookAdapter.get_facebook_and_instagram_accounts: Unexpected error {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to fetch facebook and instagram accounts")


    

    