"""Módulo para filtros avanzados de anotaciones."""
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class SortField(str, Enum):
    """Campos por los que se puede ordenar."""
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    PAGE = "page"
    POSITION = "position"

class SortOrder(str, Enum):
    """Orden de clasificación."""
    ASC = "asc"
    DESC = "desc"

@dataclass
class AnnotationFilter:
    """Filtro para búsqueda de anotaciones."""
    
    # Filtros de texto
    content_query: Optional[str] = None
    
    # Filtros de metadatos
    tags: Optional[List[str]] = None
    types: Optional[List[str]] = None
    users: Optional[List[str]] = None
    
    # Filtros de fecha
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None
    updated_before: Optional[datetime] = None
    
    # Filtros de posición
    page_range: Optional[tuple[int, int]] = None
    position_box: Optional[Dict[str, float]] = None  # {x1, y1, x2, y2}
    
    # Ordenamiento
    sort_by: SortField = SortField.CREATED_AT
    sort_order: SortOrder = SortOrder.DESC
    
    # Paginación
    limit: int = 50
    offset: int = 0

class AnnotationFilterEngine:
    """Motor de filtrado de anotaciones."""
    
    def __init__(self):
        self.text_analyzers = {
            'exact': self._exact_match,
            'contains': self._contains_match,
            'fuzzy': self._fuzzy_match
        }
    
    def _exact_match(self, text: str, query: str) -> bool:
        """Coincidencia exacta."""
        return text.lower() == query.lower()
    
    def _contains_match(self, text: str, query: str) -> bool:
        """Coincidencia parcial."""
        return query.lower() in text.lower()
    
    def _fuzzy_match(self, text: str, query: str, threshold: float = 0.8) -> bool:
        """Coincidencia aproximada usando distancia de Levenshtein."""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, text.lower(), query.lower()).ratio() >= threshold
    
    def _filter_by_text(
        self,
        annotations: List[Dict[str, Any]],
        query: str,
        match_type: str = 'contains'
    ) -> List[Dict[str, Any]]:
        """Filtrar por contenido de texto."""
        if not query:
            return annotations
            
        matcher = self.text_analyzers.get(match_type, self._contains_match)
        return [
            ann for ann in annotations
            if matcher(ann['content'], query)
        ]
    
    def _filter_by_metadata(
        self,
        annotations: List[Dict[str, Any]],
        tags: Optional[List[str]] = None,
        types: Optional[List[str]] = None,
        users: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Filtrar por metadatos."""
        filtered = annotations
        
        if tags:
            filtered = [
                ann for ann in filtered
                if any(tag in ann.get('tags', []) for tag in tags)
            ]
            
        if types:
            filtered = [
                ann for ann in filtered
                if ann.get('type') in types
            ]
            
        if users:
            filtered = [
                ann for ann in filtered
                if ann.get('user_id') in users
            ]
            
        return filtered
    
    def _filter_by_date(
        self,
        annotations: List[Dict[str, Any]],
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        updated_after: Optional[datetime] = None,
        updated_before: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Filtrar por fechas."""
        filtered = annotations
        
        if created_after:
            filtered = [
                ann for ann in filtered
                if ann['created_at'] >= created_after
            ]
            
        if created_before:
            filtered = [
                ann for ann in filtered
                if ann['created_at'] <= created_before
            ]
            
        if updated_after:
            filtered = [
                ann for ann in filtered
                if ann['updated_at'] >= updated_after
            ]
            
        if updated_before:
            filtered = [
                ann for ann in filtered
                if ann['updated_at'] <= updated_before
            ]
            
        return filtered
    
    def _filter_by_position(
        self,
        annotations: List[Dict[str, Any]],
        page_range: Optional[tuple[int, int]] = None,
        position_box: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """Filtrar por posición."""
        filtered = annotations
        
        if page_range:
            start, end = page_range
            filtered = [
                ann for ann in filtered
                if start <= ann['position']['page'] <= end
            ]
            
        if position_box:
            filtered = [
                ann for ann in filtered
                if (
                    position_box['x1'] <= ann['position']['x'] <= position_box['x2']
                    and position_box['y1'] <= ann['position']['y'] <= position_box['y2']
                )
            ]
            
        return filtered
    
    def _sort_annotations(
        self,
        annotations: List[Dict[str, Any]],
        sort_by: SortField,
        sort_order: SortOrder
    ) -> List[Dict[str, Any]]:
        """Ordenar anotaciones."""
        reverse = sort_order == SortOrder.DESC
        
        if sort_by == SortField.PAGE:
            key = lambda x: x['position']['page']
        elif sort_by == SortField.POSITION:
            key = lambda x: (x['position']['page'], x['position']['y'], x['position']['x'])
        else:
            key = lambda x: x[sort_by]
            
        return sorted(annotations, key=key, reverse=reverse)
    
    def apply_filter(
        self,
        annotations: List[Dict[str, Any]],
        filter_params: AnnotationFilter
    ) -> List[Dict[str, Any]]:
        """Aplicar filtros a las anotaciones.
        
        Args:
            annotations: Lista de anotaciones
            filter_params: Parámetros de filtrado
            
        Returns:
            Lista de anotaciones filtradas
        """
        # Aplicar filtros en secuencia
        filtered = annotations
        
        # Filtro de texto
        if filter_params.content_query:
            filtered = self._filter_by_text(
                filtered,
                filter_params.content_query
            )
        
        # Filtros de metadatos
        filtered = self._filter_by_metadata(
            filtered,
            filter_params.tags,
            filter_params.types,
            filter_params.users
        )
        
        # Filtros de fecha
        filtered = self._filter_by_date(
            filtered,
            filter_params.created_after,
            filter_params.created_before,
            filter_params.updated_after,
            filter_params.updated_before
        )
        
        # Filtros de posición
        filtered = self._filter_by_position(
            filtered,
            filter_params.page_range,
            filter_params.position_box
        )
        
        # Ordenar resultados
        filtered = self._sort_annotations(
            filtered,
            filter_params.sort_by,
            filter_params.sort_order
        )
        
        # Aplicar paginación
        start = filter_params.offset
        end = start + filter_params.limit
        return filtered[start:end]
