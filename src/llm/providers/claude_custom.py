"""
Cliente personalizado para Anthropic Claude API
"""
from anthropic import Anthropic
from typing import List, Dict, Any
import json
import os
import logging
import sys

logger = logging.getLogger(__name__)

class ClaudeClient:
    """
    Cliente para interactuar con Claude API
    """
    def __init__(self, api_key: str):
        # Eliminar cualquier espacio en blanco o saltos de línea
        api_key = api_key.strip().replace('\n', '').replace('\r', '')
        
        # Imprimir información detallada de depuración
        print(f"API Key recibida (longitud: {len(api_key)}): {api_key}")
        print(f"Primeros 10 caracteres: {api_key[:10]}")
        print(f"Últimos 10 caracteres: {api_key[-10:]}")
        
        # Verificar si la API key tiene el prefijo correcto
        if not api_key.startswith('sk-ant-'):
            print(f"ADVERTENCIA: La API key no comienza con 'sk-ant-'. Prefijo actual: {api_key[:7]}")
        
        logger.info(f"Inicializando ClaudeClient con API key: {api_key[:10]}...")
        try:
            self.client = Anthropic(api_key=api_key)
            self.model = "claude-3-opus-20240229"  # El modelo más potente de Claude
        except Exception as e:
            logger.error(f"Error al inicializar Anthropic client: {e}")
            print(f"Error de inicialización: {e}", file=sys.stderr)
            raise
        
    def generate(self, prompt: str) -> str:
        """
        Genera una respuesta usando el modelo Claude
        """
        try:
            logger.info(f"Generando respuesta con modelo: {self.model}")
            system_prompt = "Eres un asistente judicial experto. Debes responder siempre en formato JSON válido."
            
            logger.debug(f"Prompt del sistema: {system_prompt}")
            logger.debug(f"Prompt del usuario: {prompt}")
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.3,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"{prompt}\n\nIMPORTANTE: Tu respuesta debe ser un objeto JSON válido, sin ningún texto adicional antes o después."
                    }
                ]
            )
            
            response_text = message.content[0].text
            logger.info(f"Respuesta recibida. Longitud: {len(response_text)} caracteres")
            
            return response_text
                
        except Exception as e:
            logger.error(f"Error en la llamada a Claude API: {type(e).__name__} - {str(e)}")
            print(f"Error de llamada a API: {type(e).__name__} - {str(e)}", file=sys.stderr)
            raise Exception(f"Error en la llamada a Claude API: {type(e).__name__} - {str(e)}")
