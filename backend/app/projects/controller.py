import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.projects import Project, ToggleProjectFlag
from .service import ProjectsService, get_projects_service
from typing import Optional
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["projects"])
security = HTTPBearer()



@router.get("/{external_account_id}", response_model=Optional[Project])
async def get_or_create_project(
    external_account_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    projects_service: ProjectsService = Depends(get_projects_service)
):
    try:
        token = credentials.credentials
        return await projects_service.get_or_create_project(external_account_id, token)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_project: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch project")


@router.post("/toggle-insights", response_model=Project)
async def toggle_project_insight_activation(
    payload: ToggleProjectFlag,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    projects_service: ProjectsService = Depends(get_projects_service)
):
    try:
        token = credentials.credentials
        return await projects_service.toggle_project_insight_activation(token, payload)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"toggle_project_insight_activation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to toggle project insights")


@router.post("/toggle-ai-replies", response_model=Project)
async def toggle_project_ai_replies_activation(
    payload: ToggleProjectFlag,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    projects_service: ProjectsService = Depends(get_projects_service)
):
    try:
        token = credentials.credentials
        return await projects_service.toggle_project_ai_replies_activation(token, payload)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"toggle_project_ai_replies_activation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to toggle project AI replies")

