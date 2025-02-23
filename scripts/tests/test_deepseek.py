"""
Script de prueba para la conexión con Deepseek y validación de instrucciones
"""
import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
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

def test_deepseek_basic():
    """Prueba básica de conexión con Deepseek"""
    try:
        client = DeepseekClient(api_key=os.getenv("DEEPSEEK_API_KEY"))
        prompt = "Por favor, explica brevemente el rol de un juez en el sistema judicial chileno."
        
        response = client.generate(prompt)
        console.print(Panel(response, title="Respuesta Básica", border_style="green"))
        return True
    except Exception as e:
        log.error(f"""
        ❌ Error en prueba básica:
        Tipo de error: {type(e).__name__}
        Mensaje: {str(e)}
        
        Esto podría deberse a:
        - Problemas de conexión con la API
        - API key inválida
        - Rate limiting
        - Timeout en la respuesta
        
        Por favor, verifique su conexión y la validez de la API key.
        """)
        return False

def test_role_specific_instructions():
    """Prueba instrucciones específicas por rol"""
    try:
        client = DeepseekClient(api_key=os.getenv("DEEPSEEK_API_KEY"))
        
        # Prueba con rol de juez
        response_juez = client.generate(
            "¿Cómo evaluarías la admisibilidad de una querella?",
            role="juez",
            temperature=0.1
        )
        console.print(Panel(response_juez, title="Respuesta como Juez", border_style="blue"))
        
        # Prueba con rol de secretario
        response_secretario = client.generate(
            "¿Qué documentos son necesarios para presentar una querella?",
            role="secretario",
            temperature=0.1
        )
        console.print(Panel(response_secretario, title="Respuesta como Secretario", border_style="cyan"))
        
        return True
    except Exception as e:
        log.error(f"""
        ❌ Error en prueba de roles:
        Tipo de error: {type(e).__name__}
        Mensaje: {str(e)}
        
        Esto podría deberse a:
        - Problemas con el formato de las instrucciones
        - Error en la respuesta del modelo
        - Timeout en la respuesta
        
        Revise los logs para más detalles.
        """)
        return False

def test_context_handling():
    """Prueba el manejo de contexto y memoria"""
    try:
        client = DeepseekClient(api_key=os.getenv("DEEPSEEK_API_KEY"))
        
        # Contexto inicial
        context = """
        Caso en curso: Querella por estafa.
        Monto involucrado: $5,000,000 CLP
        Estado: En evaluación de admisibilidad
        """
        
        # Primera pregunta con contexto
        response1 = client.generate(
            "¿Qué aspectos debo evaluar primero?",
            role="juez",
            context=context,
            temperature=0.1
        )
        console.print(Panel(response1, title="Primera Respuesta con Contexto", border_style="yellow"))
        
        # Segunda pregunta (debería mantener contexto)
        response2 = client.generate(
            "¿Qué documentos adicionales podrían ser necesarios?",
            role="juez",
            temperature=0.1
        )
        console.print(Panel(response2, title="Segunda Respuesta (Contexto Mantenido)", border_style="yellow"))
        
        return True
    except Exception as e:
        log.error(f"""
        ❌ Error en prueba de contexto:
        Tipo de error: {type(e).__name__}
        Mensaje: {str(e)}
        
        Esto podría deberse a:
        - Problemas con el manejo de contexto
        - Error en el formato del contexto
        - Límite de tokens excedido
        
        Revise la estructura del contexto y los límites del modelo.
        """)
        return False

def test_repetition_handling():
    """Prueba la detección y manejo de repeticiones"""
    try:
        client = DeepseekClient(api_key=os.getenv("DEEPSEEK_API_KEY"))
        
        # Forzar una situación que podría causar repetición
        for _ in range(3):
            response = client.generate(
                "Explica el proceso de admisibilidad.",
                role="juez",
                temperature=0.1
            )
            console.print(Panel(response, title="Respuesta (Prueba Repetición)", border_style="magenta"))
        
        return True
    except Exception as e:
        log.error(f"""
        ❌ Error en prueba de repetición:
        Tipo de error: {type(e).__name__}
        Mensaje: {str(e)}
        
        Esto podría deberse a:
        - Problemas con la detección de repeticiones
        - Error en el manejo de la conversación
        - Timeout en respuestas múltiples
        
        Verifique los parámetros de similitud y el manejo de la conversación.
        """)
        return False

def main():
    """Función principal de pruebas"""
    console.print("\n🔍 [bold blue]Iniciando pruebas de Deepseek[/bold blue]\n")
    
    # Intentar cargar variables de .env si existe
    load_dotenv(override=True)
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        log.error("""
        🔑 DEEPSEEK_API_KEY no encontrada en variables de entorno
        
        La clave puede estar en:
        1. Variables de entorno del sistema
        2. Archivo .env
        3. GitHub Secrets (necesita ser configurada localmente)
        
        Por favor, asegúrese de que la clave esté disponible en alguna de estas ubicaciones.
        """)
        return
    
    # Tabla de resultados
    table = Table(title="Resultados de Pruebas")
    table.add_column("Prueba", style="cyan")
    table.add_column("Resultado", style="green")
    
    # Ejecutar pruebas
    tests = [
        ("Conexión Básica", test_deepseek_basic),
        ("Instrucciones por Rol", test_role_specific_instructions),
        ("Manejo de Contexto", test_context_handling),
        ("Manejo de Repeticiones", test_repetition_handling)
    ]
    
    for test_name, test_func in tests:
        result = "✅ PASS" if test_func() else "❌ FAIL"
        table.add_row(test_name, result)
    
    console.print(table)
    console.print("\n✨ [bold green]Pruebas completadas[/bold green] ✨\n")

if __name__ == "__main__":
    main()
