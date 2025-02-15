"""Módulo para gestión de carpetas y documentos de casos."""
from typing import Dict, Any, List, Optional
from src.integrations.google_drive import GoogleDriveClient

class CaseManager:
    """Gestor de estructura de carpetas y documentos de casos."""
    
    FOLDER_STRUCTURE = {
        'documentos_principales': {},
        'escritos': {},
        'pruebas': {
            'documentales': {},
            'testimoniales': {},
            'periciales': {}
        },
        'resoluciones': {},
        'comunicaciones': {},
        'otros': {}
    }
    
    DOCUMENT_TYPES = {
        'demanda': 'documentos_principales',
        'contestacion': 'documentos_principales',
        'escrito': 'escritos',
        'prueba_documental': 'pruebas/documentales',
        'prueba_testimonial': 'pruebas/testimoniales',
        'informe_pericial': 'pruebas/periciales',
        'resolucion': 'resoluciones',
        'oficio': 'comunicaciones',
        'otro': 'otros'
    }
    
    def __init__(self):
        """Inicializar el gestor de casos."""
        self.drive_client = GoogleDriveClient()
        self.cases_folder = self._get_or_create_cases_folder()
    
    def _get_or_create_cases_folder(self) -> Dict[str, Any]:
        """Obtener o crear la carpeta principal de casos."""
        folder_name = "Casos"
        folders = self.drive_client.search_files(
            query=f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        )
        
        if folders:
            return folders[0]
        
        return self.drive_client.create_folder(folder_name)
    
    def create_case_structure(self, case_id: str, title: str) -> Dict[str, Any]:
        """Crear estructura de carpetas para un nuevo caso.
        
        Args:
            case_id: Identificador único del caso
            title: Título del caso
            
        Returns:
            Dict con información de la carpeta raíz del caso
        """
        # Crear carpeta raíz del caso
        case_folder = self.drive_client.create_folder(
            name=f"{case_id} - {title}",
            parent_id=self.cases_folder['id']
        )
        
        # Crear estructura de subcarpetas
        self._create_folder_structure(case_folder['id'], self.FOLDER_STRUCTURE)
        
        return case_folder
    
    def _create_folder_structure(self, parent_id: str, structure: Dict[str, Any], path: str = "") -> None:
        """Crear estructura recursiva de carpetas."""
        for name, subfolders in structure.items():
            folder = self.drive_client.create_folder(
                name=name.replace('_', ' ').title(),
                parent_id=parent_id
            )
            if subfolders:
                new_path = f"{path}/{name}" if path else name
                self._create_folder_structure(folder['id'], subfolders, new_path)
    
    def classify_document(self, file_id: str, doc_type: str) -> Dict[str, Any]:
        """Clasificar y mover un documento a la carpeta correspondiente.
        
        Args:
            file_id: ID del archivo a clasificar
            doc_type: Tipo de documento (según DOCUMENT_TYPES)
            
        Returns:
            Dict con información del archivo movido
        """
        if doc_type not in self.DOCUMENT_TYPES:
            raise ValueError(f"Tipo de documento no válido: {doc_type}")
        
        # Obtener carpeta destino
        target_path = self.DOCUMENT_TYPES[doc_type]
        return self.move_to_folder(file_id, target_path)
    
    def move_to_folder(self, file_id: str, target_path: str) -> Dict[str, Any]:
        """Mover un archivo a una carpeta específica dentro del caso.
        
        Args:
            file_id: ID del archivo a mover
            target_path: Ruta relativa de la carpeta destino (e.g. 'pruebas/documentales')
            
        Returns:
            Dict con información del archivo movido
        """
        # Buscar carpeta destino
        path_parts = target_path.split('/')
        current_folder = self.cases_folder['id']
        
        for part in path_parts:
            folders = self.drive_client.search_files(
                query=f"name = '{part}' and '{current_folder}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
            )
            if not folders:
                raise ValueError(f"Carpeta no encontrada: {part}")
            current_folder = folders[0]['id']
        
        # Mover archivo
        return self.drive_client.move_file(file_id, current_folder)
    
    def get_case_structure(self, case_id: str) -> Dict[str, Any]:
        """Obtener estructura completa de carpetas y archivos de un caso.
        
        Args:
            case_id: Identificador del caso
            
        Returns:
            Dict con la estructura completa del caso
        """
        # Buscar carpeta raíz del caso
        case_folders = self.drive_client.search_files(
            query=f"name contains '{case_id}' and mimeType = 'application/vnd.google-apps.folder' and '{self.cases_folder['id']}' in parents and trashed = false"
        )
        
        if not case_folders:
            raise ValueError(f"Caso no encontrado: {case_id}")
        
        return self._get_folder_structure(case_folders[0]['id'])
    
    def _get_folder_structure(self, folder_id: str) -> Dict[str, Any]:
        """Obtener estructura recursiva de una carpeta."""
        # Obtener información de la carpeta
        folder = self.drive_client.service.files().get(
            fileId=folder_id,
            fields='id, name, mimeType'
        ).execute()
        
        # Obtener contenido
        children = self.drive_client.search_files(
            query=f"'{folder_id}' in parents and trashed = false"
        )
        
        result = {
            'id': folder['id'],
            'name': folder['name'],
            'type': 'folder',
            'children': []
        }
        
        # Procesar contenido
        for child in children:
            if child['mimeType'] == 'application/vnd.google-apps.folder':
                result['children'].append(
                    self._get_folder_structure(child['id'])
                )
            else:
                result['children'].append({
                    'id': child['id'],
                    'name': child['name'],
                    'type': 'file',
                    'webViewLink': child.get('webViewLink')
                })
        
        return result
