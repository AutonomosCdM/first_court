from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any
from app.models.user import UserPreferences
from app.services.user_service import UserService
from app.core.auth import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/preferences")
async def get_preferences(
    current_user = Depends(get_current_user)
) -> UserPreferences:
    try:
        preferences = await UserService.get_preferences(current_user)
        return preferences
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/preferences")
async def update_preferences(
    preferences: UserPreferences,
    current_user = Depends(get_current_user)
) -> UserPreferences:
    try:
        updated_preferences = await UserService.update_preferences(current_user, preferences)
        return updated_preferences
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sync")
async def sync_data(
    data: Dict[str, Any],
    current_user = Depends(get_current_user)
) -> JSONResponse:
    try:
        await UserService.sync_data(current_user, data)
        return JSONResponse(content={"status": "success"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
