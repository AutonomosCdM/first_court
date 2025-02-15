"""
Agente de Documentación basado en DeepSeek-Coder-V2-Instruct.
Maneja la generación y análisis de documentos legales.
"""
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from src.custom.agents.base import BaseAgent
from src.monitoring.logger import Logger
from src.integrations.google_docs import GoogleDocsClient

logger = Logger(__name__)

class DocumentationAgent(BaseAgent):
    """Agente especializado en documentación usando DeepSeek-Coder-V2-Instruct."""
    
    def __init__(self):
        """Inicializar agente de documentación."""
        super().__init__(
            name="docs",
            model="DeepSeek-Coder-V2-Instruct-21B",
            temperature=0.3
        )
        self.docs_client = GoogleDocsClient()
        
    async def process_document(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Procesar documento legal.
        
        Args:
            content: Contenido del documento
            context: Contexto adicional (tipo de documento, caso, etc.)
            
        Returns:
            Análisis y sugerencias
        """
        prompt = self._build_document_prompt(content, context)
        response = await self.generate(prompt)
        
        return self._parse_document_response(response)
    
    async def generate_document(self, template: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generar documento legal desde plantilla.
        
        Args:
            template: ID o nombre de la plantilla
            params: Parámetros para la generación
            
        Returns:
            Documento generado y metadata
        """
        prompt = self._build_generation_prompt(template, params)
        response = await self.generate(prompt)
        
        document = self._parse_generation_response(response)
        
        # Crear documento en Google Docs
        doc = self.docs_client.create_document(
            title=document['title'],
            content=document['content']
        )
        
        return {
            'document_id': doc['documentId'],
            'title': document['title'],
            'analysis': document['analysis']
        }
    
    async def analyze_changes(self, document_id: str, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analizar cambios en un documento.
        
        Args:
            document_id: ID del documento
            changes: Lista de cambios detectados
            
        Returns:
            Análisis de los cambios
        """
        doc = self.docs_client.get_document(document_id)
        prompt = self._build_changes_prompt(doc, changes)
        response = await self.generate(prompt)
        
        return self._parse_changes_response(response)
    
    async def suggest_improvements(self, document_id: str) -> Dict[str, Any]:
        """Sugerir mejoras para un documento.
        
        Args:
            document_id: ID del documento
            
        Returns:
            Lista de sugerencias
        """
        doc = self.docs_client.get_document(document_id)
        prompt = self._build_suggestions_prompt(doc)
        response = await self.generate(prompt)
        
        return self._parse_suggestions_response(response)
    
    def _build_document_prompt(self, content: str, context: Dict[str, Any]) -> str:
        """Construir prompt para análisis de documento."""
        return f"""Analiza el siguiente documento legal:

Tipo: {context.get('type', 'N/A')}
Caso: {context.get('case_id', 'N/A')}

Contenido:
{content}

Genera un análisis detallado incluyendo:
1. Resumen ejecutivo
2. Puntos clave
3. Posibles problemas o riesgos
4. Sugerencias de mejora
5. Referencias legales relevantes"""
    
    def _build_generation_prompt(self, template: str, params: Dict[str, Any]) -> str:
        """Construir prompt para generación de documento."""
        return f"""Genera un documento legal usando la siguiente plantilla y parámetros:

Plantilla: {template}

Parámetros:
{json.dumps(params, indent=2)}

El documento debe seguir el formato estándar y considerar:
1. Estructura clara y profesional
2. Lenguaje legal apropiado
3. Referencias y citas necesarias
4. Formato consistente"""
    
    def _build_changes_prompt(self, doc: Dict[str, Any], changes: List[Dict[str, Any]]) -> str:
        """Construir prompt para análisis de cambios."""
        changes_text = "\n".join(
            f"- {change['type']}: {change.get('content', '')}"
            for change in changes
        )
        
        return f"""Analiza los siguientes cambios en el documento:

Documento: {doc['title']}

Cambios detectados:
{changes_text}

Proporciona:
1. Impacto de los cambios
2. Posibles implicaciones legales
3. Recomendaciones
4. Necesidad de revisiones adicionales"""
    
    def _build_suggestions_prompt(self, doc: Dict[str, Any]) -> str:
        """Construir prompt para sugerencias."""
        return f"""Revisa el siguiente documento y sugiere mejoras:

Título: {doc['title']}

Contenido:
{doc.get('body', {}).get('content', '')}

Considera:
1. Claridad y precisión legal
2. Estructura y organización
3. Cumplimiento normativo
4. Protección legal
5. Mejoras de redacción"""
    
    def _parse_document_response(self, response: str) -> Dict[str, Any]:
        """Parsear respuesta de análisis de documento."""
        # TODO: Implementar parsing más robusto
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'analysis': response
        }
    
    def _parse_generation_response(self, response: str) -> Dict[str, Any]:
        """Parsear respuesta de generación de documento."""
        # TODO: Implementar parsing más robusto
        return {
            'title': 'Documento Legal',  # Extraer del response
            'content': response,
            'analysis': {}
        }
    
    def _parse_changes_response(self, response: str) -> Dict[str, Any]:
        """Parsear respuesta de análisis de cambios."""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'analysis': response
        }
    
    def _parse_suggestions_response(self, response: str) -> Dict[str, Any]:
        """Parsear respuesta de sugerencias."""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'suggestions': response
        }
