"""
Script para probar la comunicación entre agentes judiciales
"""
import os
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv
import logging
from rich.logging import RichHandler
from datetime import datetime
from src.agents.judge import JudgeAgent
from src.agents.prosecutor import ProsecutorAgent
from src.agents.defender import DefenderAgent
from src.agents.secretary import SecretaryAgent
from src.agents.core.messaging import MessageType, MessagePriority

# Configurar logging
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger("rich")
console = Console()

def test_agent_communication():
    """Prueba la comunicación entre agentes"""
    # Caso de prueba
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
        }
    }
    
    console.print("[bold]Iniciando prueba de comunicación entre agentes judiciales[/bold]")
    
    # Crear instancias de los agentes
    judge = JudgeAgent("Juez de Garantía")
    prosecutor = ProsecutorAgent("Fiscal")
    defender = DefenderAgent("Defensor")
    secretary = SecretaryAgent("Secretario")
    
    # Suscribir agentes para recibir notificaciones
    prosecutor.subscribe_to(judge.agent_id)
    defender.subscribe_to(judge.agent_id)
    secretary.subscribe_to(judge.agent_id)
    
    judge.subscribe_to(prosecutor.agent_id)
    defender.subscribe_to(prosecutor.agent_id)
    secretary.subscribe_to(prosecutor.agent_id)
    
    judge.subscribe_to(defender.agent_id)
    prosecutor.subscribe_to(defender.agent_id)
    secretary.subscribe_to(defender.agent_id)
    
    judge.subscribe_to(secretary.agent_id)
    prosecutor.subscribe_to(secretary.agent_id)
    defender.subscribe_to(secretary.agent_id)
    
    # 1. Fiscal solicita información al Juez
    console.print("\n[bold blue]1. Fiscal solicita información al Juez:[/bold blue]")
    prosecutor.request_information(
        receiver=judge.agent_id,
        subject="Solicitud de antecedentes previos",
        content={
            "tipo_solicitud": "antecedentes_previos",
            "imputado": case_data["imputado"],
            "motivo": "Evaluación de reincidencia"
        },
        priority=MessagePriority.HIGH
    )
    
    # Procesar mensajes del Juez
    judge.process_messages()
    
    # 2. Defensor solicita acceso a expediente
    console.print("\n[bold yellow]2. Defensor solicita acceso a expediente:[/bold yellow]")
    defender.request_information(
        receiver=secretary.agent_id,
        subject="Solicitud de acceso a expediente",
        content={
            "tipo_solicitud": "acceso_expediente",
            "rit": case_data["rit"],
            "motivo": "Preparación de defensa"
        }
    )
    
    # Procesar mensajes del Secretario
    secretary.process_messages()
    
    # 3. Juez emite decisión sobre prisión preventiva
    console.print("\n[bold green]3. Juez emite decisión sobre prisión preventiva:[/bold green]")
    judge.communicate_decision(
        receivers=[prosecutor.agent_id, defender.agent_id, secretary.agent_id],
        subject="Resolución sobre prisión preventiva",
        content={
            "tipo_decision": "prision_preventiva",
            "resultado": "rechazada",
            "fundamentos": [
                "No existen antecedentes suficientes que justifiquen la medida",
                "El imputado tiene arraigo familiar y laboral",
                "Los delitos anteriores son de menor gravedad"
            ],
            "medidas_cautelares": [
                "Firma mensual",
                "Prohibición de salir del país"
            ]
        }
    )
    
    # Procesar mensajes de todos los agentes
    prosecutor.process_messages()
    defender.process_messages()
    secretary.process_messages()
    
    # 4. Secretario notifica programación de audiencia
    console.print("\n[bold cyan]4. Secretario notifica programación de audiencia:[/bold cyan]")
    secretary.notify_update(
        receivers=[judge.agent_id, prosecutor.agent_id, defender.agent_id],
        subject="Programación de audiencia de formalización",
        content={
            "tipo_audiencia": "formalización",
            "fecha": "2024-02-15",
            "hora": "10:00",
            "sala": "Sala 3",
            "participantes_requeridos": [
                "Juez de Garantía",
                "Fiscal",
                "Defensor",
                "Imputado"
            ]
        }
    )
    
    # Procesar mensajes de todos los agentes
    judge.process_messages()
    prosecutor.process_messages()
    defender.process_messages()
    
    # 5. Fiscal notifica nuevos antecedentes
    console.print("\n[bold blue]5. Fiscal notifica nuevos antecedentes:[/bold blue]")
    prosecutor.notify_update(
        receivers=[judge.agent_id, defender.agent_id, secretary.agent_id],
        subject="Nuevos antecedentes probatorios",
        content={
            "tipo_antecedente": "informe_pericial",
            "descripcion": "Análisis de huellas dactilares en el sitio del suceso",
            "resultado": "No se encontraron coincidencias con el imputado",
            "fecha_informe": "2024-02-13"
        },
        priority=MessagePriority.HIGH
    )
    
    # Procesar mensajes de todos los agentes
    judge.process_messages()
    defender.process_messages()
    secretary.process_messages()
    
    console.print("\n✨ [bold green]Prueba de comunicación completada[/bold green] ✨\n")

def main():
    """Función principal"""
    console.print("\n📨 [bold]Prueba de Comunicación entre Agentes Judiciales[/bold]\n")
    
    load_dotenv()
    
    if not os.getenv("DEEPSEEK_API_KEY"):
        log.error("DEEPSEEK_API_KEY no encontrada en variables de entorno")
        return
    
    try:
        test_agent_communication()
    except Exception as e:
        log.error(f"Error en la prueba de comunicación: {e}")
        console.print("\n❌ [bold red]Error en la prueba[/bold red]\n")

if __name__ == "__main__":
    main()
