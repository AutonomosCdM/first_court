"""
Cliente personalizado para Groq API
"""
from groq import Groq
from typing import List, Dict, Any
import json

class GroqClient:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
    
    def generate(self, prompt: str) -> str:
        """
        Genera una respuesta usando el modelo Groq
        """
        try:
            chat_completion = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {
                        "role": "system", 
                        "content": "Eres un juez del sistema judicial chileno. Debes analizar casos y proporcionar evaluaciones precisas y fundamentadas en la ley."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=4000,
                top_p=0.95,
                response_format={"type": "json_object"}
            )
            
            # Devolver el contenido directamente
            return chat_completion.choices[0].message.content
                
        except Exception as e:
            raise Exception(f"Error en la llamada a Groq API: {str(e)}")
