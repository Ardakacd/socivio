import logging
from typing import Optional
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_async_db
from .adapter import ProjectsAdapter
from models.projects import ToggleProjectFlag, Project
from utils.jwt import get_user_id_from_token
import uuid
logger = logging.getLogger(__name__)


class ProjectsService:
    def __init__(self, projects_adapter: ProjectsAdapter):
        self.projects_adapter = projects_adapter

    async def get_or_create_project(self, external_account_id: str, token: str) -> bool:
        try:
            
            user_id = get_user_id_from_token(token)
            
            return await self.projects_adapter.get_or_create_project(external_account_id, user_id)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"ProjectsService.get_or_create_project: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to create project")

    async def toggle_project_insight_activation(self, token: str, payload: ToggleProjectFlag) -> Project:
        try:
            user_id = get_user_id_from_token(token)
            return await self.projects_adapter.toggle_project_insight_activation(user_id, payload.external_account_id, payload.allow)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"ProjectsService.toggle_project_insight_activation: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to toggle project insights")

    async def toggle_project_ai_replies_activation(self, token: str, payload: ToggleProjectFlag) -> Project:
        try:
            user_id = get_user_id_from_token(token)
            return await self.projects_adapter.toggle_project_ai_replies_activation(user_id, payload.external_account_id, payload.allow)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"ProjectsService.toggle_project_ai_replies_activation: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to toggle project AI replies")


def get_projects_service(db: AsyncSession = Depends(get_async_db)) -> ProjectsService:
    return ProjectsService(ProjectsAdapter(db))


