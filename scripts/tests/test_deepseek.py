"""
Script de prueba para la conexión con Deepseek
"""
import os
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv
import logging
from rich.logging import RichHandler
from src.llm.providers.deepseek_custom import DeepseekClient

# Configurar logging
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger("rich")
console = Console()

def test_deepseek_connection():
    """Prueba la conexión con Deepseek"""
    try:
        client = DeepseekClient(api_key=os.getenv("DEEPSEEK_API_KEY"))
        prompt = "Por favor, explica brevemente el rol de un juez en el sistema judicial chileno."
        
        response = client.generate(prompt)
        console.print(Panel(response, title="Respuesta de Deepseek", border_style="green"))
        return True
    except Exception as e:
        log.error(f"Error conectando con Deepseek: {e}")
        return False

def main():
    """Función principal de prueba"""
    console.print("\n🔍 [bold blue]Probando conexión con Deepseek[/bold blue]\n")
    
    load_dotenv()
    
    if not os.getenv("DEEPSEEK_API_KEY"):
        log.error("DEEPSEEK_API_KEY no encontrada en variables de entorno")
        return
    
    if test_deepseek_connection():
        console.print("\n✨ [bold green]Conexión con Deepseek exitosa[/bold green] ✨\n")
    else:
        console.print("\n❌ [bold red]Error conectando con Deepseek[/bold red]\n")

if __name__ == "__main__":
    main()
