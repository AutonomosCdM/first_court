"""
Script para probar el Agente Defensor con un caso real
"""
from src.agents.defender import DefenderAgent
from rich.console import Console
from rich.panel import Panel
import json
from datetime import datetime

console = Console()

def main():
    # Crear instancia del defensor
    defender = DefenderAgent()
    
    # Caso de prueba
    test_case = {
        "id": "CASO-2025-001",
        "tipo": "Penal",
        "materia": "Estafa",
        "fecha_ingreso": datetime.now().isoformat(),
        "partes": {
            "denunciante": {
                "nombre": "María González",
                "rut": "15.432.109-8",
                "domicilio": "Los Alerces 567, Ñuñoa"
            },
            "denunciado": {
                "nombre": "Inversiones Rápidas SpA",
                "rut": "76.789.012-3",
                "domicilio": "Apoquindo 4567, Of. 1201, Las Condes",
                "representante_legal": "Carlos Martínez Silva",
                "rut_representante": "9.876.543-2"
            }
        },
        "hechos": [
            "La denunciante invirtió $15.000.000 CLP en un esquema de inversión prometido por la empresa",
            "Se le prometió un retorno del 20% mensual",
            "Después de 3 meses sin recibir pagos, la empresa dejó de responder",
            "La oficina física está cerrada y el sitio web fue dado de baja",
            "Hay al menos 10 denuncias similares en redes sociales"
        ],
        "evidencias": [
            "Contrato de inversión firmado",
            "Comprobantes de transferencias bancarias",
            "Capturas de pantalla del sitio web (antes de ser dado de baja)",
            "Correos electrónicos con promesas de rentabilidad",
            "Mensajes de WhatsApp con representantes de la empresa",
            "Testimonios de otros afectados en redes sociales"
        ],
        "diligencias_realizadas": [
            "Verificación del domicilio comercial",
            "Consulta de antecedentes comerciales",
            "Recopilación de denuncias similares"
        ],
        "informe_fiscal": {
            "calificacion_preliminar": "Posible delito de estafa y apropiación indebida",
            "gravedad": "Alta",
            "riesgo_fuga": "Alto",
            "recomendaciones": [
                "Orden de detención preventiva",
                "Congelamiento de cuentas bancarias",
                "Prohibición de salida del país"
            ]
        },
        "resolucion_juez": {
            "evaluacion_preliminar": "El caso presenta indicios de un delito de estafa",
            "puntos_clave": [
                "Indicios de delito de estafa",
                "Gravedad del delito",
                "Riesgo de fuga"
            ],
            "pasos_procesales": [
                "Orden de detención preventiva",
                "Congelamiento de cuentas bancarias",
                "Prohibición de salida del país"
            ],
            "complejidades": [
                "Identificación y localización de los responsables",
                "Recuperación de los activos robados",
                "Demostración de la intención fraudulenta de la empresa"
            ]
        }
    }
    
    console.print("\n[bold blue]Iniciando análisis del caso...[/bold blue]")
    
    try:
        # Analizar el caso
        analysis = defender.analyze_case(test_case)
        
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
            title="Evaluación del Defensor",
            border_style="green",
            width=100
        ))
        
    except Exception as e:
        console.print("\n[bold red]Error durante el análisis:[/bold red]")
        console.print(Panel(str(e), border_style="red"))

if __name__ == "__main__":
    main()
