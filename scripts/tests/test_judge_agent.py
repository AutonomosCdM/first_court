"""
Script de prueba para el Agente Juez
"""
import os
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv
import logging
from rich.logging import RichHandler
from src.agents.judge import JudgeAgent

# Configurar logging
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger("rich")
console = Console()

def test_case_analysis():
    """Prueba el análisis de un caso por parte del juez"""
    # Caso de prueba: Demanda por incumplimiento de contrato
    test_case = {
        "tipo_causa": "Civil",
        "materia": "Incumplimiento de Contrato",
        "demandante": {
            "nombre": "Empresa Constructora ABC Ltda.",
            "rol": "demandante"
        },
        "demandado": {
            "nombre": "Inmobiliaria XYZ S.A.",
            "rol": "demandado"
        },
        "pretension": "Cobro de $150.000.000 por incumplimiento en pago de obras realizadas",
        "antecedentes": [
            "Contrato de construcción firmado el 01/01/2024",
            "Obras terminadas y recepcionadas el 01/02/2024",
            "Facturas impagas por $150.000.000",
            "Cartas de cobro enviadas sin respuesta"
        ]
    }
    
    try:
        judge = JudgeAgent("Juez Civil")
        analysis = judge.analyze_case(test_case)
        
        console.print("\n[bold blue]Análisis del Caso:[/bold blue]")
        console.print(Panel.fit(
            str(analysis),
            title="Evaluación Judicial",
            border_style="green"
        ))
        
        return True
    except Exception as e:
        log.error(f"Error en el análisis del caso: {e}")
        return False

def test_evidence_review():
    """Prueba la evaluación de evidencias"""
    evidence = [
        {
            "tipo": "Documento",
            "descripcion": "Contrato de construcción",
            "fecha": "01/01/2024",
            "contenido": "Contrato firmado entre las partes que establece términos y condiciones"
        },
        {
            "tipo": "Documento",
            "descripcion": "Facturas",
            "fecha": "01/02/2024",
            "contenido": "Facturas emitidas por los servicios de construcción"
        },
        {
            "tipo": "Correspondencia",
            "descripcion": "Cartas de cobro",
            "fecha": "15/02/2024",
            "contenido": "Tres cartas de cobro enviadas al demandado"
        }
    ]
    
    try:
        judge = JudgeAgent("Juez Civil")
        evaluation = judge.review_evidence(evidence)
        
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

def main():
    """Función principal de prueba"""
    console.print("\n🔍 [bold blue]Iniciando pruebas del Agente Juez[/bold blue]\n")
    
    load_dotenv()
    
    if not os.getenv("DEEPSEEK_API_KEY"):
        log.error("DEEPSEEK_API_KEY no encontrada en variables de entorno")
        return
    
    # Ejecutar pruebas
    case_analysis_ok = test_case_analysis()
    evidence_review_ok = test_evidence_review()
    
    if case_analysis_ok and evidence_review_ok:
        console.print("\n✨ [bold green]Pruebas del Agente Juez completadas con éxito[/bold green] ✨\n")
    else:
        console.print("\n❌ [bold red]Algunas pruebas fallaron[/bold red]\n")

if __name__ == "__main__":
    main()
