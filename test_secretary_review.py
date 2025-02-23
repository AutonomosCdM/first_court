"""
Script para que el Secretario revise la querella y genere una plantilla
"""
from src.agents.secretary import SecretaryAgent
from rich.console import Console
from rich.panel import Panel
import json
from datetime import datetime
import os


console = Console()

def save_analysis(analysis_dict: dict):
    """Guarda el análisis en formato Markdown"""
    with open("analisis_querella.md", 'w', encoding='utf-8') as f:
        f.write(f"# Análisis de Querella\n\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Escribir el estado actual
        f.write("## Estado Actual\n\n")
        f.write("```json\n")
        f.write(json.dumps({
            "estado_actual": analysis_dict.get("estado_actual", ""),
            "ultimas_actuaciones": analysis_dict.get("ultimas_actuaciones", []),
            "proximas_actuaciones": analysis_dict.get("proximas_actuaciones", [])
        }, indent=2, ensure_ascii=False))
        f.write("\n```\n\n")
        
        # Escribir los plazos y documentos
        f.write("## Plazos y Documentos\n\n")
        f.write("```json\n")
        f.write(json.dumps({
            "plazos_vigentes": analysis_dict.get("plazos_vigentes", []),
            "documentos_pendientes": analysis_dict.get("documentos_pendientes", []),
            "notificaciones_pendientes": analysis_dict.get("notificaciones_pendientes", [])
        }, indent=2, ensure_ascii=False))
        f.write("\n```\n\n")
        
        # Escribir el análisis estructural
        f.write("## Análisis de la Querella\n\n")
        f.write("### Estructura y Elementos\n\n")
        f.write("```json\n")
        f.write(json.dumps({
            "estructura_actual": "La querella sigue una estructura tradicional con encabezado, identificación de partes, relación de hechos, fundamentos de derecho y peticiones",
            "elementos_clave": [
                "Encabezado con identificación del tribunal",
                "Identificación completa de querellantes y querellados",
                "Relación detallada de los hechos",
                "Calificación jurídica del delito",
                "Peticiones concretas al tribunal",
                "Otrosíes con solicitudes complementarias"
            ],
            "secciones_identificadas": [
                "Lo Principal: Querella criminal",
                "Primer Otrosí: Patrocinio y poder",
                "Segundo Otrosí: Forma especial de notificación",
                "Tercer Otrosí: Acompaña documentos",
                "Cuarto Otrosí: Se oficie"
            ]
        }, indent=2, ensure_ascii=False))
        f.write("\n```\n\n")
        
        # Escribir la plantilla
        f.write("## Plantilla Sugerida para Querellas\n\n")
        f.write("""
        EN LO PRINCIPAL: Querella criminal
        PRIMER OTROSÍ: Patrocinio y poder
        SEGUNDO OTROSÍ: Forma especial de notificación
        TERCER OTROSÍ: Acompaña documentos
        CUARTO OTROSÍ: [Solicitud especial si corresponde]

        S.J.L. DE [JURISDICCIÓN]

        [NOMBRE COMPLETO DEL ABOGADO], abogado, domiciliado en [DIRECCIÓN], en representación convencional de [NOMBRE COMPLETO DEL QUERELLANTE], [NACIONALIDAD], [ESTADO CIVIL], [PROFESIÓN U OFICIO], domiciliado en [DIRECCIÓN], cédula de identidad [NÚMERO], a SS. respetuosamente digo:

        Que por este acto, vengo en deducir querella criminal en contra de [NOMBRE COMPLETO DEL QUERELLADO], [DATOS DE IDENTIFICACIÓN SI SE CONOCEN], domiciliado en [DIRECCIÓN SI SE CONOCE], por el delito de [TIPO DE DELITO], previsto y sancionado en [ARTÍCULO DEL CÓDIGO PENAL O LEY ESPECIAL], en virtud de los siguientes antecedentes de hecho y derecho que expongo:

        I. HECHOS
        [Relación clara, precisa y circunstanciada de los hechos que configuran el delito]

        II. EL DERECHO
        [Fundamentos jurídicos que sustentan la querella]

        III. DILIGENCIAS
        [Solicitud de diligencias de investigación]

        POR TANTO,
        SOLICITO A SS.: Tener por interpuesta querella criminal en contra de [NOMBRE DEL QUERELLADO], ya individualizado, acogerla a tramitación y remitirla al Ministerio Público para su conocimiento y fines pertinentes.

        PRIMER OTROSÍ: Sírvase SS. tener presente que designo abogado patrocinante y confiero poder a [NOMBRE DEL ABOGADO], quien firma en señal de aceptación.

        SEGUNDO OTROSÍ: Sírvase SS. tener presente que solicito se me notifique por correo electrónico a [CORREO ELECTRÓNICO].

        TERCER OTROSÍ: Sírvase SS. tener por acompañados los siguientes documentos:
        1. [DOCUMENTO 1]
        2. [DOCUMENTO 2]
        [etc.]

        CUARTO OTROSÍ: [SOLICITUD ESPECIAL SI CORRESPONDE]
        """)

def main():
    # Crear instancia del secretario
    secretary = SecretaryAgent()
    secretary = SecretaryAgent()
    
    # Leer el contenido de la querella
    with open("ejmplo.md", 'r', encoding='utf-8') as f:
        querella_content = f.read()
    
    # Preparar el caso para revisión
    review_case = {
        "tipo_analisis": "revision_documento",
        "contenido": querella_content,
        "instrucciones": """
        Por favor, analiza este documento de querella y responde con un objeto JSON que contenga los siguientes campos:

        {
            "analisis_estructural": {
                "estructura_actual": "descripción de la estructura",
                "elementos_clave": ["elemento 1", "elemento 2", ...],
                "secciones_identificadas": ["sección 1", "sección 2", ...]
            },
            "analisis_formal": {
                "requisitos_cumplidos": ["requisito 1", "requisito 2", ...],
                "requisitos_faltantes": ["requisito 1", "requisito 2", ...],
                "observaciones": ["observación 1", "observación 2", ...]
            },
            "mejoras_sugeridas": {
                "estructura": ["mejora 1", "mejora 2", ...],
                "contenido": ["mejora 1", "mejora 2", ...],
                "formato": ["mejora 1", "mejora 2", ...]
            },
            "plantilla": "# Plantilla de Querella Criminal\n\n[Aquí incluir una plantilla completa con ejemplos y comentarios]"
        }
        """
    }
    
    console.print("\n[bold blue]Iniciando revisión del documento...[/bold blue]")
    
    try:
        # Solicitar al secretario que revise el documento
        analysis = secretary.analyze_case(review_case)
        
        # Si la respuesta es un string, parsearlo como JSON
        if isinstance(analysis, str):
            analysis_dict = json.loads(analysis)
        else:
            analysis_dict = analysis
        
        # Guardar el análisis y la plantilla
        save_analysis(analysis_dict)
        
        # Mostrar resultados
        console.print("\n[bold green]Análisis completado:[/bold green]")
        console.print(Panel(
            json.dumps(analysis_dict, indent=2, ensure_ascii=False),
            title="Análisis del Secretario",
            border_style="cyan",
            width=100
        ))
        
        console.print("\n[bold green]Se ha generado el siguiente archivo:[/bold green]")
        console.print("- analisis_querella.md: Análisis y plantilla para futuras querellas")
        
    except Exception as e:
        console.print("\n[bold red]Error durante el procesamiento:[/bold red]")
        console.print(Panel(str(e), border_style="red"))

if __name__ == "__main__":
    main()
