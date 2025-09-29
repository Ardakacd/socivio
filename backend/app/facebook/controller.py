import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .service import FacebookService, get_facebook_service
from models.user_tokens import FacebookTokenRequest
from models.facebook import UserFacebookPages, PageInsightRequest
# Configure logging 
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/facebook", tags=["facebook"])
security = HTTPBearer()


@router.post("/init-process", response_model=bool)
async def init_process(
        facebook_token_request: FacebookTokenRequest, 
        credentials: HTTPAuthorizationCredentials = Depends(security),
        facebook_service: FacebookService = Depends(get_facebook_service)):
    """
    Returns True if facebook project is created successfully, False otherwise.
    """
    logger.info(f"Creating facebook project for user: {credentials.credentials}")
    try:
        token = credentials.credentials
        
        return await facebook_service.init_process(facebook_token_request, token)

    except HTTPException as e:
        logger.error(f"HTTP error during create facebook project: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during create facebook project: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create facebook project")

@router.get("/get-user-pages", response_model=UserFacebookPages)
async def get_user_pages(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        facebook_service: FacebookService = Depends(get_facebook_service)):
    """
    Returns list of user pages.
    """
    logger.info(f"Getting user pages for user: {credentials.credentials}")
    try:
        token = credentials.credentials
        
        return await facebook_service.get_user_pages(token)

    except HTTPException as e:
        logger.error(f"HTTP error during getting user pages: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during getting user pages: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to getting user pages")


@router.post("/page-insights", response_model=list[dict])
async def get_page_insights(
        page_insight_request: PageInsightRequest,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        facebook_service: FacebookService = Depends(get_facebook_service)):
    """
    Returns list of page insights.
    """
    logger.info(f"Getting page insights for user: {credentials.credentials}")
    try:
        token = credentials.credentials
        
        return await facebook_service.get_page_insights(page_insight_request, token)

    except HTTPException as e:
        logger.error(f"HTTP error during getting page insights: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during getting page insights: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to getting page insights")


@router.get("/get-instagram-accounts", response_model=list[dict])
async def get_instagram_accounts(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        facebook_service: FacebookService = Depends(get_facebook_service)):
    """
    Returns list of instagram accounts.
    """
    logger.info(f"Getting instagram accounts for user: {credentials.credentials}")
    try:
        token = credentials.credentials
        
        return await facebook_service.get_instagram_accounts(token)

    except HTTPException as e:
        logger.error(f"HTTP error during getting instagram accounts: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during getting instagram accounts: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to getting instagram accounts")







