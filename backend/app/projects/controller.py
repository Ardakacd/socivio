import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.projects import ProjectCreate, Project
from .service import ProjectsService, get_projects_service
from typing import Optional
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["projects"])
security = HTTPBearer()


@router.post("/", response_model=bool)
async def create_project(
    payload: ProjectCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    projects_service: ProjectsService = Depends(get_projects_service)
):
    try:
        token = credentials.credentials
        return await projects_service.create(payload, token)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"create_project: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create project")


@router.get("/{external_account_id}", response_model=Optional[Project])
async def get_project(
    external_account_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    projects_service: ProjectsService = Depends(get_projects_service)
):
    try:
        token = credentials.credentials
        return await projects_service.get_by_external_account_id(external_account_id, token)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_project: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch project")


