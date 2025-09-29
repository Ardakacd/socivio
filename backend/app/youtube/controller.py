import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .service import YoutubeService, get_youtube_service
from models.user_tokens import YoutubeTokenRequest
from models.youtube import YoutubeReport, YoutubeReportRequest
# Configure logging 
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/youtube", tags=["youtube"])
security = HTTPBearer()


@router.post("/init-process", response_model=bool)
async def init_process(
        youtube_token_request: YoutubeTokenRequest, 
        credentials: HTTPAuthorizationCredentials = Depends(security),
        youtube_service: YoutubeService = Depends(get_youtube_service)):
    """
    Returns True if youtube project is created successfully, False otherwise.
    """
    logger.info(f"Creating youtube project for user: {credentials.credentials}")
    try:
        token = credentials.credentials
        
        return await youtube_service.init_process(youtube_token_request, token)

    except HTTPException as e:
        logger.error(f"HTTP error during create youtube project: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during create youtube project: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create youtube project")

@router.post("/report", response_model=YoutubeReport)
async def query_report(
        youtube_report_request: YoutubeReportRequest,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        youtube_service: YoutubeService = Depends(get_youtube_service)):
    """
    Returns youtube report.
    """
    logger.info(f"Creating youtube project for user: {credentials.credentials}")
    try:
        token = credentials.credentials
        
        return await youtube_service.query_report(youtube_report_request, token)

    except HTTPException as e:
        logger.error(f"HTTP error during query youtube report: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during query youtube report: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to query youtube report")

@router.post("/channels", response_model=YoutubeReport)
async def get_channels(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        youtube_service: YoutubeService = Depends(get_youtube_service)):
    """
    Returns youtube channels.
    """
    logger.info(f"Creating youtube project for user: {credentials.credentials}")
    try:
        token = credentials.credentials
        
        return await youtube_service.get_channels(token)

    except HTTPException as e:
        logger.error(f"HTTP error during get channels: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during get channels: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get channels")






