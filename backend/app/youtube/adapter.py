import logging
from fastapi import HTTPException
from core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from db.models.user_tokens import UserTokenModel
from models.user_tokens import YoutubeTokenRequest
from user_tokens.adapter import UserTokenAdapter
import time
import asyncio


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
    
    
    async def init_process(self, youtube_token: YoutubeTokenRequest, user_id: int) -> dict:
        """
        Create a new YouTube project and wait until it is fully created.
        
        Returns:
            dict: The project info returned by Cloud Resource Manager.
        """
        try:
            user_tokens = await self.user_token_adapter.request_youtube_tokens(youtube_token, user_id)
            if not user_tokens:
                raise HTTPException(status_code=404, detail="YouTube tokens not found")
            # Start project creation
            operation_name = await self.__create_project(user_tokens)
            
            # Wait until creation is finished
            project_info = await self.__wait_for_project_creation(
                access_token=user_tokens.access_token, 
                operation_name=operation_name
            )
            
            project_name = project_info.get("name")  # e.g. "projects/1061145701774"
            project_number = project_name.split("/")[-1]

            api_operation_name = await self.__enable_youtube_data_api(user_tokens.access_token, project_number)
            await self.__wait_for_api_enablement(user_tokens.access_token, api_operation_name)

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

    async def __wait_for_api_enablement(self, access_token: str, operation_name: str, poll_interval: int = 2) -> dict:
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
    
    