"""
Test de la integración con Gather.town
"""
import os
import logging
from dotenv import load_dotenv
from src.integrations.gather_integration import GatherCourtIntegration
from src.agents.gather_agents import (
    GatherJudgeAgent,
    GatherProsecutorAgent,
    GatherDefenderAgent,
    GatherSecretaryAgent
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

def test_court_integration():
    """Probar la integración con la sala de tribunal existente"""
    try:
        # Inicializar integración
        gather = GatherCourtIntegration()
        
        # Obtener información del espacio
        space_info = gather.get_court_info()
        logger.info(f"Información del espacio: {space_info}")
        
        # Configurar layout
        layout = gather.configure_court_layout(gather.space_id)
        logger.info(f"Layout configurado: {layout}")
        
        # Crear agentes
        judge = GatherJudgeAgent("Juez", gather, gather.space_id)
        prosecutor = GatherProsecutorAgent("Fiscal", gather, gather.space_id)
        defender = GatherDefenderAgent("Defensor", gather, gather.space_id)
        secretary = GatherSecretaryAgent("Secretario", gather, gather.space_id)
        
        # Programar una audiencia de prueba
        hearing_data = {
            "id": "TEST-2025-001",
            "type": "Primera Audiencia",
            "description": "Audiencia de prueba"
        }
        
        participants = [
            {"name": "Juez", "role": "judge"},
            {"name": "Fiscal", "role": "prosecutor"},
            {"name": "Defensor", "role": "defender"}
        ]
        
        secretary.schedule_hearing("Primera Audiencia", hearing_data, participants)
        
        # Obtener URL del espacio
        space_url = gather.get_space_url(gather.space_id)
        logger.info(f"URL del tribunal: {space_url}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error en la prueba: {e}")
        return False

if __name__ == "__main__":
    if test_court_integration():
        logger.info("✅ Prueba completada exitosamente")
    else:
        logger.error("❌ La prueba falló")
