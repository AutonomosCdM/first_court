"""
Script para probar la interacción entre el Juez y el Fiscal
"""
import os
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv
import logging
from rich.logging import RichHandler
from src.agents.judge import JudgeAgent
from src.agents.prosecutor import ProsecutorAgent

# Configurar logging
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger("rich")
console = Console()

def simulate_criminal_case():
    """Simula un caso penal con interacción entre Juez y Fiscal"""
    # Caso de prueba: Robo en lugar habitado
    case_data = {
        "tipo_causa": "Penal",
        "rit": "1234-2024",
        "tribunal": "3° Juzgado de Garantía de Santiago",
        "delito": "Robo en lugar habitado",
        "fecha_hechos": "2024-02-12",
        "lugar": "Calle Ejemplo 123, Santiago",
        "etapa_procesal": "Audiencia de formalización",
        "victima": {
            "nombre": "Juan Pérez",
            "edad": 45,
            "domicilio": "Calle Ejemplo 123, Santiago"
        },
        "imputado": {
            "nombre": "Pedro González",
            "edad": 28,
            "antecedentes": ["Hurto simple (2022)", "Receptación (2023)"]
        },
        "hechos": [
            "Ingreso forzado por ventana trasera",
            "Sustracción de especies electrónicas y joyas",
            "Testigo vio al sospechoso salir del domicilio",
            "Especies encontradas en domicilio del imputado"
        ]
    }
    
    # Crear instancias de los agentes
    judge = JudgeAgent("Juez de Garantía")
    prosecutor = ProsecutorAgent("Fiscal")
    
    # 1. Fiscal investiga el caso
    console.print("\n[bold blue]1. Fiscal inicia investigación:[/bold blue]")
    investigation = prosecutor.investigate_case(case_data)
    console.print(Panel.fit(
        str(investigation),
        title="Informe de Investigación del Fiscal",
        border_style="blue"
    ))
    
    # 2. Juez analiza el caso
    console.print("\n[bold green]2. Juez analiza el caso:[/bold green]")
    analysis = judge.analyze_case(case_data)
    console.print(Panel.fit(
        str(analysis),
        title="Análisis del Juez",
        border_style="green"
    ))
    
    # 3. Fiscal formula acusación
    investigation_data = {
        **case_data,
        "evidencias": [
            {
                "tipo": "Material",
                "descripcion": "Especies sustraídas encontradas",
                "valor_probatorio": "Alto"
            },
            {
                "tipo": "Testimonial",
                "descripcion": "Testigo presencial",
                "valor_probatorio": "Alto"
            },
            {
                "tipo": "Pericial",
                "descripcion": "Informe de huella dactilar",
                "valor_probatorio": "Alto"
            }
        ]
    }
    
    console.print("\n[bold blue]3. Fiscal formula acusación:[/bold blue]")
    accusation = prosecutor.formulate_accusation(investigation_data)
    console.print(Panel.fit(
        str(accusation),
        title="Acusación del Fiscal",
        border_style="blue"
    ))
    
    # 4. Juez revisa las evidencias
    console.print("\n[bold green]4. Juez evalúa evidencias:[/bold green]")
    evidence_review = judge.review_evidence(investigation_data["evidencias"])
    console.print(Panel.fit(
        str(evidence_review),
        title="Evaluación de Evidencias por el Juez",
        border_style="green"
    ))
    
    # 5. Juez emite resolución
    console.print("\n[bold green]5. Juez emite resolución:[/bold green]")
    resolution = judge.issue_resolution(case_data["rit"], {
        "caso": case_data,
        "investigacion": investigation,
        "acusacion": accusation,
        "evidencias": evidence_review
    })
    console.print(Panel.fit(
        str(resolution),
        title="Resolución del Juez",
        border_style="green"
    ))

def main():
    """Función principal"""
    console.print("\n🏛️  [bold]Simulación de Caso Judicial[/bold]\n")
    
    load_dotenv()
    
    if not os.getenv("DEEPSEEK_API_KEY"):
        log.error("DEEPSEEK_API_KEY no encontrada en variables de entorno")
        return
    
    try:
        simulate_criminal_case()
        console.print("\n✨ [bold green]Simulación completada con éxito[/bold green] ✨\n")
    except Exception as e:
        log.error(f"Error en la simulación: {e}")
        console.print("\n❌ [bold red]Error en la simulación[/bold red]\n")

if __name__ == "__main__":
    main()
