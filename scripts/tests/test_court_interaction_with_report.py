"""
Script para simular y documentar la interacción entre Juez, Fiscal y Defensor
"""
import os
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv
import logging
from rich.logging import RichHandler
from datetime import datetime
import json
from pathlib import Path
from src.agents.judge import JudgeAgent
from src.agents.prosecutor import ProsecutorAgent
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

def format_json(data: dict) -> str:
    """Formatea un diccionario JSON para markdown"""
    return json.dumps(data, indent=2, ensure_ascii=False)

def generate_markdown_report(case_data: dict, interactions: list) -> str:
    """Genera el reporte en formato markdown"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    markdown = f"""# Simulación de Caso Judicial
*Generado el: {current_time}*

## Información del Caso
**RIT:** {case_data.get('rit', 'No especificado')}
**Tribunal:** {case_data.get('tribunal', 'No especificado')}
**Tipo de Causa:** {case_data.get('tipo_causa', 'No especificado')}
**Delito:** {case_data.get('delito', 'No especificado')}

### Partes Involucradas
**Víctima:** {case_data.get('victima', {}).get('nombre', 'No especificado')}
**Imputado:** {case_data.get('imputado', {}).get('nombre', 'No especificado')}

### Hechos
```json
{format_json(case_data.get('hechos', []))}
```

## Desarrollo del Caso

"""
    
    for interaction in interactions:
        markdown += f"### {interaction['title']}\n"
        if interaction.get('description'):
            markdown += f"{interaction['description']}\n\n"
        
        if interaction.get('content'):
            markdown += "```json\n"
            markdown += format_json(interaction['content'])
            markdown += "\n```\n\n"
    
    markdown += """## Conclusiones y Observaciones
1. El caso demuestra la importancia de la interacción entre los diferentes actores del sistema judicial
2. Cada agente aporta su perspectiva única y especializada al proceso
3. La documentación detallada permite un seguimiento claro del desarrollo del caso

## Próximos Pasos
1. Programar audiencia de formalización
2. Establecer plazos para la investigación
3. Coordinar la presentación de pruebas

---
*Este documento fue generado automáticamente por el sistema de simulación judicial*
"""
    
    return markdown

def simulate_criminal_case():
    """Simula un caso penal con interacción entre Juez, Fiscal y Defensor"""
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
        },
        "hechos": [
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
    
    interactions = []
    
    # Crear instancias de los agentes
    judge = JudgeAgent("Juez de Garantía")
    prosecutor = ProsecutorAgent("Fiscal")
    defender = DefenderAgent("Defensor")
    
    # 1. Fiscal investiga el caso
    console.print("\n[bold blue]1. Fiscal inicia investigación:[/bold blue]")
    investigation = prosecutor.investigate_case(case_data)
    console.print(Panel.fit(
        str(investigation),
        title="Informe de Investigación del Fiscal",
        border_style="blue"
    ))
    interactions.append({
        "title": "Investigación del Fiscal",
        "description": "El Fiscal realiza una investigación preliminar del caso, analizando los hechos y evidencias disponibles.",
        "content": investigation
    })
    
    # 2. Defensor analiza el caso
    console.print("\n[bold yellow]2. Defensor analiza el caso:[/bold yellow]")
    defense_analysis = defender.analyze_defense_case(case_data)
    console.print(Panel.fit(
        str(defense_analysis),
        title="Análisis del Defensor",
        border_style="yellow"
    ))
    interactions.append({
        "title": "Análisis del Defensor",
        "description": "El Defensor realiza un análisis preliminar del caso desde la perspectiva de la defensa.",
        "content": defense_analysis
    })
    
    # 3. Juez analiza el caso
    console.print("\n[bold green]3. Juez analiza el caso:[/bold green]")
    judge_analysis = judge.analyze_case(case_data)
    console.print(Panel.fit(
        str(judge_analysis),
        title="Análisis del Juez",
        border_style="green"
    ))
    interactions.append({
        "title": "Análisis del Juez",
        "description": "El Juez realiza un análisis inicial del caso, evaluando los aspectos legales y procesales.",
        "content": judge_analysis
    })
    
    # 4. Fiscal formula acusación
    console.print("\n[bold blue]4. Fiscal formula acusación:[/bold blue]")
    accusation = prosecutor.formulate_accusation(case_data)
    console.print(Panel.fit(
        str(accusation),
        title="Acusación del Fiscal",
        border_style="blue"
    ))
    interactions.append({
        "title": "Acusación del Fiscal",
        "description": "El Fiscal presenta su acusación formal basada en la investigación realizada.",
        "content": accusation
    })
    
    # 5. Defensor prepara defensa
    console.print("\n[bold yellow]5. Defensor prepara defensa:[/bold yellow]")
    defense = defender.prepare_defense(case_data, accusation)
    console.print(Panel.fit(
        str(defense),
        title="Defensa Preparada",
        border_style="yellow"
    ))
    interactions.append({
        "title": "Preparación de la Defensa",
        "description": "El Defensor prepara su estrategia de defensa en respuesta a la acusación fiscal.",
        "content": defense
    })
    
    # 6. Juez evalúa evidencias
    console.print("\n[bold green]6. Juez evalúa evidencias:[/bold green]")
    evidence_review = judge.review_evidence(case_data.get("evidencias", []))
    console.print(Panel.fit(
        str(evidence_review),
        title="Evaluación de Evidencias por el Juez",
        border_style="green"
    ))
    interactions.append({
        "title": "Evaluación de Evidencias",
        "description": "El Juez realiza una evaluación de las evidencias presentadas por ambas partes.",
        "content": evidence_review
    })
    
    # 7. Juez emite resolución
    console.print("\n[bold green]7. Juez emite resolución:[/bold green]")
    resolution = judge.issue_resolution(case_data["rit"], {
        "caso": case_data,
        "investigacion": investigation,
        "acusacion": accusation,
        "defensa": defense,
        "evidencias": evidence_review
    })
    console.print(Panel.fit(
        str(resolution),
        title="Resolución del Juez",
        border_style="green"
    ))
    interactions.append({
        "title": "Resolución Judicial",
        "description": "El Juez emite su resolución considerando todos los elementos presentados.",
        "content": resolution
    })
    
    # Generar reporte markdown
    markdown_content = generate_markdown_report(case_data, interactions)
    
    # Crear directorio de reportes si no existe
    reports_dir = Path("docs/reportes_casos")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Guardar reporte
    report_path = reports_dir / f"caso_{case_data['rit'].replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_path.write_text(markdown_content, encoding='utf-8')
    
    console.print(f"\n[bold green]Reporte guardado en: {report_path}[/bold green]")
    
    return report_path

def main():
    """Función principal"""
    console.print("\n🏛️  [bold]Simulación de Caso Judicial[/bold]\n")
    
    load_dotenv()
    
    if not os.getenv("DEEPSEEK_API_KEY"):
        log.error("DEEPSEEK_API_KEY no encontrada en variables de entorno")
        return
    
    try:
        report_path = simulate_criminal_case()
        console.print("\n✨ [bold green]Simulación completada con éxito[/bold green] ✨\n")
        console.print(f"📝 Reporte generado en: {report_path}\n")
    except Exception as e:
        log.error(f"Error en la simulación: {e}")
        console.print("\n❌ [bold red]Error en la simulación[/bold red]\n")

if __name__ == "__main__":
    main()
