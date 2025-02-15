"""
Endpoints para la gestión de videollamadas.
"""
from fastapi import APIRouter, HTTPException, Depends
from src.auth.auth_manager import get_current_user, get_google_credentials
from src.services.meetings import MeetingService
from src.monitoring.logger import Logger
from src.monitoring.metrics import meeting_metrics

router = APIRouter(prefix="/api/meetings", tags=["meetings"])
meeting_service = MeetingService()
logger = Logger(__name__)

@router.get("/create")
async def create_meeting(
    current_user = Depends(get_current_user),
    google_credentials = Depends(get_google_credentials)
):
    """Crear una nueva reunión de Meet."""
    try:
        with meeting_metrics.measure_latency("create_meeting_endpoint"):
            result = await meeting_service.create_meeting(google_credentials)
            return result
    except Exception as e:
        logger.error(f"Error creating meeting: {str(e)}")
        raise HTTPException(status_code=500, detail="MEETING_CREATION_FAILED")

@router.get("/{meeting_id}/state")
async def get_meeting_state(
    meeting_id: str,
    current_user = Depends(get_current_user),
    google_credentials = Depends(get_google_credentials)
):
    """Obtener estado de una reunión."""
    try:
        with meeting_metrics.measure_latency("get_meeting_state_endpoint"):
            result = await meeting_service.get_meeting_state(meeting_id, google_credentials)
            return result
    except Exception as e:
        logger.error(f"Error getting meeting state: {str(e)}")
        raise HTTPException(status_code=404, detail="MEETING_NOT_FOUND")
