from turtle import ht
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import select
import logging
from fastapi import HTTPException
from db.models.user_tokens import UserTokenModel, PlatformType
from models.user_tokens import YoutubeTokenRequest, YoutubeToken, CreateUserToken
from core.config import settings
import httpx
from datetime import datetime, timedelta

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
            expires_at = datetime.utcnow() + timedelta(seconds=user_token.tokens.expires_in)

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
                return None

            return tokens

        except SQLAlchemyError as e:
            logger.error(f"UserTokenAdapter: Database error fetching tokens for user_id={user_id}, platform={platform}: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"UserTokenAdapter: Unexpected error fetching tokens for user_id={user_id}, platform={platform}: {e}", exc_info=True)
            return None

    