"""
Cliente personalizado para Deepseek API con manejo mejorado de instrucciones y contexto
"""
import requests
from typing import List, Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

class DeepseekClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.conversation_history: List[Dict[str, str]] = []
        
    def _get_system_prompt(self, role: str) -> str:
        """
        Obtiene un prompt de sistema detallado basado en el rol
        """
        base_instructions = """
        Instrucciones importantes:
        1. Mantén respuestas concisas y directas
        2. Evita repeticiones y loops de pensamiento
        3. Si no estás seguro de algo, indícalo claramente
        4. Sigue estrictamente el formato de respuesta requerido
        5. No generes información ficticia
        """
        
        role_prompts = {
            "juez": """
            Eres un juez del sistema judicial chileno con las siguientes responsabilidades:
            - Analizar casos basándote estrictamente en la ley y jurisprudencia chilena
            - Evaluar evidencia de manera imparcial y objetiva
            - Emitir resoluciones fundamentadas y claras
            - Garantizar el debido proceso
            """,
            "secretario": """
            Eres un secretario judicial chileno con las siguientes responsabilidades:
            - Revisar y validar documentación legal
            - Gestionar el flujo de casos y expedientes
            - Asegurar el cumplimiento de plazos y procedimientos
            - Mantener registros precisos
            """,
            "default": """
            Eres un asistente legal especializado en el sistema judicial chileno.
            Debes proporcionar información precisa y fundamentada en la legislación vigente.
            """
        }
        
        return base_instructions + role_prompts.get(role.lower(), role_prompts["default"])

    def generate(self, 
                prompt: str, 
                role: str = "default", 
                temperature: float = 0.1,
                max_tokens: int = 2000,
                context: Optional[str] = None) -> str:
        """
        Genera una respuesta usando el modelo Deepseek con manejo mejorado
        
        Args:
            prompt: El prompt principal
            role: Rol específico para las instrucciones del sistema
            temperature: Control de creatividad (0.0 - 1.0)
            max_tokens: Máximo de tokens en la respuesta
            context: Contexto adicional opcional
        """
        system_prompt = self._get_system_prompt(role)
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Agregar contexto si existe
        if context:
            messages.append({"role": "system", "content": f"Contexto adicional: {context}"})
        
        # Agregar historial de conversación relevante
        messages.extend(self.conversation_history[-5:])  # Últimas 5 interacciones
        
        # Agregar el prompt actual
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": 0.95,
            "frequency_penalty": 0.5,  # Aumentado para reducir repeticiones
            "presence_penalty": 0.5,   # Aumentado para mejorar variedad
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                generated_text = result["choices"][0]["message"]["content"].strip()
                
                # Detectar posibles loops o respuestas repetitivas
                if self._detect_repetition(generated_text):
                    logger.warning("Detectada posible respuesta repetitiva")
                    # Reiniciar contexto y reintentar con temperatura más baja
                    self.conversation_history = []
                    return self.generate(prompt, role, max(0.0, temperature - 0.05))
                
                # Actualizar historial
                self.conversation_history.append({
                    "role": "user",
                    "content": prompt
                })
                self.conversation_history.append({
                    "role": "assistant",
                    "content": generated_text
                })
                
                return generated_text
            else:
                raise Exception("No se encontró texto en la respuesta")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en la llamada a Deepseek API: {str(e)}")
            raise Exception(f"Error en la llamada a Deepseek API: {str(e)}")
        except KeyError as e:
            logger.error(f"Error en el formato de respuesta: {str(e)}")
            raise Exception(f"Error en el formato de respuesta de Deepseek API: {str(e)}")
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            raise Exception(f"Error inesperado: {str(e)}")

    def _detect_repetition(self, text: str) -> bool:
        """
        Detecta patrones repetitivos en la respuesta
        """
        # Verificar últimas respuestas por similitud
        if len(self.conversation_history) >= 2:
            last_response = self.conversation_history[-1].get("content", "")
            similarity = self._calculate_similarity(text, last_response)
            if similarity > 0.8:  # 80% similar
                return True
        
        # Detectar frases repetidas dentro del texto
        sentences = text.split(". ")
        unique_sentences = set(sentences)
        if len(sentences) > len(unique_sentences) * 1.3:  # Más del 30% repetido
            return True
            
        return False
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calcula similitud simple entre dos textos
        """
        # Implementación básica de similitud por coincidencia de palabras
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)

    def reset_conversation(self):
        """
        Reinicia el historial de conversación
        """
        self.conversation_history = []
