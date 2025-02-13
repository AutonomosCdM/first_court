"""
Script de prueba para el Agente Fiscal
"""
import os
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv
import logging
from rich.logging import RichHandler
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

def test_case_investigation():
    """Prueba la investigación de un caso por parte del fiscal"""
    # Caso de prueba: Robo en lugar habitado
    test_case = {
        "tipo_causa": "Penal",
        "delito": "Robo en lugar habitado",
        "fecha_hechos": "2024-02-12",
        "lugar": "Calle Ejemplo 123, Santiago",
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
    
    try:
        prosecutor = ProsecutorAgent("Fiscal Penal")
        investigation = prosecutor.investigate_case(test_case)
        
        console.print("\n[bold blue]Análisis de la Investigación:[/bold blue]")
        console.print(Panel.fit(
            str(investigation),
            title="Informe de Investigación",
            border_style="green"
        ))
        
        return True
    except Exception as e:
        log.error(f"Error en la investigación del caso: {e}")
        return False

def test_accusation_formulation():
    """Prueba la formulación de una acusación"""
    investigation_data = {
        "delito": "Robo en lugar habitado",
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
        ],
        "imputado": {
            "nombre": "Pedro González",
            "participacion": "Autor directo",
            "antecedentes": ["Hurto simple (2022)", "Receptación (2023)"]
        },
        "circunstancias": [
            "Nocturnidad",
            "Escalamiento",
            "Reincidencia"
        ]
    }
    
    try:
        prosecutor = ProsecutorAgent("Fiscal Penal")
        accusation = prosecutor.formulate_accusation(investigation_data)
        
        console.print("\n[bold blue]Acusación Formulada:[/bold blue]")
        console.print(Panel.fit(
            str(accusation),
            title="Escrito de Acusación",
            border_style="green"
        ))
        
        return True
    except Exception as e:
        log.error(f"Error en la formulación de la acusación: {e}")
        return False

def main():
    """Función principal de prueba"""
    console.print("\n🔍 [bold blue]Iniciando pruebas del Agente Fiscal[/bold blue]\n")
    
    load_dotenv()
    
    if not os.getenv("DEEPSEEK_API_KEY"):
        log.error("DEEPSEEK_API_KEY no encontrada en variables de entorno")
        return
    
    # Ejecutar pruebas
    investigation_ok = test_case_investigation()
    accusation_ok = test_accusation_formulation()
    
    if investigation_ok and accusation_ok:
        console.print("\n✨ [bold green]Pruebas del Agente Fiscal completadas con éxito[/bold green] ✨\n")
    else:
        console.print("\n❌ [bold red]Algunas pruebas fallaron[/bold red]\n")

if __name__ == "__main__":
    main()
