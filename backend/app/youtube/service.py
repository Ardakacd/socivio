import logging
from fastapi import  HTTPException
from .adapter import YoutubeAdapter
from utils.jwt import get_user_id_from_token
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_async_db
from fastapi import Depends
from models.user_tokens import YoutubeTokenRequest
from models.youtube import YoutubeReportRequest, YoutubeReport, YoutubeChannels
# Configure logging
logger = logging.getLogger(__name__)

class YoutubeService:
    def __init__(self, youtube_adapter: YoutubeAdapter):
        self.youtube_adapter = youtube_adapter

    async def init_process(
        self,
        youtube_token: YoutubeTokenRequest,
        token: str) -> bool:
        """
        Returns True if youtube tokens are requested successfully, False otherwise.
        """
        
        try:
            user_id = get_user_id_from_token(token)
            
            return await self.youtube_adapter.init_process(youtube_token, user_id)

        except HTTPException as e:
            logger.error(f"HTTP error during request youtube tokens: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during request youtube tokens: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to request youtube tokens")

    async def query_report(
        self,
        youtube_report_request: YoutubeReportRequest,
        token: str
    ) -> YoutubeReport:
        try:

            user_id = get_user_id_from_token(token)
            return await self.youtube_adapter.query_report(youtube_report_request, user_id)
        except HTTPException as e:
            logger.error(f"HTTP error during query report: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during query report: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to query report")


    async def get_channels(self, token: str) -> YoutubeChannels:
        try:
            user_id = get_user_id_from_token(token)
            return await self.youtube_adapter.get_channels(user_id)
        except HTTPException as e:
            logger.error(f"HTTP error during get channels: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during get channels: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to get channels")


   
def get_youtube_service(db: AsyncSession = Depends(get_async_db)) -> YoutubeService:
    youtube_adapter = YoutubeAdapter(db)
    return YoutubeService(youtube_adapter)
