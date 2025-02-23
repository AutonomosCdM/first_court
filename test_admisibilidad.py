"""
Script para probar la interacción de admisibilidad y resolución
"""
from src.agents.judge import JudgeAgent
from src.agents.prosecutor import ProsecutorAgent
from src.agents.defender import DefenderAgent
from src.agents.secretary import SecretaryAgent
from rich.console import Console
from rich.panel import Panel
import json
from datetime import datetime
import os
import time

console = Console()

def save_resolution(case_id: str, resolution_data: dict):
    """Guarda la resolución en un archivo"""
    resolution_file = f"resolucion_{case_id}.md"
    with open(resolution_file, 'w', encoding='utf-8') as f:
        f.write(f"# Resolución - Caso {case_id}\n\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Escribir el análisis completo
        f.write("## Análisis del Caso\n\n")
        f.write("```json\n")
        f.write(json.dumps(resolution_data, indent=2, ensure_ascii=False))
        f.write("\n```\n\n")

def extract_key_info(content: str) -> dict:
    """Extrae información clave del contenido de la querella"""
    # Extraer los hechos
    hechos_start = content.find("I Hechos")
    hechos_end = content.find("II", hechos_start)
    hechos = content[hechos_start:hechos_end].strip() if hechos_start >= 0 and hechos_end >= 0 else ""
    
    # Extraer el derecho
    derecho_start = content.find("II")
    derecho_end = content.find("III", derecho_start)
    derecho = content[derecho_start:derecho_end].strip() if derecho_start >= 0 and derecho_end >= 0 else ""
    
    # Extraer diligencias
    diligencias_start = content.find("III. Diligencias")
    diligencias_end = content.find("POR TANTO", diligencias_start)
    diligencias = content[diligencias_start:diligencias_end].strip() if diligencias_start >= 0 and diligencias_end >= 0 else ""
    
    return {
        "hechos": hechos,
        "derecho": derecho,
        "diligencias": diligencias
    }

def process_agent_response(response):
    """Procesa la respuesta de un agente y la convierte en un formato consistente"""
    if isinstance(response, str):
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response"}
    return response

def main():
    # Crear instancias de los agentes
    judge = JudgeAgent()
    prosecutor = ProsecutorAgent()
    defender = DefenderAgent()
    secretary = SecretaryAgent()
    
    # Leer el contenido de la querella
    with open("ejmplo.md", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraer información clave
    key_info = extract_key_info(content)
    
    # Preparar el caso base
    base_case = {
        "id": "CASO-2025-002",
        "tipo": "Penal",
        "materia": "Estafa",
        "fecha_ingreso": datetime.now().isoformat(),
        "estado": "En Revisión de Admisibilidad",
        "resumen": key_info,
        "partes": {
            "querellantes": [
                "VÍCTOR IGNACIO AGÜERO NEIPÁN",
                "DANIEL YSAY ANABALÓN OJEDA",
                "BELÉN ALEJANDRA ARANEDA MAILLANCA",
                "BRENDA MAKARENA BUSTOS BARRIENTOS",
                "KARLA BELÉN CATALÁN PAREDES",
                "YAMILET YASMIN GALLARDO RUDOLPH",
                "MABEL ISAMAR HUENTEQUEO HUENTEQUEO",
                "MARÍA JOSÉ MELLADO FLORES",
                "VÍCTOR ABRAHAM MOLINA PEÑA"
            ],
            "querellados": [
                "CLAUDIO ROSAMEL LAVADO CASTRO",
                "JORGE PAREDES MÉNDEZ",
                "RODRIGO BUSTOS CASTILLO",
                "GABRIEL ALEJANDRO CARRILLO VARELA"
            ]
        },
        "delitos": ["Estafa"],
        "lugar": "Llifén, comuna de Futrono",
        "fecha_hechos": "2018-12-01"
    }
    
    console.print("\n[bold blue]Iniciando análisis de admisibilidad...[/bold blue]")
    
    try:
        # 1. Secretario revisa el caso
        console.print("\n[bold cyan]Secretario revisando el caso...[/bold cyan]")
        secretary_analysis = process_agent_response(secretary.analyze_case(base_case))
        console.print(Panel(json.dumps(secretary_analysis, indent=2, ensure_ascii=False), title="Análisis del Secretario", border_style="cyan"))
        
        # Esperar 3 segundos entre llamadas
        console.print("\n[bold yellow]Esperando 3 segundos entre llamadas...[/bold yellow]")
        time.sleep(3)
        
        # 2. Fiscal analiza el caso
        console.print("\n[bold red]Fiscal analizando el caso...[/bold red]")
        base_case["analisis_secretario"] = secretary_analysis
        prosecutor_analysis = process_agent_response(prosecutor.analyze_case(base_case))
        console.print(Panel(json.dumps(prosecutor_analysis, indent=2, ensure_ascii=False), title="Análisis del Fiscal", border_style="red"))
        
        # Esperar 3 segundos entre llamadas
        console.print("\n[bold yellow]Esperando 3 segundos entre llamadas...[/bold yellow]")
        time.sleep(3)
        
        # 3. Defensor analiza el caso
        console.print("\n[bold green]Defensor analizando el caso...[/bold green]")
        base_case["analisis_fiscal"] = prosecutor_analysis
        defender_analysis = process_agent_response(defender.analyze_case(base_case))
        console.print(Panel(json.dumps(defender_analysis, indent=2, ensure_ascii=False), title="Análisis del Defensor", border_style="green"))
        
        # Esperar 3 segundos entre llamadas
        console.print("\n[bold yellow]Esperando 3 segundos entre llamadas...[/bold yellow]")
        time.sleep(3)
        
        # 4. Juez analiza todo y decide
        console.print("\n[bold yellow]Juez analizando el caso...[/bold yellow]")
        base_case["analisis_defensor"] = defender_analysis
        resolution = process_agent_response(judge.analyze_case(base_case))
        console.print(Panel(json.dumps(resolution, indent=2, ensure_ascii=False), title="Resolución del Juez", border_style="yellow"))
        
        # Guardar la resolución
        save_resolution(base_case["id"], resolution)
        
        console.print("\n[bold green]Resolución generada correctamente.[/bold green]")
        
    except Exception as e:
        console.print("\n[bold red]Error durante el procesamiento:[/bold red]")
        console.print(Panel(str(e), border_style="red"))

if __name__ == "__main__":
    main()
