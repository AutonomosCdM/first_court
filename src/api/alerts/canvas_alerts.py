from typing import Dict, List
import asyncio
from datetime import datetime, timedelta
from ..services.notification_service import NotificationService

class CanvasAlerts:
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service
        self.latency_threshold = 2.0  # segundos
        self.connection_threshold = 100  # conexiones por caso
        self.error_threshold = 10  # errores por minuto

    async def check_api_latency(self, latency: float, endpoint: str):
        """Alerta si la latencia supera el umbral"""
        if latency > self.latency_threshold:
            await self.notification_service.send_alert(
                title="Alta Latencia en Canvas API",
                message=f"Endpoint {endpoint} está experimentando latencia de {latency}s",
                severity="warning"
            )

    async def check_ws_connections(self, case_id: str, connections: int):
        """Alerta si hay demasiadas conexiones en un caso"""
        if connections > self.connection_threshold:
            await self.notification_service.send_alert(
                title="Exceso de Conexiones WebSocket",
                message=f"Caso {case_id} tiene {connections} conexiones activas",
                severity="warning"
            )

    async def check_error_rate(self, errors: int, window: int = 60):
        """Alerta si hay demasiados errores por minuto"""
        if errors > self.error_threshold:
            await self.notification_service.send_alert(
                title="Alta Tasa de Errores en Canvas",
                message=f"Se detectaron {errors} errores en los últimos {window} segundos",
                severity="error"
            )

    async def monitor_canvas_health(self):
        """Monitor continuo de la salud del sistema"""
        while True:
            try:
                # Aquí irían las verificaciones periódicas
                await asyncio.sleep(60)
            except Exception as e:
                await self.notification_service.send_alert(
                    title="Error en Monitoreo de Canvas",
                    message=str(e),
                    severity="error"
                )
