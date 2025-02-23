"""
Script para probar el Agente Secretario con un caso real
"""
from src.agents.secretary import SecretaryAgent
from rich.console import Console
from rich.panel import Panel
import json
from datetime import datetime, timedelta

console = Console()

def main():
    # Crear instancia del secretario
    secretary = SecretaryAgent()
    
    # Caso de prueba
    test_case = {
        "id": "CASO-2025-001",
        "tipo": "Penal",
        "materia": "Estafa",
        "fecha_ingreso": datetime.now().isoformat(),
        "estado": "En Proceso",
        "partes": {
            "denunciante": {
                "nombre": "María González",
                "rut": "15.432.109-8",
                "domicilio": "Los Alerces 567, Ñuñoa",
                "email": "maria.gonzalez@email.com",
                "telefono": "+56 9 8765 4321"
            },
            "denunciado": {
                "nombre": "Inversiones Rápidas SpA",
                "rut": "76.789.012-3",
                "domicilio": "Apoquindo 4567, Of. 1201, Las Condes",
                "representante_legal": "Carlos Martínez Silva",
                "rut_representante": "9.876.543-2"
            }
        },
        "actuaciones": [
            {
                "tipo": "Ingreso Denuncia",
                "fecha": (datetime.now() - timedelta(days=5)).isoformat(),
                "estado": "Completado"
            },
            {
                "tipo": "Análisis Fiscal",
                "fecha": (datetime.now() - timedelta(days=3)).isoformat(),
                "estado": "Completado",
                "documento": "informe_fiscal.pdf"
            },
            {
                "tipo": "Resolución Judicial",
                "fecha": (datetime.now() - timedelta(days=2)).isoformat(),
                "estado": "Completado",
                "documento": "resolucion_inicial.pdf"
            },
            {
                "tipo": "Notificación Partes",
                "fecha": (datetime.now() - timedelta(days=1)).isoformat(),
                "estado": "Pendiente"
            },
            {
                "tipo": "Audiencia Inicial",
                "fecha": (datetime.now() + timedelta(days=5)).isoformat(),
                "estado": "Programado",
                "sala": "Sala 3",
                "hora": "09:30"
            }
        ],
        "documentos": [
            {
                "tipo": "Denuncia",
                "nombre": "denuncia_original.pdf",
                "fecha": (datetime.now() - timedelta(days=5)).isoformat(),
                "estado": "Procesado"
            },
            {
                "tipo": "Evidencia",
                "nombre": "contrato_inversion.pdf",
                "fecha": (datetime.now() - timedelta(days=5)).isoformat(),
                "estado": "Procesado"
            },
            {
                "tipo": "Evidencia",
                "nombre": "comprobantes_transferencias.pdf",
                "fecha": (datetime.now() - timedelta(days=5)).isoformat(),
                "estado": "Procesado"
            },
            {
                "tipo": "Informe",
                "nombre": "informe_fiscal.pdf",
                "fecha": (datetime.now() - timedelta(days=3)).isoformat(),
                "estado": "Pendiente Notificación"
            },
            {
                "tipo": "Resolución",
                "nombre": "resolucion_inicial.pdf",
                "fecha": (datetime.now() - timedelta(days=2)).isoformat(),
                "estado": "Pendiente Notificación"
            }
        ],
        "notificaciones_pendientes": [
            {
                "destinatario": "María González",
                "tipo": "Resolución Judicial",
                "documento": "resolucion_inicial.pdf",
                "medio": "Email",
                "prioridad": "Alta"
            },
            {
                "destinatario": "Inversiones Rápidas SpA",
                "tipo": "Resolución Judicial",
                "documento": "resolucion_inicial.pdf",
                "medio": "Oficio",
                "prioridad": "Alta"
            }
        ],
        "agenda": [
            {
                "tipo": "Audiencia Inicial",
                "fecha": (datetime.now() + timedelta(days=5)).isoformat(),
                "hora": "09:30",
                "sala": "Sala 3",
                "participantes": [
                    "Juez",
                    "Fiscal",
                    "Defensor",
                    "María González",
                    "Carlos Martínez Silva"
                ],
                "estado": "Confirmación Pendiente"
            }
        ]
    }
    
    console.print("\n[bold blue]Iniciando análisis del caso...[/bold blue]")
    
    try:
        # Analizar el caso
        analysis = secretary.analyze_case(test_case)
        
        # Si analysis es un string, parsearlo como JSON
        if isinstance(analysis, str):
            analysis_dict = json.loads(analysis)
        else:
            analysis_dict = analysis

        # Formatear el JSON para mostrarlo
        formatted_json = json.dumps(analysis_dict, indent=2, ensure_ascii=False)
        
        # Mostrar resultados
        console.print("\n[bold green]Análisis completado:[/bold green]")
        console.print(Panel(
            formatted_json,
            title="Evaluación del Secretario",
            border_style="green",
            width=100
        ))
        
    except Exception as e:
        console.print("\n[bold red]Error durante el análisis:[/bold red]")
        console.print(Panel(str(e), border_style="red"))

if __name__ == "__main__":
    main()
