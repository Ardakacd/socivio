import logging
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from db.models.user_tokens import UserTokenModel, PlatformType
from models.user_tokens import YoutubeTokenRequest
from user_tokens.adapter import UserTokenAdapter
import time
import asyncio
from models.youtube import YoutubeReportRequest, YoutubeReport


logger = logging.getLogger(__name__)


class YoutubeAdapter:
    """
    Youtube adapter for youtube operations.
    
    This adapter provides async interface for youtube operations
    with proper error handling and session management.
    """

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.user_token_adapter = UserTokenAdapter(self.db_session)
    
    
    async def init_process(self, youtube_token: YoutubeTokenRequest, user_id: int) -> bool:
        """
        Create a new YouTube project and wait until it is fully created.
        
        Returns:
            dict: The project info returned by Cloud Resource Manager.
        """
        try:
            user_tokens = await self.user_token_adapter.request_youtube_tokens(youtube_token, user_id)
            if not user_tokens:
                raise HTTPException(status_code=404, detail="YouTube tokens not found")
            #operation_name = await self.__create_project(user_tokens)
            
            # Wait until creation is finished
            #project_info = await self.__wait_for_project_creation(
            #    access_token=user_tokens.access_token, 
            #    operation_name=operation_name
            #)
            
            #project_name = 
            #if not project_name:
            #    raise HTTPException(status_code=500, detail="No project name returned")
            # project_number = project_name.split("/")[-1]

            #api_operation_name = await self.__enable_youtube_data_api(user_tokens.access_token, project_number)
            #analytics_operation_name = await self.__enable_youtube_analytics_api(user_tokens.access_token, project_number)
           # await self.__wait_for_youtube_data_api_enablement(user_tokens.access_token, api_operation_name)
           # await self.__wait_for_youtube_analytics_api_enablement(user_tokens.access_token, analytics_operation_name)

            return True

        except HTTPException as e:
            logger.error(f"HTTP error while creating project for user_id={user_id}: {e.detail}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error while creating project for user_id={user_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to create project")

    async def __create_project(self, user_tokens: UserTokenModel) -> str:
        """
        Start a new YouTube project creation.
        Returns the operation name to track progress.
        """
        

        access_token = user_tokens.access_token 
        project_id = f"socivio-project-{int(time.time())}"

        url_create = "https://cloudresourcemanager.googleapis.com/v3/projects"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "projectId": project_id,
            "displayName": "Socivio Project"
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(url_create, headers=headers, json=payload)
            if resp.status_code >= 400:
                logger.error(f"Project creation failed: {resp.text}")
                raise HTTPException(status_code=resp.status_code, detail=resp.text)

            op_data = resp.json()
            operation_name = op_data.get("name")
            if not operation_name:
                logger.error(f"No operation returned for project creation: {op_data}")
                raise HTTPException(status_code=500, detail="No operation returned")
            
            logger.info(f"Project creation started: operation={operation_name}")
            return operation_name

    async def __wait_for_project_creation(self, access_token: str, operation_name: str, poll_interval: int = 2) -> dict:
        """
        Poll the project creation operation until done.
        Returns the project response on success.
        """
        url_op = f"https://cloudresourcemanager.googleapis.com/v3/{operation_name}"
        headers = {"Authorization": f"Bearer {access_token}"}

        async with httpx.AsyncClient() as client:
            while True:
                resp = await client.get(url_op, headers=headers)
                op_json = resp.json()

                if op_json.get("done"):
                    if "error" in op_json:
                        logger.error(f"Project creation error: {op_json['error']}")
                        raise HTTPException(status_code=500, detail=str(op_json["error"]))
                    logger.info(f"Project created successfully: {op_json.get('response')}")
                    return op_json.get("response")

                logger.info("Waiting for project creation to finish...")
                await asyncio.sleep(poll_interval)

    async def __enable_youtube_data_api(self, access_token: str, project_number: str) -> str:
        """
        Enable YouTube Data API v3 for a given Google Cloud project.

        Args:
            access_token (str): OAuth2 access token with sufficient permissions.
            project_id (str): ID of the project to enable the API for.

        Returns:
            str: Operation name for tracking the enablement progress.
        """
        try:
            url = f"https://serviceusage.googleapis.com/v1/projects/{project_number}/services/youtube.googleapis.com:enable"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json={})

                if response.status_code >= 400:
                    logger.error(f"Failed to enable YouTube Data API: {response.text}")
                    raise HTTPException(status_code=response.status_code, detail=response.text)

                operation_data = response.json()
                operation_name = operation_data.get("name")
                if not operation_name:
                    logger.error(f"No operation returned for API enablement: {operation_data}")
                    raise HTTPException(status_code=500, detail="No operation returned for API enablement")

                logger.info(f"YouTube Data API enablement started: operation={operation_name}")
                return operation_name

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error enabling YouTube Data API for project {project_number}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to enable YouTube Data API")

    async def __wait_for_youtube_data_api_enablement(self, access_token: str, operation_name: str, poll_interval: int = 2) -> dict:
        """
        Poll the enable API operation until done.
        Returns the operation response on success.

        Args:
            access_token (str): OAuth2 access token with sufficient permissions.
            operation_name (str): Name of the enable API operation returned by Service Usage API.
            poll_interval (int): Seconds to wait between polling attempts.

        Returns:
            dict: Operation response if the API is enabled successfully.

        Raises:
            HTTPException: If the operation fails or an unexpected error occurs.
        """
        url_op = f"https://serviceusage.googleapis.com/v1/{operation_name}"
        headers = {"Authorization": f"Bearer {access_token}"}

        async with httpx.AsyncClient() as client:
            while True:
                resp = await client.get(url_op, headers=headers)
                op_json = resp.json()

                if op_json.get("done"):
                    if "error" in op_json:
                        logger.error(f"Enable API operation error: {op_json['error']}")
                        raise HTTPException(status_code=500, detail=str(op_json["error"]))
                    logger.info(f"YouTube Data API enabled successfully: {op_json.get('response')}")
                    return op_json.get("response", op_json)

                logger.info("Waiting for YouTube Data API enable operation to finish...")
                await asyncio.sleep(poll_interval)

    async def __enable_youtube_analytics_api(self, access_token: str, project_number: str) -> str:
        """
        Enable YouTube Analytics API for a given Google Cloud project.

        Args:
            access_token (str): OAuth2 access token with sufficient permissions.
            project_number (str): Number of the project to enable the API for.

        Returns:
            str: Operation name for tracking the enablement progress.
        """
        try:
            url = f"https://serviceusage.googleapis.com/v1/projects/{project_number}/services/youtubeanalytics.googleapis.com:enable"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json={})

                if response.status_code >= 400:
                    logger.error(f"Failed to enable YouTube Analytics API: {response.text}")
                    raise HTTPException(status_code=response.status_code, detail=response.text)

                operation_data = response.json()
                operation_name = operation_data.get("name")
                if not operation_name:
                    logger.error(f"No operation returned for API enablement: {operation_data}")
                    raise HTTPException(status_code=500, detail="No operation returned for API enablement")

                logger.info(f"YouTube Analytics API enablement started: operation={operation_name}")
                return operation_name

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error enabling YouTube Analytics API for project {project_number}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to enable YouTube Analytics API")

    async def __wait_for_youtube_analytics_api_enablement(self, access_token: str, operation_name: str, poll_interval: int = 2) -> dict:
        """
        Poll the enable API operation until done.
        Returns the operation response on success.
        """
        url_op = f"https://serviceusage.googleapis.com/v1/{operation_name}"
        headers = {"Authorization": f"Bearer {access_token}"}

        async with httpx.AsyncClient() as client:
            while True:
                resp = await client.get(url_op, headers=headers)
                op_json = resp.json()

                if op_json.get("done"):
                    if "error" in op_json:
                        logger.error(f"Enable API operation error: {op_json['error']}")
                        raise HTTPException(status_code=500, detail=str(op_json["error"]))
                    logger.info(f"YouTube Analytics API enabled successfully: {op_json.get('response')}")
                    return op_json.get("response", op_json)

                logger.info("Waiting for YouTube Analytics API enable operation to finish...")
                await asyncio.sleep(poll_interval)

    async def query_report(
        self,
        youtube_report_request: YoutubeReportRequest,    
        user_id: int,
    ) -> YoutubeReport:
        """
        Query the YouTube Analytics API for a report.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics: Comma-separated metrics (e.g., "views,likes")
            dimensions: Comma-separated dimensions (e.g., "day,country")
            filters: Filter expression (e.g., "country==US")
            ids: The channel or content owner to retrieve data for (default: "channel==MINE")

        Returns:
            JSON response from YouTube Analytics API, or None if failed
        """
        try:
            user_tokens = await self.user_token_adapter.get_tokens_by_user_id(user_id, PlatformType.youtube)
            if not user_tokens:
                raise HTTPException(status_code=404, detail="YouTube tokens not found")
            
            
            

            YOUTUBE_ANALYTICS_BASE_URL = "https://youtubeanalytics.googleapis.com/v2/reports"

            params = {
                "ids": youtube_report_request.ids,
                "startDate": youtube_report_request.start_date,
                "endDate": youtube_report_request.end_date,
                "metrics": youtube_report_request.metrics,
            }

            if youtube_report_request.dimensions:
                params["dimensions"] = youtube_report_request.dimensions
            if youtube_report_request.filters:
                params["filters"] = youtube_report_request.filters

            headers = {
                "Authorization": f"Bearer {user_tokens.access_token}",
                "Accept": "application/json"
            }

            logger.info(f"YouTubeAnalyticsAdapter: Querying report {params}")
            async with httpx.AsyncClient() as client:
                resp = await client.get(YOUTUBE_ANALYTICS_BASE_URL, params=params, headers=headers)
                if resp.status_code != 200:
                    error_msg = resp.text
                    logger.error(f"YouTubeAnalyticsAdapter: API request failed ({resp.status_code}): {error_msg}")
                    raise HTTPException(status_code=resp.status_code, detail=error_msg)
                data = resp.json()
                
                
                logger.info("YouTubeAnalyticsAdapter: Report retrieved successfully")
                return YoutubeReport(report=data.get('rows', []), ids=youtube_report_request.ids)
        except HTTPException as e:
            logger.error(f"HTTP error during query report: {e.detail}")
            raise e
        except Exception as e:
            logger.error(f"YouTubeAnalyticsAdapter: Unexpected error {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to query report")

    