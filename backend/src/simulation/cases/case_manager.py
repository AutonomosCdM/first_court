"""
Sistema de gestión de casos para simulaciones
"""
from typing import Dict, List, Optional
from enum import Enum
import json
from pathlib import Path

class CaseType(Enum):
    CONTROL_DETENCION = "control_detencion"
    FORMALIZACION = "formalizacion"
    JUICIO_ORAL = "juicio_oral"
    PROCEDIMIENTO_ABREVIADO = "procedimiento_abreviado"
    JUICIO_SIMPLIFICADO = "juicio_simplificado"

class CaseComplexity(Enum):
    BASIC = "basic"          # Conceptos fundamentales
    INTERMEDIATE = "inter"   # Múltiples delitos/participantes
    ADVANCED = "advanced"    # Casos complejos, doctrina dividida

class CaseManager:
    """
    Gestiona los casos disponibles para simulaciones, incluyendo:
    - Carga y validación de casos
    - Selección basada en nivel y objetivos
    - Generación de variantes
    """
    
    def __init__(self, cases_directory: str = "case_templates"):
        self.cases_directory = Path(cases_directory)
        self.cases: Dict[str, Dict] = {}
        self.load_cases()
        
    def load_cases(self):
        """
        Carga los casos desde los archivos de template
        """
        for case_file in self.cases_directory.glob("*.json"):
            with open(case_file, 'r', encoding='utf-8') as f:
                case_data = json.load(f)
                if self._validate_case_data(case_data):
                    self.cases[case_data["id"]] = case_data
    
    def get_case(self, case_id: str) -> Dict:
        """
        Obtiene un caso específico
        """
        if case_id not in self.cases:
            raise ValueError(f"Caso {case_id} no encontrado")
        return self.cases[case_id]
    
    def find_suitable_cases(self,
                           semester: int,
                           case_type: Optional[CaseType] = None,
                           complexity: Optional[CaseComplexity] = None) -> List[Dict]:
        """
        Encuentra casos apropiados según criterios
        """
        suitable_cases = []
        
        for case in self.cases.values():
            if self._case_matches_criteria(case, semester, case_type, complexity):
                suitable_cases.append(case)
                
        return suitable_cases
    
    def create_case_variant(self, base_case_id: str) -> Dict:
        """
        Crea una variante de un caso base
        """
        base_case = self.get_case(base_case_id)
        
        # Crear una variante modificando elementos no esenciales
        variant = base_case.copy()
        variant["id"] = f"{base_case_id}_variant_{len(self.cases)}"
        
        # Modificar elementos para crear variación
        self._modify_case_details(variant)
        
        # Guardar la variante
        self.cases[variant["id"]] = variant
        
        return variant
    
    def _validate_case_data(self, case_data: Dict) -> bool:
        """
        Valida que el caso tenga toda la información necesaria
        """
        required_fields = [
            "id", "type", "complexity", "min_semester",
            "facts", "evidence", "legal_basis", "expected_arguments"
        ]
        
        return all(field in case_data for field in required_fields)
    
    def _case_matches_criteria(self,
                             case: Dict,
                             semester: int,
                             case_type: Optional[CaseType],
                             complexity: Optional[CaseComplexity]) -> bool:
        """
        Verifica si un caso cumple con los criterios de búsqueda
        """
        if semester < case["min_semester"]:
            return False
            
        if case_type and case["type"] != case_type.value:
            return False
            
        if complexity and case["complexity"] != complexity.value:
            return False
            
        return True
    
    def _modify_case_details(self, case: Dict):
        """
        Modifica detalles no esenciales del caso para crear variantes
        """
        # Modificar nombres, fechas, lugares manteniendo la estructura legal
        if "personas" in case:
            case["personas"] = self._modify_personas(case["personas"])
            
        if "lugares" in case:
            case["lugares"] = self._modify_lugares(case["lugares"])
            
        if "fechas" in case:
            case["fechas"] = self._modify_fechas(case["fechas"])
    
    def _modify_personas(self, personas: List[Dict]) -> List[Dict]:
        """
        Modifica datos de personas manteniendo roles
        """
        nombres_imputados = [
            "Pedro Soto", "Carlos Ruiz", "Luis Morales", "Roberto Silva",
            "Miguel Ángel", "José Pérez", "Diego Muñoz"
        ]
        nombres_victimas = [
            "Ana Torres", "Carmen Rojas", "Patricia Vega", "Laura Flores",
            "Sofía Castro", "Isabel Pinto", "Carolina Díaz"
        ]
        
        modified_personas = []
        for persona in personas:
            modified_persona = persona.copy()
            if persona["rol"] == "imputado":
                modified_persona["nombre"] = nombres_imputados.pop()
            elif persona["rol"] == "víctima":
                modified_persona["nombre"] = nombres_victimas.pop()
            modified_personas.append(modified_persona)
            
        return modified_personas
    
    def _modify_lugares(self, lugares: List[Dict]) -> List[Dict]:
        """
        Modifica lugares manteniendo contexto
        """
        calles = [
            "Avenida Libertad", "Calle República", "Pasaje Los Robles",
            "Avenida Alemania", "Calle Picarte", "Avenida Francia"
        ]
        comisarias = [
            "Primera Comisaría", "Segunda Comisaría", "Tercera Comisaría",
            "Subcomisaria Los Robles", "Tenencia Central"
        ]
        
        modified_lugares = []
        for lugar in lugares:
            modified_lugar = lugar.copy()
            if lugar["tipo"] == "lugar_hechos":
                modified_lugar["nombre"] = f"{calles.pop()} {100 + len(calles)}"
            elif lugar["tipo"] == "lugar_detencion":
                modified_lugar["nombre"] = comisarias.pop()
            modified_lugares.append(modified_lugar)
            
        return modified_lugares
    
    def _modify_fechas(self, fechas: Dict) -> Dict:
        """
        Modifica fechas manteniendo relaciones temporales
        """
        from datetime import datetime, timedelta
        import random
        
        # Convertir fechas a datetime
        fecha_base = datetime.strptime(fechas["hecho"], "%Y-%m-%dT%H:%M:%S")
        
        # Generar nueva fecha base (entre 1 y 30 días antes o después)
        delta_dias = random.randint(-30, 30)
        nueva_fecha_base = fecha_base + timedelta(days=delta_dias)
        
        # Mantener las diferencias temporales entre eventos
        modified_fechas = {}
        for key, value in fechas.items():
            fecha_original = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
            diferencia = fecha_original - fecha_base
            modified_fechas[key] = (nueva_fecha_base + diferencia).strftime("%Y-%m-%dT%H:%M:%S")
            
        return modified_fechas
