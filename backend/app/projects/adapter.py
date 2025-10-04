from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from fastapi import HTTPException
from db.models.projects import ProjectModel
import logging
import uuid
from models.projects import Project
logger = logging.getLogger(__name__)


class ProjectsAdapter:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_or_create_project(self, external_account_id: str, user_id: int) -> ProjectModel:
        try:
            stmt = insert(ProjectModel).values(
                id=str(uuid.uuid4()),
                user_id=user_id,
                external_account_id=external_account_id,
            ).on_conflict_do_nothing(
                index_elements=["user_id", "external_account_id"]
            ).returning(ProjectModel)

            result = await self.db.execute(stmt)
            project = result.scalar_one_or_none()

            # If a new project wasn't created (conflict), fetch the existing one
            if not project:
                query = select(ProjectModel).where(
                    ProjectModel.user_id == user_id,
                    ProjectModel.external_account_id == external_account_id,
                )
                result = await self.db.execute(query)
                project = result.scalar_one()

            await self.db.commit()
            return project

        except Exception as e:
            await self.db.rollback()
            logger.error(f"get_or_create_project failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to get or create project")

    async def toggle_project_insight_activation(self, user_id: int, external_account_id: str, allow: bool) -> Project:
        try:
            query = select(ProjectModel).where(
                ProjectModel.user_id == user_id,
                ProjectModel.external_account_id == external_account_id,
            )
            result = await self.db.execute(query)
            project = result.scalar_one_or_none()
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            project.allow_insights = allow
            await self.db.commit()
            return Project(
                id=project.id,
                external_account_id=project.external_account_id,
                allow_insights=project.allow_insights,
                allow_ai_replies=project.allow_ai_replies,
            )
        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"toggle_project_insight_activation failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to toggle project insights")

    async def toggle_project_ai_replies_activation(self, user_id: int, external_account_id: str, allow: bool) -> Project:
        try:
            query = select(ProjectModel).where(
                ProjectModel.user_id == user_id,
                ProjectModel.external_account_id == external_account_id,
            )
            result = await self.db.execute(query)
            project = result.scalar_one_or_none()
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            project.allow_ai_replies = allow
            await self.db.commit()
            return Project(
                id=project.id,
                external_account_id=project.external_account_id,
                allow_insights=project.allow_insights,
                allow_ai_replies=project.allow_ai_replies,
            )
        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"toggle_project_ai_replies_activation failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to toggle project AI replies")


