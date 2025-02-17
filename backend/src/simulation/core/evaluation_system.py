"""
Sistema de evaluación para simulaciones de audiencias
"""
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
import re

class EvaluationCriteria(Enum):
    LEGAL_KNOWLEDGE = "legal_knowledge"
    ARGUMENTATION = "argumentation"
    PROCEDURE = "procedure"
    COMMUNICATION = "communication"
    TIME_MANAGEMENT = "time_management"

class EvaluationSystem:
    """
    Sistema de evaluación que analiza el desempeño en tiempo real
    y genera retroalimentación detallada.
    """
    
    def __init__(self):
        # Criterios base para todos los roles
        self.base_criteria = {
            EvaluationCriteria.LEGAL_KNOWLEDGE: {
                "weight": 0.25,
                "metrics": ["citation_accuracy", "law_application"]
            },
            EvaluationCriteria.ARGUMENTATION: {
                "weight": 0.25,
                "metrics": ["logic_structure", "evidence_use"]
            },
            EvaluationCriteria.PROCEDURE: {
                "weight": 0.20,
                "metrics": ["protocol_compliance", "formalities"]
            },
            EvaluationCriteria.COMMUNICATION: {
                "weight": 0.15,
                "metrics": ["clarity", "persuasion"]
            },
            EvaluationCriteria.TIME_MANAGEMENT: {
                "weight": 0.15,
                "metrics": ["timing", "efficiency"]
            }
        }
        
        # Criterios específicos para el juez
        self.judge_criteria = {
            EvaluationCriteria.LEGAL_KNOWLEDGE: {
                "weight": 0.30,
                "metrics": ["citation_accuracy", "law_application"]
            },
            EvaluationCriteria.ARGUMENTATION: {
                "weight": 0.30,
                "metrics": ["logic_structure", "evidence_use"]
            },
            EvaluationCriteria.PROCEDURE: {
                "weight": 0.20,
                "metrics": ["protocol_compliance", "formalities"]
            },
            EvaluationCriteria.COMMUNICATION: {
                "weight": 0.10,
                "metrics": ["clarity", "persuasion"]
            },
            EvaluationCriteria.TIME_MANAGEMENT: {
                "weight": 0.10,
                "metrics": ["timing", "efficiency"]
            }
        }
        
        # Criterios específicos para el secretario
        self.secretary_criteria = {
            EvaluationCriteria.LEGAL_KNOWLEDGE: {
                "weight": 0.20,
                "metrics": ["citation_accuracy", "law_application"]
            },
            EvaluationCriteria.ARGUMENTATION: {
                "weight": 0.10,
                "metrics": ["logic_structure", "evidence_use"]
            },
            EvaluationCriteria.PROCEDURE: {
                "weight": 0.30,
                "metrics": ["protocol_compliance", "formalities"]
            },
            EvaluationCriteria.COMMUNICATION: {
                "weight": 0.20,
                "metrics": ["clarity", "persuasion"]
            },
            EvaluationCriteria.TIME_MANAGEMENT: {
                "weight": 0.20,
                "metrics": ["timing", "efficiency"]
            }
        }
        
        # Inicializar con criterios base
        self.evaluation_criteria = self.base_criteria
        self.evaluation_metrics = {
            "hearing_direction": "Dirección de la audiencia",
            "process_control": "Control del proceso",
            "guarantees_compliance": "Cumplimiento de garantías",
            "resolution_structure": "Estructura de la resolución"
        }
        self.communication_metrics = {
            "clarity_and_precision": "Claridad y precisión",
            "authority_exercise": "Ejercicio de autoridad",
            "impartiality": "Imparcialidad"
        }
        
        self.time_management_metrics = {
            "hearing_pace": "Ritmo de la audiencia",
            "deliberation_time": "Tiempo de deliberación",
            "resolution_timing": "Oportunidad de la resolución"
        }
        # Por defecto usamos los criterios base
        self.evaluation_criteria = self.base_criteria
    
    def evaluate_interaction(self, content: str, context: Dict, interaction_type: str) -> Dict:
        # Seleccionar criterios según el rol
        speaker_role = context.get("speaker_role", "default")
        
        if speaker_role == "judge":
            self.evaluation_criteria = self.judge_criteria
            return self._evaluate_judge_resolution(content, context)
        elif speaker_role == "secretary":
            self.evaluation_criteria = self.secretary_criteria
            return self._evaluate_secretary_certification(content, context)
        else:
            self.evaluation_criteria = self.base_criteria
            return self._evaluate_base_interaction(content, context, interaction_type)

    def _evaluate_judge_resolution(self, content: str, context: Dict) -> Dict:
        """Evalúa una resolución judicial"""
        scores = {}
        
        # Evaluación de Conocimiento Legal
        legal_score = self._evaluate_judge_legal_knowledge(content)
        scores[EvaluationCriteria.LEGAL_KNOWLEDGE.value] = {
            "score": legal_score,
            "weight": self.judge_criteria[EvaluationCriteria.LEGAL_KNOWLEDGE]["weight"],
            "feedback": self._get_legal_feedback(legal_score)
        }
        
        # Evaluación de Argumentación
        arg_score = self._evaluate_judge_argumentation(content)
        scores[EvaluationCriteria.ARGUMENTATION.value] = {
            "score": arg_score,
            "weight": self.judge_criteria[EvaluationCriteria.ARGUMENTATION]["weight"],
            "feedback": self._get_argumentation_feedback(arg_score)
        }
        
        # Evaluación de Procedimiento
        proc_score = self._evaluate_judge_procedure(content)
        scores[EvaluationCriteria.PROCEDURE.value] = {
            "score": proc_score,
            "weight": self.judge_criteria[EvaluationCriteria.PROCEDURE]["weight"],
            "feedback": self._get_procedure_feedback(proc_score)
        }
        
        # Evaluación de Comunicación
        comm_score = self._evaluate_judge_communication(content)
        scores[EvaluationCriteria.COMMUNICATION.value] = {
            "score": comm_score,
            "weight": self.judge_criteria[EvaluationCriteria.COMMUNICATION]["weight"],
            "feedback": self._get_communication_feedback(comm_score)
        }
        
        # Evaluación de Gestión del Tiempo
        time_score = self._evaluate_judge_time_management(content, context)
        scores[EvaluationCriteria.TIME_MANAGEMENT.value] = {
            "score": time_score,
            "weight": self.judge_criteria[EvaluationCriteria.TIME_MANAGEMENT]["weight"],
            "feedback": self._get_time_feedback(time_score)
        }
        
        # Cálculo de puntaje general
        overall_score = sum(s["score"] * s["weight"] for s in scores.values())
        
        return {
            "timestamp": datetime.now(),
            "overall_score": overall_score,
            "criteria_scores": scores,
            "immediate_feedback": self._generate_judge_feedback(scores)
        }
    def _evaluate_judge_legal_knowledge(self, content: str) -> float:
        """Evalúa el conocimiento legal en una resolución judicial"""
        score = 0.0
        
        # Análisis normativo
        if re.search(r'artículo[s]?\s+\d+', content, re.IGNORECASE):
            score += 0.25
        
        # Interpretación jurisprudencial
        if re.search(r'jurisprudencia|corte suprema|corte de apelaciones', content, re.IGNORECASE):
            score += 0.25
        
        # Fundamentación legal
        if re.search(r'considerando|fundamento|por estas consideraciones', content, re.IGNORECASE):
            score += 0.25
        
        # Garantías constitucionales
        if re.search(r'garantía|derecho|constitucional', content, re.IGNORECASE):
            score += 0.25
        
        return score
    
    def _evaluate_judge_argumentation(self, content: str) -> float:
        """Evalúa la argumentación en una resolución judicial"""
        score = 0.0
        
        # Razonamiento judicial
        if re.search(r'PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO', content):
            score += 0.25
        
        # Análisis de pruebas
        if re.search(r'prueba|evidencia|antecedente|testimonio', content, re.IGNORECASE):
            score += 0.25
        
        # Motivación de la decisión
        if re.search(r'SE RESUELVE|HA LUGAR|NO HA LUGAR', content):
            score += 0.25
        
        # Lógica jurídica
        if re.search(r'por lo tanto|en consecuencia|por estas consideraciones', content, re.IGNORECASE):
            score += 0.25
        
        return score
    
    def _evaluate_judge_procedure(self, content: str) -> float:
        """Evalúa el procedimiento en una resolución judicial"""
        score = 0.0
        
        # Dirección de la audiencia
        if re.search(r'audiencia|oído|visto', content, re.IGNORECASE):
            score += 0.25
        
        # Control del proceso
        if re.search(r'trámite|diligencia|medida', content, re.IGNORECASE):
            score += 0.25
        
        # Cumplimiento de garantías
        if re.search(r'derecho|garantía|debido proceso', content, re.IGNORECASE):
            score += 0.25
        
        # Estructura de la resolución
        if re.search(r'vistos|considerando|resuelvo', content, re.IGNORECASE):
            score += 0.25
        
        return score
    
    def _evaluate_judge_communication(self, content: str) -> float:
        """Evalúa la comunicación en una resolución judicial"""
        score = 0.0
        
        # Claridad y precisión
        if not re.search(r'\b(etc|otros|demás)\b', content, re.IGNORECASE):
            score += 0.33
        
        # Ejercicio de autoridad
        if re.search(r'SE RESUELVE|ORDENA|DISPONE', content):
            score += 0.33
        
        # Imparcialidad
        if not re.search(r'\b(yo|mi|me|opino|creo)\b', content, re.IGNORECASE):
            score += 0.34
        
        return score
    
    def _evaluate_judge_time_management(self, content: str, context: Dict) -> float:
        """Evalúa la gestión del tiempo en una resolución judicial"""
        score = 0.0
        
        # Ritmo de la audiencia
        duration = (context["end_time"] - context["start_time"]).total_seconds()
        if duration <= context["allowed_duration"]:
            score += 0.33
        
        # Tiempo de deliberación (asumimos que una resolución muy corta o muy larga no es óptima)
        words = len(content.split())
        if 100 <= words <= 500:
            score += 0.33
        
        # Oportunidad de la resolución
        if context["current_phase"] == "judge_resolution":
            score += 0.34
        
        return score
    
    def _generate_judge_feedback(self, scores: Dict) -> List[str]:
        """Genera retroalimentación específica para jueces"""
        feedback = []
        
        # Retroalimentación por criterio
        for criteria, data in scores.items():
            if data["score"] < 0.6:
                feedback.extend(data["feedback"]["suggestions"])
        
        return feedback

    def _get_legal_feedback(self, score: float) -> Dict:
        """Genera retroalimentación sobre el conocimiento legal"""
        if score >= 0.8:
            return {
                "level": "Excelente",
                "suggestions": ["Mantiene un alto nivel de análisis legal"]
            }
        elif score >= 0.6:
            return {
                "level": "Bueno",
                "suggestions": ["Considere profundizar en la jurisprudencia aplicable"]
            }
        else:
            return {
                "level": "Necesita Mejora",
                "suggestions": [
                    "Cite artículos específicos de la ley",
                    "Incluya referencias a jurisprudencia relevante",
                    "Desarrolle mejor la fundamentación legal"
                ]
            }

    def _get_argumentation_feedback(self, score: float) -> Dict:
        """Genera retroalimentación sobre la argumentación"""
        if score >= 0.8:
            return {
                "level": "Excelente",
                "suggestions": ["Mantiene un alto nivel de argumentación"]
            }
        elif score >= 0.6:
            return {
                "level": "Bueno",
                "suggestions": ["Refuerce el análisis de las pruebas presentadas"]
            }
        else:
            return {
                "level": "Necesita Mejora",
                "suggestions": [
                    "Estructure mejor sus argumentos",
                    "Analice detalladamente las pruebas",
                    "Motive claramente su decisión"
                ]
            }

    def _get_procedure_feedback(self, score: float) -> Dict:
        """Genera retroalimentación sobre el procedimiento"""
        if score >= 0.8:
            return {
                "level": "Excelente",
                "suggestions": ["Mantiene un excelente control del procedimiento"]
            }
        elif score >= 0.6:
            return {
                "level": "Bueno",
                "suggestions": ["Refuerce el control de las garantías procesales"]
            }
        else:
            return {
                "level": "Necesita Mejora",
                "suggestions": [
                    "Mejore la dirección de la audiencia",
                    "Asegure el cumplimiento de garantías",
                    "Siga la estructura procesal adecuada"
                ]
            }

    def _get_communication_feedback(self, score: float) -> Dict:
        """Genera retroalimentación sobre la comunicación"""
        if score >= 0.8:
            return {
                "level": "Excelente",
                "suggestions": ["Mantiene una comunicación clara y efectiva"]
            }
        elif score >= 0.6:
            return {
                "level": "Bueno",
                "suggestions": ["Mejore la precisión en el lenguaje utilizado"]
            }
        else:
            return {
                "level": "Necesita Mejora",
                "suggestions": [
                    "Evite expresiones ambiguas",
                    "Mantenga un tono imparcial",
                    "Sea más claro y preciso"
                ]
            }

    def _get_time_feedback(self, score: float) -> Dict:
        """Genera retroalimentación sobre la gestión del tiempo"""
        if score >= 0.8:
            return {
                "level": "Excelente",
                "suggestions": ["Mantiene una excelente gestión del tiempo"]
            }
        elif score >= 0.6:
            return {
                "level": "Bueno",
                "suggestions": ["Optimice el tiempo de deliberación"]
            }
        else:
            return {
                "level": "Necesita Mejora",
                "suggestions": [
                    "Ajuste el ritmo de la audiencia",
                    "Reduzca el tiempo de deliberación",
                    "Resuelva en el momento oportuno"
                ]
            }

    def _evaluate_secretary_certification(self, content: str, context: Dict) -> Dict:
        """Evalúa una certificación del secretario"""
        scores = {}
        
        # Evaluación de Conocimiento Legal
        legal_score = self._evaluate_secretary_legal_knowledge(content)
        scores[EvaluationCriteria.LEGAL_KNOWLEDGE.value] = {
            "score": legal_score,
            "weight": self.secretary_criteria[EvaluationCriteria.LEGAL_KNOWLEDGE]["weight"],
            "feedback": self._get_secretary_legal_feedback(legal_score)
        }
        
        # Evaluación de Argumentación
        arg_score = self._evaluate_secretary_argumentation(content)
        scores[EvaluationCriteria.ARGUMENTATION.value] = {
            "score": arg_score,
            "weight": self.secretary_criteria[EvaluationCriteria.ARGUMENTATION]["weight"],
            "feedback": self._get_secretary_argumentation_feedback(arg_score)
        }
        
        # Evaluación de Procedimiento
        proc_score = self._evaluate_secretary_procedure(content, context)
        scores[EvaluationCriteria.PROCEDURE.value] = {
            "score": proc_score,
            "weight": self.secretary_criteria[EvaluationCriteria.PROCEDURE]["weight"],
            "feedback": self._get_secretary_procedure_feedback(proc_score)
        }
        
        # Evaluación de Comunicación
        comm_score = self._evaluate_secretary_communication(content)
        scores[EvaluationCriteria.COMMUNICATION.value] = {
            "score": comm_score,
            "weight": self.secretary_criteria[EvaluationCriteria.COMMUNICATION]["weight"],
            "feedback": self._get_secretary_communication_feedback(comm_score)
        }
        
        # Evaluación de Gestión del Tiempo
        time_score = self._evaluate_secretary_time_management(content, context)
        scores[EvaluationCriteria.TIME_MANAGEMENT.value] = {
            "score": time_score,
            "weight": self.secretary_criteria[EvaluationCriteria.TIME_MANAGEMENT]["weight"],
            "feedback": self._get_secretary_time_feedback(time_score)
        }
        
        # Cálculo de puntaje general
        overall_score = sum(s["score"] * s["weight"] for s in scores.values())
        
        return {
            "timestamp": datetime.now(),
            "overall_score": overall_score,
            "criteria_scores": scores,
            "immediate_feedback": self._generate_secretary_feedback(scores)
        }
    
    def _evaluate_secretary_legal_knowledge(self, content: str) -> float:
        """Evalúa el conocimiento legal del secretario"""
        score = 0.0
        
        # Identificación correcta del tipo de audiencia
        if re.search(r'audiencia de control de detención|audiencia de formalización|audiencia de juicio', content, re.IGNORECASE):
            score += 0.25
        
        # Registro de resoluciones
        if re.search(r'se decretó|se resolvió|se dispuso', content, re.IGNORECASE):
            score += 0.25
        
        # Identificación de intervinientes
        if re.search(r'Ministerio Público|Defensoría|imputado', content, re.IGNORECASE):
            score += 0.25
        
        # Registro de plazos y términos
        if re.search(r'plazo de|término de|dentro de', content, re.IGNORECASE):
            score += 0.25
        
        return score
    
    def _evaluate_secretary_argumentation(self, content: str) -> float:
        """Evalúa la argumentación del secretario"""
        score = 0.0
        
        # Estructura clara del certificado
        if re.search(r'CERTIFICO:|Para constancia', content, re.IGNORECASE):
            score += 0.33
        
        # Numeración y orden lógico
        if re.search(r'\d+\.\s+Que', content):
            score += 0.33
        
        # Conclusión apropiada
        if re.search(r'Para constancia.*firma', content, re.IGNORECASE):
            score += 0.34
        
        return score
    
    def _evaluate_secretary_procedure(self, content: str, context: Dict) -> float:
        """Evalúa el procedimiento del secretario"""
        score = 0.0
        
        # Verificación de documentos requeridos
        docs_required = set(context.get("documents_required", []))
        docs_mentioned = set()
        for doc in ["acta", "resolucion", "oficio"]:
            if re.search(doc, content, re.IGNORECASE):
                docs_mentioned.add(doc)
        if len(docs_mentioned) >= len(docs_required):
            score += 0.25
        
        # Registro de horarios
        if re.search(r'\d{2}:\d{2}\s*-\s*\d{2}:\d{2}', content):
            score += 0.25
        
        # Registro de notificaciones
        if re.search(r'notificación|notificado|notífiqué', content, re.IGNORECASE):
            score += 0.25
        
        # Firma y cargo
        if re.search(r'Secretari[oa]\s+del\s+Tribunal', content):
            score += 0.25
        
        return score
    
    def _evaluate_secretary_communication(self, content: str) -> float:
        """Evalúa la comunicación del secretario"""
        score = 0.0
        
        # Claridad en la redacción
        if not re.search(r'\b(etc|otros|demás)\b', content, re.IGNORECASE):
            score += 0.33
        
        # Precisión en la información
        if re.search(r'RUT|Nº|Rol', content):
            score += 0.33
        
        # Formato profesional
        if re.search(r'[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+', content):
            score += 0.34
        
        return score
    
    def _evaluate_secretary_time_management(self, content: str, context: Dict) -> float:
        """Evalúa la gestión del tiempo del secretario"""
        score = 0.0
        
        # Registro oportuno
        duration = (context["end_time"] - context["start_time"]).total_seconds()
        if duration <= context["allowed_duration"]:
            score += 0.33
        
        # Detalle de horarios
        if re.search(r'\d{2}:\d{2}', content):
            score += 0.33
        
        # Secuencia temporal clara
        if re.search(r'Inicio|Término|durante', content, re.IGNORECASE):
            score += 0.34
        
        return score
    
    def _get_secretary_legal_feedback(self, score: float) -> Dict:
        """Genera retroalimentación sobre el conocimiento legal del secretario"""
        if score >= 0.8:
            return {
                "level": "Excelente",
                "suggestions": ["Mantiene un excelente registro legal"]
            }
        elif score >= 0.6:
            return {
                "level": "Bueno",
                "suggestions": ["Incluya más detalles sobre las resoluciones"]
            }
        else:
            return {
                "level": "Necesita Mejora",
                "suggestions": [
                    "Identifique claramente el tipo de audiencia",
                    "Registre todas las resoluciones importantes",
                    "Incluya la identificación completa de los intervinientes"
                ]
            }
    
    def _get_secretary_argumentation_feedback(self, score: float) -> Dict:
        """Genera retroalimentación sobre la argumentación del secretario"""
        if score >= 0.8:
            return {
                "level": "Excelente",
                "suggestions": ["Mantiene una estructura clara y ordenada"]
            }
        elif score >= 0.6:
            return {
                "level": "Bueno",
                "suggestions": ["Mejore la organización de los puntos certificados"]
            }
        else:
            return {
                "level": "Necesita Mejora",
                "suggestions": [
                    "Use una estructura más clara",
                    "Numere los puntos certificados",
                    "Incluya una conclusión apropiada"
                ]
            }
    
    def _get_secretary_procedure_feedback(self, score: float) -> Dict:
        """Genera retroalimentación sobre el procedimiento del secretario"""
        if score >= 0.8:
            return {
                "level": "Excelente",
                "suggestions": ["Excelente manejo del procedimiento"]
            }
        elif score >= 0.6:
            return {
                "level": "Bueno",
                "suggestions": ["Verifique la completitud de los documentos requeridos"]
            }
        else:
            return {
                "level": "Necesita Mejora",
                "suggestions": [
                    "Registre todos los documentos generados",
                    "Incluya los horarios de la audiencia",
                    "Documente las notificaciones realizadas"
                ]
            }
    
    def _get_secretary_communication_feedback(self, score: float) -> Dict:
        """Genera retroalimentación sobre la comunicación del secretario"""
        if score >= 0.8:
            return {
                "level": "Excelente",
                "suggestions": ["Comunicación clara y profesional"]
            }
        elif score >= 0.6:
            return {
                "level": "Bueno",
                "suggestions": ["Mejore la precisión en la identificación"]
            }
        else:
            return {
                "level": "Necesita Mejora",
                "suggestions": [
                    "Use un lenguaje más preciso",
                    "Incluya identificadores únicos",
                    "Mantenga un formato profesional"
                ]
            }
    
    def _get_secretary_time_feedback(self, score: float) -> Dict:
        """Genera retroalimentación sobre la gestión del tiempo del secretario"""
        if score >= 0.8:
            return {
                "level": "Excelente",
                "suggestions": ["Excelente manejo del tiempo"]
            }
        elif score >= 0.6:
            return {
                "level": "Bueno",
                "suggestions": ["Mejore el detalle de los horarios"]
            }
        else:
            return {
                "level": "Necesita Mejora",
                "suggestions": [
                    "Registre los horarios con mayor detalle",
                    "Mantenga una secuencia temporal clara",
                    "Complete el registro en tiempo oportuno"
                ]
            }
    
    def _generate_secretary_feedback(self, scores: Dict) -> List[str]:
        """Genera retroalimentación específica para secretarios"""
        feedback = []
        
        # Retroalimentación por criterio
        for criteria, data in scores.items():
            if data["score"] < 0.6:
                feedback.extend(data["feedback"]["suggestions"])
        
        return feedback

    def _evaluate_base_interaction(self, content: str, context: Dict, interaction_type: str = "default") -> Dict:
        """Evalúa una interacción específica"""
        evaluation = {}
        
        for criteria in EvaluationCriteria:
            score = self._evaluate_criteria(criteria, content, context, interaction_type)
            evaluation[criteria.value] = {
                "score": score,
                "weight": self.evaluation_criteria[criteria]["weight"],
                "feedback": self._generate_criteria_feedback(criteria, score)
            }
        
        return {
            "timestamp": datetime.now(),
            "overall_score": self._calculate_overall_score(evaluation),
            "criteria_scores": evaluation,
            "immediate_feedback": self._generate_immediate_feedback(evaluation)
        }
    
    def _evaluate_criteria(self,
                          criteria: EvaluationCriteria,
                          content: str,
                          context: Dict,
                          interaction_type: str) -> float:
        """
        Evalúa un criterio específico
        """
        metrics = self.evaluation_criteria[criteria]["metrics"]
        scores = []
        
        for metric in metrics:
            # Aquí se implementaría la lógica específica para cada métrica
            # Por ahora, usamos un placeholder
            score = self._evaluate_metric(metric, content, context)
            scores.append(score)
        
        return sum(scores) / len(scores)
    
    def _evaluate_metric(self,
                        metric: str,
                        content: str,
                        context: Dict) -> float:
        """
        Evalúa una métrica específica basada en el contenido y contexto
        """
        # Métricas de conocimiento legal
        if metric == "citation_accuracy":
            return self._evaluate_citation_accuracy(content)
        elif metric == "law_application":
            return self._evaluate_law_application(content, context)
        elif metric == "precedent_use":
            return self._evaluate_precedent_use(content)
        
        # Métricas de argumentación
        elif metric == "logic_structure":
            return self._evaluate_logic_structure(content)
        elif metric == "evidence_use":
            return self._evaluate_evidence_use(content, context)
        elif metric == "counter_arguments":
            return self._evaluate_counter_arguments(content, context)
        
        # Métricas de procedimiento
        elif metric == "protocol_compliance":
            return self._evaluate_protocol_compliance(content, context)
        elif metric == "timing":
            return self._evaluate_timing(context)
        elif metric == "formalities":
            return self._evaluate_formalities(content)
        
        # Métricas de comunicación
        elif metric == "clarity":
            return self._evaluate_clarity(content)
        elif metric == "persuasion":
            return self._evaluate_persuasion(content)
        elif metric == "professional_conduct":
            return self._evaluate_professional_conduct(content)
        
        # Métricas de gestión del tiempo
        elif metric == "intervention_timing":
            return self._evaluate_intervention_timing(context)
        elif metric == "response_time":
            return self._evaluate_response_time(context)
        elif metric == "efficiency":
            return self._evaluate_efficiency(content, context)
        
        return 0.0

    def _evaluate_citation_accuracy(self, content: str) -> float:
        """Evalúa la precisión de las citas legales"""
        # Buscar referencias a artículos, leyes, códigos
        citation_patterns = [
            r'artículo\s+\d+',
            r'art\.\s*\d+',
            r'ley\s+\d+[\.\d]*',
            r'código\s+\w+'
        ]
        citations = sum(1 for pattern in citation_patterns if re.search(pattern, content.lower()))
        return min(citations * 0.25, 1.0)

    def _evaluate_law_application(self, content: str, context: Dict) -> float:
        """Evalúa la correcta aplicación de la ley"""
        # Verificar coherencia entre la ley citada y el contexto
        phase = context.get('current_phase')
        if not phase:
            return 0.0
        
        phase_keywords = {
            'detention_report': ['detención', 'flagrancia', 'derechos'],
            'prosecutor_arguments': ['prisión preventiva', 'peligro', 'necesidad'],
            'defender_arguments': ['libertad', 'proporcionalidad', 'arraigo'],
            'judge_resolution': ['mérito', 'fundada', 'proporcional']
        }
        
        keywords = phase_keywords.get(phase, [])
        matches = sum(1 for keyword in keywords if keyword in content.lower())
        return min(matches / len(keywords) if keywords else 0, 1.0)

    def _evaluate_logic_structure(self, content: str) -> float:
        """Evalúa la estructura lógica de la argumentación"""
        # Buscar conectores lógicos y estructura argumentativa
        logic_connectors = [
            'por lo tanto', 'en consecuencia', 'debido a',
            'considerando', 'sin embargo', 'no obstante',
            'en primer lugar', 'en segundo lugar', 'finalmente'
        ]
        
        matches = sum(1 for connector in logic_connectors if connector in content.lower())
        return min(matches * 0.2, 1.0)

    def _evaluate_protocol_compliance(self, content: str, context: Dict) -> float:
        """Evalúa el cumplimiento del protocolo de la audiencia"""
        phase = context.get('current_phase')
        role = context.get('speaker_role')
        
        if not (phase and role):
            return 0.0
        
        # Verificar si la acción es permitida en la fase actual
        allowed_actions = context.get('allowed_actions', [])
        action = context.get('action')
        
        if action not in allowed_actions:
            return 0.0
        
        # Verificar formalidades según la fase
        phase_formalities = {
            'opening': ['buenos días', 'se da inicio', 'audiencia'],
            'detention_report': ['detenido', 'circunstancias', 'procedimiento'],
            'prosecutor_arguments': ['solicito', 'fundamentos', 'pruebas'],
            'defender_arguments': ['defensa', 'solicita', 'argumentos'],
            'judge_resolution': ['resuelvo', 'considerando', 'mérito']
        }
        
        formalities = phase_formalities.get(phase, [])
        matches = sum(1 for form in formalities if form in content.lower())
        return min(matches / len(formalities) if formalities else 0, 1.0)
        """
        Evalúa una métrica específica
        """
        # Implementar lógica específica para cada métrica
        # Por ahora retornamos un valor de ejemplo
        return 0.75
    
    def _calculate_overall_score(self, evaluation: Dict) -> float:
        """
        Calcula la puntuación general ponderada
        """
        weighted_sum = 0
        for criteria in EvaluationCriteria:
            criteria_eval = evaluation[criteria.value]
            weighted_sum += criteria_eval["score"] * criteria_eval["weight"]
        
        return round(weighted_sum, 2)
    
    def _generate_criteria_feedback(self,
                                  criteria: EvaluationCriteria,
                                  score: float) -> Dict:
        """
        Genera retroalimentación específica para un criterio
        """
        feedback = {
            "level": self._get_performance_level(score),
            "suggestions": [],
            "resources": []
        }
        
        if score < 0.6:
            feedback["suggestions"].append(
                self._get_improvement_suggestion(criteria)
            )
            feedback["resources"].extend(
                self._get_learning_resources(criteria)
            )
        
        return feedback
    
    def _generate_immediate_feedback(self, evaluation: Dict) -> List[str]:
        """
        Genera retroalimentación inmediata basada en la evaluación
        """
        feedback = []
        
        # Analizar cada criterio
        for criteria in EvaluationCriteria:
            score = evaluation[criteria.value]['score']
            if score < 0.6:
                criteria_name = self.evaluation_metrics.get(criteria.value, criteria.value)
                tip = self._get_quick_tip(criteria)
                feedback.append(f"Atención en {criteria_name}: {tip}")
        
        return feedback

    def _evaluate_precedent_use(self, content: str) -> float:
        """
        Evalúa el uso de precedentes judiciales
        """
        precedent_patterns = [
            r'sentencia\s+\d+',
            r'causa\s+rol\s+\d+',
            r'jurisprudencia',
            r'precedente'
        ]
        matches = sum(1 for pattern in precedent_patterns if re.search(pattern, content.lower()))
        return min(matches * 0.33, 1.0)

    def _evaluate_evidence_use(self, content: str, context: Dict) -> float:
        """
        Evalúa el uso de evidencia en la argumentación
        """
        evidence_keywords = [
            'prueba', 'evidencia', 'documento', 'testigo',
            'peritaje', 'informe', 'registro', 'antecedente'
        ]
        
        # Verificar referencias a evidencia
        matches = sum(1 for keyword in evidence_keywords if keyword in content.lower())
        
        # Verificar si la evidencia es relevante para la fase actual
        phase = context.get('current_phase')
        if phase in ['prosecutor_arguments', 'defender_arguments']:
            return min(matches * 0.25, 1.0)
        return min(matches * 0.15, 1.0)

    def _evaluate_counter_arguments(self, content: str, context: Dict) -> float:
        """
        Evalúa la capacidad de contra-argumentación
        """
        counter_patterns = [
            r'sin embargo',
            r'no obstante',
            r'por el contrario',
            r'en contraste',
            r'a diferencia',
            r'se opone',
            r'contradice'
        ]
        
        matches = sum(1 for pattern in counter_patterns if re.search(pattern, content.lower()))
        
        # Bonus por contra-argumentos en fases específicas
        phase = context.get('current_phase')
        if phase in ['defender_arguments', 'prosecutor_rebuttal']:
            return min(matches * 0.4, 1.0)
        return min(matches * 0.25, 1.0)

    def _evaluate_timing(self, context: Dict) -> float:
        """
        Evalúa el manejo del tiempo en la intervención
        """
        start_time = context.get('start_time')
        end_time = context.get('end_time')
        allowed_duration = context.get('allowed_duration', 300)  # 5 minutos por defecto
        
        if not (start_time and end_time):
            return 0.0
        
        duration = (end_time - start_time).total_seconds()
        if duration > allowed_duration * 1.2:  # 20% de margen
            return 0.0
        elif duration > allowed_duration:
            return 0.5
        return 1.0

    def _evaluate_formalities(self, content: str) -> float:
        """
        Evalúa el cumplimiento de formalidades generales
        """
        formality_patterns = [
            r'señor[ía]*\s+juez',
            r'ilustrísim[oa]',
            r'con\s+el\s+debido\s+respeto',
            r'solicito\s+a\s+[su]*\s+señoría',
            r'vengo\s+en'
        ]
        
        matches = sum(1 for pattern in formality_patterns if re.search(pattern, content.lower()))
        return min(matches * 0.33, 1.0)

    def _evaluate_clarity(self, content: str) -> float:
        """
        Evalúa la claridad en la comunicación
        """
        # Analizar longitud promedio de oraciones
        sentences = [s.strip() for s in re.split(r'[.!?]+', content) if s.strip()]
        if not sentences:
            return 0.0
        
        avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Penalizar oraciones muy largas (más de 25 palabras)
        if avg_length > 25:
            return 0.5
        elif avg_length > 15:
            return 0.75
        return 1.0

    def _evaluate_persuasion(self, content: str) -> float:
        """
        Evalúa la capacidad de persuasión
        """
        persuasion_elements = [
            r'demuestr[oa]',
            r'evidenci[oa]',
            r'comprob[óo]',
            r'claramente',
            r'sin\s+duda',
            r'necesari[oa]mente',
            r'fundamental'
        ]
        
        matches = sum(1 for pattern in persuasion_elements if re.search(pattern, content.lower()))
        return min(matches * 0.25, 1.0)

    def _evaluate_professional_conduct(self, content: str) -> float:
        """
        Evalúa la conducta profesional
        """
        unprofessional_patterns = [
            r'insist[oe]',
            r'reclam[oe]',
            r'protest[oe]',
            r'exig[oe]',
            r'inaceptable',
            r'inadmisible'
        ]
        
        matches = sum(1 for pattern in unprofessional_patterns if re.search(pattern, content.lower()))
        return max(0, 1 - matches * 0.25)

    def _evaluate_intervention_timing(self, context: Dict) -> float:
        """
        Evalúa el momento de la intervención
        """
        current_phase = context.get('current_phase')
        allowed_phases = context.get('allowed_phases', [])
        
        if not current_phase:
            return 0.0
        
        if current_phase not in allowed_phases:
            return 0.0
        return 1.0

    def _evaluate_response_time(self, context: Dict) -> float:
        """
        Evalúa el tiempo de respuesta
        """
        response_time = context.get('response_time', 0)  # en segundos
        if response_time > 10:
            return 0.0
        elif response_time > 5:
            return 0.5
        return 1.0

    def _evaluate_efficiency(self, content: str, context: Dict) -> float:
        """
        Evalúa la eficiencia en la comunicación
        """
        # Analizar repeticiones innecesarias
        words = content.lower().split()
        if not words:
            return 0.0
        
        word_count = len(words)
        unique_words = len(set(words))
        
        # Calcular ratio de palabras únicas
        uniqueness_ratio = unique_words / word_count
        
        # Penalizar textos muy largos
        if word_count > 200:
            return uniqueness_ratio * 0.5
        return uniqueness_ratio

    def _get_performance_level(self, score: float) -> str:
        """
        Determina el nivel de desempeño basado en el puntaje
        """
        if score >= 0.9:
            return "Excelente"
        elif score >= 0.8:
            return "Muy Bueno"
        elif score >= 0.7:
            return "Bueno"
        elif score >= 0.6:
            return "Regular"
        else:
            return "Necesita Mejora"

    def _get_improvement_suggestion(self, criteria: EvaluationCriteria) -> str:
        """
        Retorna una sugerencia de mejora para un criterio
        """
        suggestions = {
            EvaluationCriteria.LEGAL_KNOWLEDGE: [
                "Refuerza tus citas legales con artículos específicos",
                "Relaciona tus argumentos con jurisprudencia relevante",
                "Profundiza en la aplicación práctica de la norma"
            ],
            EvaluationCriteria.ARGUMENTATION: [
                "Estructura tus argumentos de manera más lógica",
                "Fortalece tus contra-argumentos",
                "Mejora el uso de evidencia para respaldar tus puntos"
            ],
            EvaluationCriteria.PROCEDURE: [
                "Presta atención a los protocolos de la audiencia",
                "Mejora el manejo de los tiempos de intervención",
                "Cumple con las formalidades requeridas"
            ],
            EvaluationCriteria.COMMUNICATION: [
                "Usa un lenguaje más claro y conciso",
                "Mejora tu capacidad de persuasión",
                "Mantén un tono profesional constante"
            ],
            EvaluationCriteria.TIME_MANAGEMENT: [
                "Optimiza la duración de tus intervenciones",
                "Mejora tus tiempos de respuesta",
                "Sé más eficiente en tu comunicación"
            ]
        }
        
        options = suggestions.get(criteria, [])
        return options[hash(str(datetime.now())) % len(options)] if options else ""

    def _get_learning_resources(self, criteria: EvaluationCriteria) -> List[Dict]:
        """
        Retorna recursos de aprendizaje para un criterio
        """
        resources = {
            EvaluationCriteria.LEGAL_KNOWLEDGE: [
                {
                    "type": "document",
                    "title": "Manual de Citas Legales",
                    "url": "/resources/legal_citations.pdf"
                },
                {
                    "type": "video",
                    "title": "Técnicas de Investigación Jurídica",
                    "url": "/resources/legal_research.mp4"
                }
            ],
            EvaluationCriteria.ARGUMENTATION: [
                {
                    "type": "course",
                    "title": "Argumentación Jurídica Avanzada",
                    "url": "/courses/advanced_argumentation"
                },
                {
                    "type": "exercise",
                    "title": "Práctica de Contra-argumentación",
                    "url": "/exercises/counter_arguments"
                }
            ],
            EvaluationCriteria.PROCEDURE: [
                {
                    "type": "simulation",
                    "title": "Simulador de Audiencias",
                    "url": "/simulations/hearing_practice"
                },
                {
                    "type": "guide",
                    "title": "Guía de Protocolos Judiciales",
                    "url": "/guides/court_protocols"
                }
            ],
            EvaluationCriteria.COMMUNICATION: [
                {
                    "type": "workshop",
                    "title": "Taller de Oratoria Jurídica",
                    "url": "/workshops/legal_speech"
                },
                {
                    "type": "video",
                    "title": "Técnicas de Persuasión en el Tribunal",
                    "url": "/resources/persuasion_techniques.mp4"
                }
            ],
            EvaluationCriteria.TIME_MANAGEMENT: [
                {
                    "type": "tool",
                    "title": "Cronometrador de Intervenciones",
                    "url": "/tools/intervention_timer"
                },
                {
                    "type": "guide",
                    "title": "Guía de Eficiencia en Audiencias",
                    "url": "/guides/hearing_efficiency"
                }
            ]
        }
        
        return resources.get(criteria, [])

    def _get_quick_tip(self, criteria: EvaluationCriteria) -> str:
        """
        Retorna un consejo rápido para mejora inmediata
        """
        tips = {
            EvaluationCriteria.LEGAL_KNOWLEDGE: [
                "Cita al menos un artículo específico en cada argumento principal",
                "Relaciona tus argumentos con jurisprudencia reciente",
                "Explica cómo la ley se aplica al caso concreto"
            ],
            EvaluationCriteria.ARGUMENTATION: [
                "Estructura: premisa, argumento, conclusión",
                "Anticipa y responde a posibles contra-argumentos",
                "Usa evidencia específica para cada punto clave"
            ],
            EvaluationCriteria.PROCEDURE: [
                "Sigue el orden establecido para las intervenciones",
                "Respeta los tiempos asignados",
                "Usa las formalidades correctas al dirigirte al tribunal"
            ],
            EvaluationCriteria.COMMUNICATION: [
                "Mantén oraciones cortas y claras",
                "Usa pausas estratégicas para enfatizar puntos clave",
                "Mantén contacto visual con el tribunal"
            ],
            EvaluationCriteria.TIME_MANAGEMENT: [
                "Prioriza tus argumentos más fuertes",
                "Prepara respuestas concisas",
                "Evita repeticiones innecesarias"
            ]
        }
        
        options = tips.get(criteria, [])
        return options[hash(str(datetime.now())) % len(options)] if options else ""
        if score >= 0.9:
            return "Excelente"
        elif score >= 0.8:
            return "Muy Bueno"
        elif score >= 0.7:
            return "Bueno"
        elif score >= 0.6:
            return "Regular"
        else:
            return "Necesita Mejora"
    
    def _get_improvement_suggestion(self, criteria: EvaluationCriteria) -> str:
        """
        Retorna una sugerencia de mejora para un criterio
        """
        suggestions = {
            EvaluationCriteria.LEGAL_KNOWLEDGE: "Reforzar conocimiento de normativa aplicable",
            EvaluationCriteria.ARGUMENTATION: "Mejorar estructura de argumentos",
            EvaluationCriteria.PROCEDURE: "Revisar protocolos procesales",
            EvaluationCriteria.COMMUNICATION: "Trabajar en claridad de expresión",
            EvaluationCriteria.TIME_MANAGEMENT: "Optimizar tiempos de intervención"
        }
        return suggestions.get(criteria, "Revisar material de estudio")
    
    def _get_learning_resources(self, criteria: EvaluationCriteria) -> List[str]:
        """
        Retorna recursos de aprendizaje para un criterio
        """
        resources = {
            EvaluationCriteria.LEGAL_KNOWLEDGE: [
                "Manual de Derecho Procesal Penal",
                "Casos Prácticos - Unidad 3"
            ],
            EvaluationCriteria.ARGUMENTATION: [
                "Técnicas de Argumentación Jurídica",
                "Taller de Litigación"
            ]
        }
        return resources.get(criteria, ["Material General de Estudio"])
    
    def _get_quick_tip(self, criteria: EvaluationCriteria) -> str:
        """
        Retorna un consejo rápido para mejora inmediata
        """
        tips = {
            EvaluationCriteria.LEGAL_KNOWLEDGE: "Citar artículos específicos",
            EvaluationCriteria.ARGUMENTATION: "Estructurar argumentos con premisas claras",
            EvaluationCriteria.PROCEDURE: "Seguir protocolo formal",
            EvaluationCriteria.COMMUNICATION: "Mantener contacto visual y voz clara",
            EvaluationCriteria.TIME_MANAGEMENT: "Ser conciso y directo"
        }
        return tips.get(criteria, "Revisar material de apoyo")
