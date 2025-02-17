"""
Gestor principal del sistema de simulación de audiencias
"""
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
import json

class SimulationLevel(Enum):
    BASIC = "basic"          # Semestres 1-4
    INTERMEDIATE = "inter"   # Semestres 5-6
    ADVANCED = "advanced"    # Semestres 7-10

class ParticipantRole(Enum):
    JUDGE = "judge"
    PROSECUTOR = "prosecutor"
    DEFENDER = "defender"
    SECRETARY = "secretary"
    STUDENT = "student"

class SimulationManager:
    """
    Gestiona las simulaciones de audiencias, incluyendo:
    - Configuración de participantes
    - Control de flujo de la audiencia
    - Gestión de interacciones
    - Evaluación y retroalimentación
    """
    
    def __init__(self):
        self.active_simulations: Dict[str, Dict] = {}
        self.simulation_history: List[Dict] = []
        
    def create_simulation(self, 
                         case_id: str,
                         level: SimulationLevel,
                         student_data: Dict,
                         student_role: ParticipantRole) -> str:
        """
        Crea una nueva simulación
        """
        simulation_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{case_id}"
        
        self.active_simulations[simulation_id] = {
            "case_id": case_id,
            "level": level,
            "student_data": student_data,
            "student_role": student_role,
            "start_time": datetime.now(),
            "status": "initialized",
            "interactions": [],
            "metrics": {
                "legal_accuracy": 0.0,
                "procedural_compliance": 0.0,
                "communication_skills": 0.0,
                "time_management": 0.0
            }
        }
        
        return simulation_id
    
    def start_simulation(self, simulation_id: str) -> Dict:
        """
        Inicia una simulación existente
        """
        if simulation_id not in self.active_simulations:
            raise ValueError(f"Simulación {simulation_id} no encontrada")
            
        simulation = self.active_simulations[simulation_id]
        simulation["status"] = "in_progress"
        simulation["current_phase"] = "opening"
        
        return {
            "simulation_id": simulation_id,
            "start_time": datetime.now(),
            "initial_state": simulation
        }
    
    def record_interaction(self, 
                          simulation_id: str,
                          participant: ParticipantRole,
                          content: str,
                          interaction_type: str) -> Dict:
        """
        Registra una interacción en la simulación
        """
        if simulation_id not in self.active_simulations:
            raise ValueError(f"Simulación {simulation_id} no encontrada")
            
        interaction = {
            "timestamp": datetime.now(),
            "participant": participant,
            "content": content,
            "type": interaction_type
        }
        
        self.active_simulations[simulation_id]["interactions"].append(interaction)
        
        return interaction
    
    def end_simulation(self, simulation_id: str) -> Dict:
        """
        Finaliza una simulación y genera reporte
        """
        if simulation_id not in self.active_simulations:
            raise ValueError(f"Simulación {simulation_id} no encontrada")
            
        simulation = self.active_simulations[simulation_id]
        simulation["status"] = "completed"
        simulation["end_time"] = datetime.now()
        
        # Generar reporte final
        report = self._generate_final_report(simulation)
        
        # Mover a historial
        self.simulation_history.append(simulation)
        del self.active_simulations[simulation_id]
        
        return report
    
    def _generate_final_report(self, simulation: Dict) -> Dict:
        """
        Genera el reporte final de la simulación
        """
        return {
            "case_id": simulation["case_id"],
            "level": simulation["level"],
            "duration": str(simulation["end_time"] - simulation["start_time"]),
            "metrics": simulation["metrics"],
            "interactions_count": len(simulation["interactions"]),
            "student_role": simulation["student_role"],
            "recommendations": self._generate_recommendations(simulation)
        }
    
    def _generate_recommendations(self, simulation: Dict) -> List[Dict]:
        """
        Genera recomendaciones basadas en el desempeño
        """
        recommendations = []
        metrics = simulation["metrics"]
        
        # Ejemplo de recomendaciones basadas en métricas
        if metrics["legal_accuracy"] < 0.7:
            recommendations.append({
                "area": "Precisión Legal",
                "suggestion": "Reforzar conocimiento de normativa aplicable",
                "resources": ["Unidad 3 - Marco Legal", "Práctica de Casos Similares"]
            })
            
        if metrics["procedural_compliance"] < 0.7:
            recommendations.append({
                "area": "Cumplimiento Procesal",
                "suggestion": "Mejorar conocimiento de procedimientos",
                "resources": ["Manual de Procedimiento Penal", "Simulaciones Básicas"]
            })
            
        return recommendations
