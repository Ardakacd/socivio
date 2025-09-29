from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import select
import logging
from fastapi import HTTPException
from db.models.user_tokens import UserTokenModel, PlatformType
from models.user_tokens import YoutubeTokenRequest, YoutubeToken, CreateUserToken, FacebookTokenRequest, FacebookToken
from core.config import settings
import httpx
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)


class UserTokenAdapter:
    """
    User token adapter for database operations.
    
    This adapter provides async interface for user token CRUD operations
    with proper error handling and session management.
    """
    
    def __init__(self, session: AsyncSession):
        self.db: AsyncSession = session
    
    
    async def request_youtube_tokens(self, youtube_token_request: YoutubeTokenRequest, user_id: int) -> Optional[UserTokenModel]:
        """
        Request youtube tokens from Google.
        """
        
        try:
            URL = "https://oauth2.googleapis.com/token"

            HEADERS = {
                "Content-Type": "application/x-www-form-urlencoded",
            }

            payload = {
                "code": youtube_token_request.code,
                "client_id": settings.YOUTUBE_CLIENT_ID,
                "client_secret": settings.YOUTUBE_CLIENT_SECRET,
                "redirect_uri": settings.YOUTUBE_REDIRECT_URL,
                "grant_type": "authorization_code",
            }

            with httpx.Client() as client:
                response = client.post(URL, headers=HEADERS, data=payload)
                data = response.json()
                
                youtube_token = YoutubeToken(
                    access_token=data["access_token"],
                    refresh_token=data["refresh_token"],
                    expires_in=data["expires_in"]
                )

                user_token = CreateUserToken(
                    user_id=user_id,
                    tokens=youtube_token,
                    platform=PlatformType.youtube
                )

                return await self.create_user_token(user_token)
        except HTTPException as e:
            logger.error(f'HTTPException has occurred: {e}')
            raise
        except Exception as e:
            logger.error(f'Error has occurred: {e}')
            raise

    async def create_user_token(self, user_token: CreateUserToken) -> Optional[UserTokenModel]:
        """
        Insert or update a user token for a given user_id and platform.
        If a record exists, overwrite it. Otherwise, insert a new one.
        """
        logger.info(
            f"UserTokenAdapter: Creating/Updating token for user_id={user_token.user_id}, platform={user_token.platform}"
        )
        try:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=user_token.tokens.expires_in)

            # Check if token exists for user_id + platform
            query = select(UserTokenModel).where(
                UserTokenModel.user_id == user_token.user_id,
                UserTokenModel.platform == user_token.platform,
            )
            result = await self.db.execute(query)
            existing_token = result.scalar_one_or_none()

            if existing_token:
                existing_token.access_token = user_token.tokens.access_token
                existing_token.refresh_token = user_token.tokens.refresh_token
                existing_token.expires_at = expires_at
                db_token = existing_token
                logger.info("UserTokenAdapter: Existing token found, updating it.")
            else:
                db_token = UserTokenModel(
                    user_id=user_token.user_id,
                    access_token=user_token.tokens.access_token,
                    refresh_token=user_token.tokens.refresh_token,
                    expires_at=expires_at,
                    platform=user_token.platform,
                )
                self.db.add(db_token)
                logger.info("UserTokenAdapter: No existing token, creating new one.")

            await self.db.commit()
            return db_token

        except IntegrityError as e:
            logger.error(
                f"UserTokenAdapter: Integrity error for user_id {user_token.user_id}, platform {user_token.platform}: {e}"
            )
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="You already have a token for this platform")
        except SQLAlchemyError as e:
            logger.error(
                f"UserTokenAdapter: Database error for user_id {user_token.user_id}, platform {user_token.platform}: {e}"
            )
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create user token")
        except Exception as e:
            logger.error(
                f"UserTokenAdapter: Unexpected error for user_id {user_token.user_id}, platform {user_token.platform}: {e}",
                exc_info=True,
            )
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create user token")


    async def get_tokens_by_user_id(self, user_id: int, platform: Optional[PlatformType] = None) -> Optional[UserTokenModel]:
        """
        Retrieve all tokens for a given user_id, filtered by platform.
        
        Args:
            user_id: ID of the user
            platform: Platform to filter tokens (PlatformType enum)
        
        Returns:
            UserTokenModel instance if found, None otherwise
        """
        logger.info(f"UserTokenAdapter: Fetching tokens for user_id={user_id}, platform={platform}")
        try:
            query = select(UserTokenModel).where(UserTokenModel.user_id == user_id).where(UserTokenModel.platform == platform)
            
            result = await self.db.execute(query)
            tokens = result.scalar_one_or_none()
            
            if not tokens:
                logger.info(f"UserTokenAdapter: No tokens found for user_id={user_id}, platform={platform}")
                raise HTTPException(status_code=400, detail='No tokens found')

            if platform == PlatformType.youtube and tokens.expires_at and datetime.now(timezone.utc) >= tokens.expires_at:
                logger.info(f"UserTokenAdapter: YouTube token expired for user_id={user_id}, attempting refresh")
                refreshed_tokens = await self.refresh_youtube_token(tokens)
                if refreshed_tokens:
                    return refreshed_tokens
                else:
                    logger.warning(f"UserTokenAdapter: Failed to refresh YouTube token for user_id={user_id}")
                    raise HTTPException(status_code=400, detail='Failed to refresh YouTube token')

            # Facebook → refresh if near expiry (e.g., < 10 days left)
            if platform == PlatformType.facebook and tokens.expires_at:
                now = datetime.now(timezone.utc)
                time_left = tokens.expires_at - now
                if time_left.days <= 10:  
                    logger.info(
                        f"UserTokenAdapter: Facebook token expiring soon "
                        f"(in {time_left.days} days) for user_id={user_id}, attempting refresh"
                    )
                    refreshed_tokens = await self.refresh_facebook_token(tokens)
                    if refreshed_tokens:
                        return refreshed_tokens
                    else:
                        logger.warning(f"UserTokenAdapter: Failed to refresh Facebook token for user_id={user_id}")
                        raise HTTPException(status_code=400, detail="Failed to refresh Facebook token")


            return tokens

        except SQLAlchemyError as e:
            logger.error(f"UserTokenAdapter: Database error fetching tokens for user_id={user_id}, platform={platform}: {e}", exc_info=True)
            raise HTTPException(status_code=400, detail='Failed to get tokens')
        except Exception as e:
            logger.error(f"UserTokenAdapter: Unexpected error fetching tokens for user_id={user_id}, platform={platform}: {e}", exc_info=True)
            raise HTTPException(status_code=400, detail='Failed to get tokens')

    async def refresh_youtube_token(self, user_token: UserTokenModel) -> Optional[UserTokenModel]:
        """
        Refresh an expired YouTube token using the refresh token.
        
        Args:
            user_token: The UserTokenModel with expired access token
            
        Returns:
            Updated UserTokenModel with new tokens, or None if refresh failed
        """
        logger.info(f"UserTokenAdapter: Refreshing YouTube token for user_id={user_token.user_id}")
        
        try:
            URL = "https://oauth2.googleapis.com/token"
            
            HEADERS = {
                "Content-Type": "application/x-www-form-urlencoded",
            }
            
            payload = {
                "refresh_token": user_token.refresh_token,
                "client_id": settings.YOUTUBE_CLIENT_ID,
                "client_secret": settings.YOUTUBE_CLIENT_SECRET,
                "grant_type": "refresh_token",
            }
            
            with httpx.Client() as client:
                response = client.post(URL, headers=HEADERS, data=payload)
                
                if response.status_code != 200:
                    logger.error(f"UserTokenAdapter: YouTube token refresh failed with status {response.status_code}: {response.text}")
                    raise HTTPException(status_code=400, detail='Failed to refresh YouTube token')
                
                data = response.json()
                
                user_token.access_token = data["access_token"]
                #  Google may or may not return a new refresh token
                if "refresh_token" in data:
                    user_token.refresh_token = data["refresh_token"]
                
                expires_in = data.get("expires_in", 3600)  # Default to 1 hour if not provided
                user_token.expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
                
                await self.db.commit()
                
                logger.info(f"UserTokenAdapter: Successfully refreshed YouTube token for user_id={user_token.user_id}")
                return user_token
                
        except httpx.RequestError as e:
            logger.error(f"UserTokenAdapter: Network error during YouTube token refresh for user_id={user_token.user_id}: {e}")
            raise HTTPException(status_code=400, detail='Failed to refresh YouTube token')
        except KeyError as e:
            logger.error(f"UserTokenAdapter: Missing required field in YouTube refresh response for user_id={user_token.user_id}: {e}")
            raise HTTPException(status_code=400, detail='Failed to refresh YouTube token')
        except SQLAlchemyError as e:
            logger.error(f"UserTokenAdapter: Database error during YouTube token refresh for user_id={user_token.user_id}: {e}")
            await self.db.rollback()
            raise HTTPException(status_code=400, detail='Failed to refresh YouTube token')
        except Exception as e:
            logger.error(f"UserTokenAdapter: Unexpected error during YouTube token refresh for user_id={user_token.user_id}: {e}", exc_info=True)
            await self.db.rollback()
            raise HTTPException(status_code=400, detail='Failed to refresh YouTube token')

    async def request_facebook_tokens(self, facebook_token_request: FacebookTokenRequest, user_id: int) -> Optional[CreateUserToken]:
        """
        Exchange authorization code for a Facebook access token.
        Upgrade to a long-lived token and store it.
        """
        try:
            # Exchange code for short-lived token(approximately 2 hours)
            short_lived_url = "https://graph.facebook.com/v21.0/oauth/access_token"
            short_lived_params = {
                "client_id": settings.FACEBOOK_APP_ID,
                "client_secret": settings.FACEBOOK_APP_SECRET,
                "redirect_uri": settings.FACEBOOK_REDIRECT_URI,
                "code": facebook_token_request.code
            }

            with httpx.Client() as client:
                resp = client.get(short_lived_url, params=short_lived_params)
                short_lived_data = resp.json()

                if "access_token" not in short_lived_data:
                    logger.error(f"Failed to get short-lived Facebook token: {short_lived_data}")
                    raise HTTPException(status_code=400, detail='Failed to get short-lived Facebook token')

                short_lived_token = short_lived_data["access_token"]

            # Exchange short-lived token for long-lived token(approximately 60 days)
            return await self._upgrade_to_long_lived(short_lived_token, user_id)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error requesting Facebook tokens: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to request Facebook tokens")

    async def _upgrade_to_long_lived(self, token: str, user_id: int) -> Optional[CreateUserToken]:
        """
        Exchange a short-lived or long-lived token for a fresh long-lived token
        """
        try:
            long_lived_url = "https://graph.facebook.com/v21.0/oauth/access_token"
            long_lived_params = {
                "grant_type": "fb_exchange_token",
                "client_id": settings.FACEBOOK_APP_ID,
                "client_secret": settings.FACEBOOK_APP_SECRET,
                "fb_exchange_token": token,
            }

            with httpx.Client() as client:
                resp = client.get(long_lived_url, params=long_lived_params)
                long_lived_data = resp.json()

                if "access_token" not in long_lived_data:
                    logger.error(f"Failed to get long-lived Facebook token: {long_lived_data}")
                    raise HTTPException(status_code=400, detail='Failed to get long-lived Facebook token')

                access_token = long_lived_data["access_token"]
                expires_in = long_lived_data.get("expires_in", 60 * 24 * 60 * 60)  # ~60 days

            fb_token = FacebookToken(
                access_token=access_token,
                expires_in=expires_in,
            )

            user_token = CreateUserToken(
                user_id=user_id,
                tokens=fb_token,
                platform=PlatformType.facebook,
            )

            return await self.create_user_token(user_token)

        except Exception as e:
            logger.error(f"Error upgrading to long-lived Facebook token: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to upgrade to long-lived Facebook token")

    async def refresh_facebook_token(self, db_token: UserTokenModel) -> Optional[UserTokenModel]:
        """
        Refresh a Facebook long-lived token before it expires.
        Should be called by a background job or on API error 190.
        """
        try:
            logger.info(f"Refreshing Facebook token for user_id={db_token.user_id}")
            refreshed_token = await self._upgrade_to_long_lived(db_token.access_token, db_token.user_id)
            return refreshed_token
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to refresh Facebook token for user_id={db_token.user_id}: {e}")
            raise e


    