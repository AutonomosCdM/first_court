"""
Script de prueba para el Agente Defensor
"""
import os
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv
import logging
from rich.logging import RichHandler
from src.agents.defender import DefenderAgent

# Configurar logging
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger("rich")
console = Console()

def test_defense_analysis():
    """Prueba el análisis de caso desde la perspectiva de la defensa"""
    # Caso de prueba: Robo en lugar habitado
    test_case = {
        "tipo_causa": "Penal",
        "delito": "Robo en lugar habitado",
        "fecha_hechos": "2024-02-12",
        "lugar": "Calle Ejemplo 123, Santiago",
        "imputado": {
            "nombre": "Pedro González",
            "edad": 28,
            "antecedentes": ["Hurto simple (2022)", "Receptación (2023)"]
        },
        "evidencia_fiscal": [
            "Ingreso forzado por ventana trasera",
            "Sustracción de especies electrónicas y joyas",
            "Testigo vio al sospechoso salir del domicilio",
            "Especies encontradas en domicilio del imputado"
        ],
        "detalles_detencion": {
            "fecha": "2024-02-13",
            "hora": "02:30",
            "lugar": "Domicilio del imputado",
            "circunstancias": "Allanamiento sin orden judicial previa"
        }
    }
    
    try:
        defender = DefenderAgent("Defensor Penal")
        analysis = defender.analyze_defense_case(test_case)
        
        console.print("\n[bold blue]Análisis de la Defensa:[/bold blue]")
        console.print(Panel.fit(
            str(analysis),
            title="Estrategia de Defensa",
            border_style="green"
        ))
        
        return True
    except Exception as e:
        log.error(f"Error en el análisis de la defensa: {e}")
        return False

def test_evidence_evaluation():
    """Prueba la evaluación de evidencias desde la perspectiva de la defensa"""
    evidence = [
        {
            "tipo": "Testimonial",
            "descripcion": "Testigo presencial",
            "contenido": "Vio al sospechoso salir del domicilio",
            "circunstancias": "Observación nocturna a distancia"
        },
        {
            "tipo": "Material",
            "descripcion": "Especies recuperadas",
            "contenido": "Electrónicos y joyas encontradas en domicilio del imputado",
            "circunstancias": "Allanamiento sin orden judicial"
        },
        {
            "tipo": "Pericial",
            "descripcion": "Informe de huellas",
            "contenido": "Huellas parciales en la ventana",
            "circunstancias": "Levantamiento 24 horas después del hecho"
        }
    ]
    
    try:
        defender = DefenderAgent("Defensor Penal")
        evaluation = defender.evaluate_evidence(evidence)
        
        console.print("\n[bold blue]Evaluación de Evidencias:[/bold blue]")
        console.print(Panel.fit(
            str(evaluation),
            title="Análisis de Evidencias",
            border_style="green"
        ))
        
        return True
    except Exception as e:
        log.error(f"Error en la evaluación de evidencias: {e}")
        return False

def test_defense_preparation():
    """Prueba la preparación de la defensa"""
    case_data = {
        "tipo_causa": "Penal",
        "delito": "Robo en lugar habitado",
        "imputado": {
            "nombre": "Pedro González",
            "edad": 28,
            "situacion": "Primerizo en delitos violentos"
        }
    }
    
    prosecution_arguments = {
        "calificacion_juridica": "Robo en lugar habitado",
        "participacion": "Autor directo",
        "agravantes": [
            "Nocturnidad",
            "Escalamiento",
            "Reincidencia"
        ],
        "pena_solicitada": "5 años y 1 día"
    }
    
    try:
        defender = DefenderAgent("Defensor Penal")
        defense = defender.prepare_defense(case_data, prosecution_arguments)
        
        console.print("\n[bold blue]Preparación de la Defensa:[/bold blue]")
        console.print(Panel.fit(
            str(defense),
            title="Estrategia y Argumentos",
            border_style="green"
        ))
        
        return True
    except Exception as e:
        log.error(f"Error en la preparación de la defensa: {e}")
        return False

def main():
    """Función principal de prueba"""
    console.print("\n🔍 [bold blue]Iniciando pruebas del Agente Defensor[/bold blue]\n")
    
    load_dotenv()
    
    if not os.getenv("DEEPSEEK_API_KEY"):
        log.error("DEEPSEEK_API_KEY no encontrada en variables de entorno")
        return
    
    # Ejecutar pruebas
    analysis_ok = test_defense_analysis()
    evidence_ok = test_evidence_evaluation()
    defense_ok = test_defense_preparation()
    
    if analysis_ok and evidence_ok and defense_ok:
        console.print("\n✨ [bold green]Pruebas del Agente Defensor completadas con éxito[/bold green] ✨\n")
    else:
        console.print("\n❌ [bold red]Algunas pruebas fallaron[/bold red]\n")

if __name__ == "__main__":
    main()
