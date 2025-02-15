"""
Endpoints para gestionar preferencias de usuario.
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict
from src.auth.auth_manager import get_current_user
from src.services.preferences import PreferencesService
from src.monitoring.logger import Logger
from src.monitoring.metrics import preferences_metrics

router = APIRouter(prefix="/api/users", tags=["preferences"])
preferences_service = PreferencesService()
logger = Logger(__name__)

@router.get("/preferences")
async def get_preferences(current_user = Depends(get_current_user)):
    """Obtener preferencias del usuario actual."""
    try:
        with preferences_metrics.measure_latency("get_preferences_endpoint"):
            preferences = await preferences_service.get_preferences(
                current_user.id
            )
            return preferences
            
    except Exception as e:
        logger.error(f"Error getting preferences: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="PREFERENCES_ERROR"
        )

@router.put("/preferences")
async def sync_preferences(
    request: Dict = Body(...),
    current_user = Depends(get_current_user)
):
    """Sincronizar preferencias del usuario."""
    try:
        with preferences_metrics.measure_latency("sync_preferences_endpoint"):
            if not request.get('deviceId'):
                raise HTTPException(
                    status_code=400,
                    detail="DEVICE_ID_REQUIRED"
                )
                
            result = await preferences_service.sync_preferences(
                user_id=current_user.id,
                request=request,
                device_id=request['deviceId']
            )
            return result
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing preferences: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="SYNC_ERROR"
        )
