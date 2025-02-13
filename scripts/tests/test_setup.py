"""
Script de prueba inicial para verificar la configuración del sistema
"""
import os
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv
import logging
from rich.logging import RichHandler

# Configurar logging
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger("rich")
console = Console()

def check_environment():
    """Verifica la configuración del entorno"""
    console.print(Panel.fit(
        "Verificando configuración del sistema",
        border_style="blue"
    ))
    
    # Verificar .env
    load_dotenv()
    required_vars = [
        "ENV",
        "LOG_LEVEL",
        "LLM_PROVIDER"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        log.error(f"Variables de entorno faltantes: {', '.join(missing_vars)}")
        return False
    
    log.info("✅ Variables de entorno configuradas correctamente")
    return True

def check_imports():
    """Verifica las importaciones principales"""
    try:
        import langchain
        import chromadb
        import pydantic
        
        log.info("✅ Dependencias principales importadas correctamente")
        return True
    except ImportError as e:
        log.error(f"Error importando dependencias: {e}")
        return False

def main():
    """Función principal de prueba"""
    console.print("\n🔍 [bold blue]Iniciando verificación del sistema[/bold blue]\n")
    
    # Verificar entorno
    env_ok = check_environment()
    
    # Verificar importaciones
    imports_ok = check_imports()
    
    if env_ok and imports_ok:
        console.print("\n✨ [bold green]Sistema configurado correctamente[/bold green] ✨\n")
    else:
        console.print("\n❌ [bold red]Se encontraron errores en la configuración[/bold red]\n")

if __name__ == "__main__":
    main()
