"""
Endpoints para sincronización offline.
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, List
from src.auth.auth_manager import get_current_user
from src.services.sync import SyncService
from src.monitoring.logger import Logger
from src.monitoring.metrics import sync_metrics

router = APIRouter(prefix="/api", tags=["sync"])
sync_service = SyncService()
logger = Logger(__name__)

@router.post("/sync")
async def sync_operations(
    operations: List[Dict] = Body(...),
    last_sync: str = Body(...),
    device_id: str = Body(...),
    current_user = Depends(get_current_user)
):
    """Sincronizar operaciones pendientes.
    
    Args:
        operations: Lista de operaciones pendientes
        last_sync: Timestamp de última sincronización
        device_id: ID del dispositivo
    """
    try:
        with sync_metrics.measure_latency("sync_endpoint"):
            result = await sync_service.sync(
                operations=operations,
                last_sync=last_sync,
                device_id=device_id
            )
            return result
            
    except Exception as e:
        logger.error(f"Error in sync: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="SYNC_ERROR"
        )
