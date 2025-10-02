import logging
from typing import Optional
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_async_db
from .adapter import ProjectsAdapter
from models.projects import ProjectCreate, Project
from utils.jwt import get_user_id_from_token
import uuid
logger = logging.getLogger(__name__)


class ProjectsService:
    def __init__(self, projects_adapter: ProjectsAdapter):
        self.projects_adapter = projects_adapter

    async def create(self, payload: ProjectCreate, token: str) -> bool:
        try:
            
            user_id = get_user_id_from_token(token)
            account_id = str(uuid.uuid4())
            print(account_id, user_id, payload.external_account_id)
            return await self.projects_adapter.create_project(account_id, user_id, payload.external_account_id)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"ProjectsService.create: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to create project")

    async def get_by_external_account_id(self, external_account_id: str, token: str) -> Optional[Project]:
        try:
            user_id = get_user_id_from_token(token)
            row = await self.projects_adapter.get_by_external_account_id(user_id, external_account_id)
            if not row:
                return None
            return Project(id=row.id, external_account_id=row.external_account_id, user_id=row.user_id)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"ProjectsService.get_by_external_account_id: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to fetch project")


def get_projects_service(db: AsyncSession = Depends(get_async_db)) -> ProjectsService:
    return ProjectsService(ProjectsAdapter(db))


