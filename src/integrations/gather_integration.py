"""
Módulo para la integración con Gather.town
"""
import os
import logging
from typing import Dict, List, Optional
import requests
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()
GATHER_API_KEY = os.getenv("GATHER_API_KEY")
GATHER_API_BASE = "https://api.gather.town/api/v2"

# Template IDs para diferentes tipos de salas
TEMPLATES = {
    "tribunal_base": "1DemolM3y2NJZ5Wo\\first_court",  # Template básico de sala
    "audiencia": "1DemolM3y2NJZ5Wo\\first_court",     # Template para audiencias
    "mediacion": "1DemolM3y2NJZ5Wo\\first_court"      # Template para mediación
}

class GatherCourtIntegration:
    def __init__(self, api_key: Optional[str] = None):
        """Inicializar la integración con Gather"""
        self.api_key = api_key or GATHER_API_KEY
        if not self.api_key:
            raise ValueError("GATHER_API_KEY no está configurada")
        
        self.headers = {"apiKey": self.api_key}
        self.space_id = "1DemolM3y2NJZ5Wo"  # ID del espacio first_court
        self.space_name = "first_court"

    def get_court_info(self) -> Dict:
        """
        Obtener información sobre el espacio del tribunal
        
        Returns:
            Dict con la información del espacio
        """
        try:
            response = requests.get(
                f"{GATHER_API_BASE}/spaces/{self.space_id}",
                headers=self.headers
            )
            
            if response.status_code != 200:
                logger.error(f"Error de Gather API: {response.status_code}")
                logger.error(f"Respuesta: {response.text}")
                
            response.raise_for_status()
            
            space_data = response.json()
            logger.info(f"Información del espacio obtenida: {self.space_name}")
            return space_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener información del espacio en Gather: {e}")
            raise

    def configure_court_layout(
        self,
        space_id: str,
        map_id: str = "default",
        layout_config: Optional[Dict] = None
    ) -> Dict:
        """
        Configurar el layout de una sala de tribunal
        
        Args:
            space_id: ID del espacio
            map_id: ID del mapa (default por defecto)
            layout_config: Configuración personalizada del layout
            
        Returns:
            Dict con la configuración actualizada del mapa
        """
        try:
            # Obtener mapa actual
            response = requests.get(
                f"{GATHER_API_BASE}/spaces/{space_id}/maps/{map_id}",
                headers=self.headers
            )
            response.raise_for_status()
            current_map = response.json()
            
            # Configuración por defecto del tribunal
            default_layout = {
                "areas": [
                    {
                        "name": "Sala Principal",
                        "description": "Sala principal del tribunal",
                        "x": 0, "y": 0, "width": 20, "height": 15
                    },
                    {
                        "name": "Estrado del Juez",
                        "description": "Área reservada para el juez",
                        "x": 8, "y": 0, "width": 4, "height": 3
                    },
                    {
                        "name": "Mesa Fiscal",
                        "description": "Área para el fiscal",
                        "x": 2, "y": 4, "width": 3, "height": 2
                    },
                    {
                        "name": "Mesa Defensor",
                        "description": "Área para el defensor",
                        "x": 15, "y": 4, "width": 3, "height": 2
                    },
                    {
                        "name": "Secretaría",
                        "description": "Área de la secretaría del tribunal",
                        "x": 8, "y": 12, "width": 4, "height": 3
                    }
                ]
            }
            
            # Combinar con configuración personalizada si existe
            layout = layout_config or default_layout
            current_map.update(layout)
            
            # Actualizar mapa
            response = requests.post(
                f"{GATHER_API_BASE}/spaces/{space_id}/maps/{map_id}",
                json=current_map,
                headers=self.headers
            )
            response.raise_for_status()
            
            logger.info(f"Layout actualizado para espacio: {space_id}")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al configurar layout en Gather: {e}")
            raise

    def get_space_url(self, space_id: str) -> str:
        """Obtener URL para acceder al espacio"""
        return f"https://gather.town/app/{space_id}"
