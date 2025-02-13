"""
Script de prueba para el Agente Secretario
"""
import os
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv
import logging
from rich.logging import RichHandler
from src.agents.secretary import SecretaryAgent
from datetime import datetime, timedelta

# Configurar logging
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger("rich")
console = Console()

def test_case_status_review():
    """Prueba la revisión del estado de una causa"""
    test_case = {
        "tipo_causa": "Penal",
        "rit": "1234-2024",
        "tribunal": "3° Juzgado de Garantía de Santiago",
        "delito": "Robo en lugar habitado",
        "etapa_procesal": "Audiencia de formalización",
        "fecha_inicio": "2024-02-12",
        "ultima_actuacion": "2024-02-13",
        "partes": {
            "fiscal": {
                "nombre": "María López",
                "correo": "mlopez@fiscalia.cl"
            },
            "defensor": {
                "nombre": "Juan Pérez",
                "correo": "jperez@defensoría.cl"
            },
            "imputado": {
                "nombre": "Pedro González",
                "rut": "12.345.678-9"
            }
        },
        "actuaciones": [
            {
                "fecha": "2024-02-12",
                "tipo": "Ingreso de causa",
                "estado": "Completada"
            },
            {
                "fecha": "2024-02-13",
                "tipo": "Solicitud de audiencia",
                "estado": "Pendiente"
            }
        ]
    }
    
    try:
        secretary = SecretaryAgent()
        status = secretary.review_case_status(test_case)
        
        console.print("\n[bold blue]Estado de la Causa:[/bold blue]")
        console.print(Panel.fit(
            str(status),
            title="Revisión de Estado",
            border_style="blue"
        ))
        
        return True
    except Exception as e:
        log.error(f"Error en la revisión de estado: {e}")
        return False

def test_resolution_generation():
    """Prueba la generación de una resolución"""
    context = {
        "tipo_causa": "Penal",
        "rit": "1234-2024",
        "tribunal": "3° Juzgado de Garantía de Santiago",
        "materia": "Solicitud de audiencia de formalización",
        "solicitante": "Ministerio Público",
        "fundamentos": [
            "Existencia de antecedentes suficientes",
            "Necesidad de formalizar la investigación",
            "Imputado en libertad"
        ],
        "urgencia": "Normal"
    }
    
    try:
        secretary = SecretaryAgent()
        resolution = secretary.generate_resolution(
            "Decreto de tramitación",
            context
        )
        
        console.print("\n[bold blue]Resolución Generada:[/bold blue]")
        console.print(Panel.fit(
            str(resolution),
            title="Resolución",
            border_style="blue"
        ))
        
        return True
    except Exception as e:
        log.error(f"Error en la generación de resolución: {e}")
        return False

def test_hearing_scheduling():
    """Prueba la programación de una audiencia"""
    case_data = {
        "tipo_causa": "Penal",
        "rit": "1234-2024",
        "tribunal": "3° Juzgado de Garantía de Santiago",
        "tipo_audiencia": "Formalización",
        "urgencia": "Normal",
        "duracion_estimada": "30 minutos"
    }
    
    participants = [
        {
            "rol": "Juez",
            "nombre": "Ana García",
            "disponibilidad": ["09:00-13:00", "15:00-17:00"]
        },
        {
            "rol": "Fiscal",
            "nombre": "María López",
            "disponibilidad": ["10:00-18:00"]
        },
        {
            "rol": "Defensor",
            "nombre": "Juan Pérez",
            "disponibilidad": ["09:00-18:00"]
        }
    ]
    
    try:
        secretary = SecretaryAgent()
        schedule = secretary.schedule_hearing(
            "Formalización",
            case_data,
            participants
        )
        
        console.print("\n[bold blue]Programación de Audiencia:[/bold blue]")
        console.print(Panel.fit(
            str(schedule),
            title="Agenda",
            border_style="blue"
        ))
        
        return True
    except Exception as e:
        log.error(f"Error en la programación de audiencia: {e}")
        return False

def test_notification_generation():
    """Prueba la generación de una notificación"""
    recipient = {
        "nombre": "Juan Pérez",
        "cargo": "Defensor Penal",
        "correo": "jperez@defensoria.cl",
        "direccion": "Calle Defensa 123, Santiago"
    }
    
    content = {
        "tipo_causa": "Penal",
        "rit": "1234-2024",
        "tribunal": "3° Juzgado de Garantía de Santiago",
        "materia": "Citación a audiencia de formalización",
        "fecha_audiencia": "2024-02-15 09:00",
        "sala": "Sala 3",
        "observaciones": "Traer documentación del imputado"
    }
    
    try:
        secretary = SecretaryAgent()
        notification = secretary.generate_notification(
            "Citación a audiencia",
            recipient,
            content
        )
        
        console.print("\n[bold blue]Notificación Generada:[/bold blue]")
        console.print(Panel.fit(
            str(notification),
            title="Notificación",
            border_style="blue"
        ))
        
        return True
    except Exception as e:
        log.error(f"Error en la generación de notificación: {e}")
        return False

def main():
    """Función principal de prueba"""
    console.print("\n📋 [bold blue]Iniciando pruebas del Agente Secretario[/bold blue]\n")
    
    load_dotenv()
    
    if not os.getenv("DEEPSEEK_API_KEY"):
        log.error("DEEPSEEK_API_KEY no encontrada en variables de entorno")
        return
    
    # Ejecutar pruebas
    status_ok = test_case_status_review()
    resolution_ok = test_resolution_generation()
    hearing_ok = test_hearing_scheduling()
    notification_ok = test_notification_generation()
    
    if status_ok and resolution_ok and hearing_ok and notification_ok:
        console.print("\n✨ [bold green]Pruebas del Agente Secretario completadas con éxito[/bold green] ✨\n")
    else:
        console.print("\n❌ [bold red]Algunas pruebas fallaron[/bold red]\n")

if __name__ == "__main__":
    main()
