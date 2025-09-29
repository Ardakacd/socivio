import logging
from .adapter import UserTokenAdapter
from db.database import get_async_db
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from utils.jwt import get_user_id_from_token

logger = logging.getLogger(__name__)

class UserTokenService:
    def __init__(self, user_tokens_adapter: UserTokenAdapter):
        self.user_tokens_adapter = user_tokens_adapter

    async def delete_users_all_tokens(self, token: str) -> bool:
        try:
            user_id = get_user_id_from_token(token)

            # Delete user tokens using internal ID
            return await self.user_tokens_adapter.delete_users_all_tokens(user_id)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server error"
            )


def get_user_tokens_service(
        db: AsyncSession = Depends(get_async_db),
) -> UserTokenService:
    user_tokens_adapter = UserTokenAdapter(db)
    return UserTokenService(user_tokens_adapter)
