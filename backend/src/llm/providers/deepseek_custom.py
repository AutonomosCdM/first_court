"""
Cliente personalizado para Deepseek API
"""
import requests
from typing import List, Dict, Any
import json

class DeepseekClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def generate(self, prompt: str) -> str:
        """
        Genera una respuesta usando el modelo Deepseek
        """
        endpoint = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"Error en la llamada a Deepseek API: {str(e)}")
