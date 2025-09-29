import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .service import UserTokenService, get_user_tokens_service

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user-tokens", tags=["user-tokens"])
security = HTTPBearer()


@router.delete("/delete", response_model=bool)
async def delete_users_all_tokens(credentials: HTTPAuthorizationCredentials = Depends(security), user_service: UserTokenService = Depends(get_user_tokens_service)):
    """
    Delete users all tokens.
    
    Returns True if successful, False if failed.
    """
    logger.info(f"Delete users all tokens attempt")
    try:
        token = credentials.credentials
        result = await user_service.delete_users_all_tokens(token)
        logger.info(f"Delete users all tokens successful")
        return result

    except HTTPException as e:
        logger.error(f"HTTP error during delete users all tokens: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during delete users all tokens: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


