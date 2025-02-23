"""
Script para probar la interacción entre los agentes judiciales
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

console = Console()

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

def load_case_from_file(file_path: str) -> dict:
    """Carga el contenido del archivo y lo estructura como un caso"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraer información clave
    key_info = extract_key_info(content)
    
    # Estructurar el caso
    case = {
        "id": "CASO-2025-002",
        "tipo": "Penal",
        "materia": "Estafa",
        "fecha_ingreso": datetime.now().isoformat(),
        "estado": "En Proceso",
        "resumen": {
            "hechos": key_info["hechos"],
            "derecho": key_info["derecho"],
            "diligencias": key_info["diligencias"]
        },
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
        "fecha_hechos": "2018-12-01",
        "documentos": [
            "Mandato judicial",
            "Documentos de identidad"
        ]
    }
    return case

def save_interaction_log(case_id: str, interactions: list):
    """Guarda el registro de interacciones en un archivo"""
    log_file = f"interacciones_{case_id}.md"
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"# Registro de Interacciones - Caso {case_id}\n\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for interaction in interactions:
            f.write(f"## {interaction['agente']}\n")
            f.write(f"### Análisis\n")
            f.write("```json\n")
            f.write(json.dumps(interaction['analisis'], indent=2, ensure_ascii=False))
            f.write("\n```\n\n")

def main():
    # Crear instancias de los agentes
    judge = JudgeAgent()
    prosecutor = ProsecutorAgent()
    defender = DefenderAgent()
    secretary = SecretaryAgent()
    
    # Cargar el caso desde el archivo
    case = load_case_from_file("ejmplo.md")
    
    console.print("\n[bold blue]Iniciando procesamiento del caso...[/bold blue]")
    
    interactions = []
    
    try:
        # 1. Secretario revisa el caso
        console.print("\n[bold cyan]Secretario analizando el caso...[/bold cyan]")
        secretary_analysis = secretary.analyze_case(case)
        interactions.append({
            "agente": "Secretario",
            "analisis": secretary_analysis
        })
        
        # 2. Fiscal analiza el caso
        console.print("\n[bold red]Fiscal analizando el caso...[/bold red]")
        prosecutor_analysis = prosecutor.analyze_case(case)
        interactions.append({
            "agente": "Fiscal",
            "analisis": prosecutor_analysis
        })
        
        # Actualizar el caso con el análisis fiscal
        case["informe_fiscal"] = prosecutor_analysis
        
        # 3. Defensor analiza el caso
        console.print("\n[bold green]Defensor analizando el caso...[/bold green]")
        defender_analysis = defender.analyze_case(case)
        interactions.append({
            "agente": "Defensor",
            "analisis": defender_analysis
        })
        
        # Actualizar el caso con el análisis de la defensa
        case["informe_defensa"] = defender_analysis
        
        # 4. Juez analiza el caso
        console.print("\n[bold yellow]Juez analizando el caso...[/bold yellow]")
        judge_analysis = judge.analyze_case(case)
        interactions.append({
            "agente": "Juez",
            "analisis": judge_analysis
        })
        
        # Guardar el registro de interacciones
        save_interaction_log(case["id"], interactions)
        
        console.print("\n[bold green]Procesamiento completado. Se ha generado el registro de interacciones.[/bold green]")
        
    except Exception as e:
        console.print("\n[bold red]Error durante el procesamiento:[/bold red]")
        console.print(Panel(str(e), border_style="red"))

if __name__ == "__main__":
    main()
