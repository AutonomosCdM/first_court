"""
Motor de templates para el sistema judicial
"""
from typing import Dict, Any
from pathlib import Path
from datetime import datetime
import re
from jinja2 import Environment, FileSystemLoader, select_autoescape

class TemplateEngine:
    """Motor de templates para el sistema judicial"""
    
    def __init__(self):
        """Inicializa el motor de templates"""
        template_dir = Path(__file__).parent / 'templates'
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Registrar filtros personalizados
        self.env.filters['format_date'] = self.format_date
        self.env.filters['format_time'] = self.format_time
        self.env.filters['format_datetime'] = self.format_datetime
    
    def render_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """
        Renderiza un template con los datos proporcionados
        
        Args:
            template_name: Nombre del template (sin extensión)
            data: Diccionario con los datos para el template
            
        Returns:
            String con el HTML renderizado
        """
        template = self.env.get_template(f"{template_name}.html")
        
        # Preparar datos comunes
        common_data = {
            "current_year": datetime.now().year,
            "system_name": "Sistema Judicial",
            "support_email": "soporte@autonomos.dev"
        }
        
        # Combinar datos comunes con los específicos
        render_data = {**common_data, **data}
        
        return template.render(**render_data)
    
    @staticmethod
    def format_date(value: str) -> str:
        """Formatea una fecha ISO a formato legible"""
        if not value:
            return ""
        try:
            date = datetime.fromisoformat(value)
            return date.strftime("%d de %B de %Y")
        except:
            return value
    
    @staticmethod
    def format_time(value: str) -> str:
        """Formatea una hora ISO a formato legible"""
        if not value:
            return ""
        try:
            time = datetime.fromisoformat(value)
            return time.strftime("%H:%M hrs")
        except:
            return value
    
    @staticmethod
    def format_datetime(value: str) -> str:
        """Formatea una fecha y hora ISO a formato legible"""
        if not value:
            return ""
        try:
            dt = datetime.fromisoformat(value)
            return dt.strftime("%d de %B de %Y a las %H:%M hrs")
        except:
            return value
    
    def prepare_hearing_data(self, case_data: Dict, hearing_data: Dict) -> Dict:
        """
        Prepara los datos para un template de audiencia
        
        Args:
            case_data: Datos del caso
            hearing_data: Datos de la audiencia
            
        Returns:
            Dict con los datos procesados para el template
        """
        # Extraer fecha y hora
        hearing_datetime = datetime.fromisoformat(hearing_data.get('datetime', ''))
        
        return {
            "case_id": case_data.get('id'),
            "case_type": case_data.get('tipo'),
            "case_matter": case_data.get('materia'),
            "hearing_type": hearing_data.get('title'),
            "hearing_date": self.format_date(hearing_data.get('datetime')),
            "hearing_time": self.format_time(hearing_data.get('datetime')),
            "duration": hearing_data.get('duration', 60),
            "is_virtual": hearing_data.get('virtual', True),
            "meet_link": hearing_data.get('meet_link'),
            "participants": [
                {
                    "name": p.get('nombre'),
                    "role": p.get('rol'),
                    "email": p.get('email')
                }
                for p in case_data.get('participantes', [])
            ],
            "calendar_link": self._generate_calendar_link(hearing_data)
        }
    
    def _generate_calendar_link(self, hearing_data: Dict) -> str:
        """
        Genera un enlace para agregar el evento al calendario
        
        Args:
            hearing_data: Datos de la audiencia
            
        Returns:
            String con el enlace de Google Calendar
        """
        # Implementar generación de enlace de calendario
        # Por ahora retornamos un placeholder
        return "#"
