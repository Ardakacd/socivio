from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from db.models.projects import ProjectModel
import logging

logger = logging.getLogger(__name__)


class ProjectsAdapter:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_project(self, account_id: str, user_id: int, external_account_id: str) -> bool:
        try:
            project = ProjectModel(id=account_id, user_id=user_id, external_account_id=external_account_id)
            self.db.add(project)
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"ProjectsAdapter.create_project: {e}")
            raise HTTPException(status_code=500, detail="Failed to create project")

    async def get_by_external_account_id(self, user_id: int, external_account_id: str) -> Optional[ProjectModel]:
        try:
            stmt = select(ProjectModel).where(
                ProjectModel.external_account_id == external_account_id,
                ProjectModel.user_id == user_id,
            )
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to fetch project: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch project")


