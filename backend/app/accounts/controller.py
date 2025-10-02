import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .service import AccountsService, get_accounts_service
from models.accounts import ConnectedAccounts

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/accounts", tags=["accounts"])
security = HTTPBearer()


@router.get("/connected", response_model=ConnectedAccounts)
async def get_connected_accounts(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        accounts_service: AccountsService = Depends(get_accounts_service)):
    """
    Returns connected Facebook pages, Instagram accounts, and YouTube channels.
    """
    logger.info(f"Getting connected accounts for user: {credentials.credentials}")
    try:
        token = credentials.credentials
        return await accounts_service.get_connected_accounts(token)
    except HTTPException as e:
        logger.error(f"HTTP error during get connected accounts: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during get connected accounts: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get connected accounts")


