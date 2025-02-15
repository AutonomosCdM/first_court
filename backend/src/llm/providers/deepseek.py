from langchain.chat_models import ChatOpenAI
from typing import Dict, Any
from config.judicial_settings import JudicialSettings

class DeepseekLegalLLM:
    def __init__(self, settings: JudicialSettings):
        self.client = ChatOpenAI(
            model_name="deepseek-law-v1",
            temperature=0.3,
            max_tokens=2048
        )
        
    def generate_legal_analysis(self, prompt: str) -> str:
        """Genera análisis legal usando el modelo Deepseek"""
        return self.client.predict(prompt)
        
    def generate_document(self, template: str, context: Dict[str, Any]) -> str:
        """Genera documentos legales basados en plantillas"""
        prompt = f"Basado en la siguiente plantilla:\n{template}\n\nContexto:\n{context}\n\nGenera el documento:"
        return self.client.predict(prompt)
