"""Módulo para gestión de plantillas de documentos."""
from typing import Dict, Any, Optional, List
from src.integrations.google_docs import GoogleDocsClient
from src.integrations.google_drive import GoogleDriveClient

class TemplateManager:
    """Gestor de plantillas de documentos."""
    
    TEMPLATE_TYPES = {
        'demanda': {
            'fields': ['tribunal', 'cliente', 'contraparte', 'materia', 'petitorio'],
            'type': 'documento_legal'
        },
        'poder': {
            'fields': ['mandante', 'mandatario', 'facultades'],
            'type': 'documento_legal'
        },
        'escrito_simple': {
            'fields': ['tribunal', 'causa', 'peticion'],
            'type': 'documento_legal'
        }
    }
    
    def __init__(self):
        """Inicializar el gestor de plantillas."""
        self.docs_client = GoogleDocsClient()
        self.drive_client = GoogleDriveClient()
        self.templates_folder = self._get_or_create_templates_folder()
    
    def _get_or_create_templates_folder(self) -> Dict[str, Any]:
        """Obtener o crear la carpeta de plantillas."""
        folder_name = "Plantillas"
        folders = self.drive_client.search_files(
            query=f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        )
        
        if folders:
            return folders[0]
        
        return self.drive_client.create_folder(folder_name)
    
    def create_template(self, template_type: str, title: str,
                       content: str) -> Dict[str, Any]:
        """Crear una nueva plantilla.
        
        Args:
            template_type: Tipo de plantilla (demanda, poder, etc)
            title: Título de la plantilla
            content: Contenido inicial de la plantilla
            
        Returns:
            Dict con la información del documento creado
        """
        if template_type not in self.TEMPLATE_TYPES:
            raise ValueError(f"Tipo de plantilla no válido: {template_type}")
        
        # Crear documento
        doc = self.docs_client.create_document(
            title=f"[Plantilla] {title}",
            metadata={
                'template_type': template_type,
                'fields': self.TEMPLATE_TYPES[template_type]['fields']
            }
        )
        
        # Mover a carpeta de plantillas
        self.drive_client.move_file(doc['id'], self.templates_folder['id'])
        
        # Insertar contenido
        if content:
            self.docs_client.insert_text(doc['id'], content)
        
        return doc
    
    def create_from_template(self, template_id: str,
                           variables: Dict[str, Any]) -> Dict[str, Any]:
        """Crear documento desde una plantilla.
        
        Args:
            template_id: ID de la plantilla
            variables: Variables para reemplazar en la plantilla
            
        Returns:
            Dict con la información del documento creado
        """
        # Obtener plantilla
        template = self.docs_client.get_document(template_id)
        
        # Crear documento desde plantilla
        doc = self.docs_client.create_document(
            title=f"{template['title'].replace('[Plantilla] ', '')}",
            template_id=template_id,
            metadata={'variables': variables}
        )
        
        # Reemplazar variables
        self.docs_client.replace_text(doc['id'], variables)
        
        return doc
    
    def list_templates(self, template_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Listar plantillas disponibles.
        
        Args:
            template_type: Opcional, filtrar por tipo de plantilla
            
        Returns:
            Lista de plantillas
        """
        query = f"'{self.templates_folder['id']}' in parents"
        if template_type:
            if template_type not in self.TEMPLATE_TYPES:
                raise ValueError(f"Tipo de plantilla no válido: {template_type}")
            query += f" and properties has {{ key='template_type' and value='{template_type}' }}"
        
        return self.drive_client.search_files(query=query)
