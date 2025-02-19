import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.integrations.gather_integration import GatherIntegration, GatherIntegrationError
from rich.console import Console
from rich.panel import Panel
import json
import requests

def verify_api_key(api_key: str) -> bool:
    """
    Verify the Gather API key by making requests to different endpoints
    
    Args:
        api_key (str): API key to verify
    
    Returns:
        bool: True if API key is valid, False otherwise
    """
    # List of potential API endpoints to try
    endpoints = [
        "https://api.gather.town/api/v2/spaces",
        "https://gather.town/api/v2/spaces",
        "https://api.gather.town/api/getEmailGuestlist"
    ]

    for endpoint in endpoints:
        try:
            print(f"Trying endpoint: {endpoint}")
            response = requests.get(
                endpoint, 
                headers={"apiKey": api_key},
                params={"spaceId": "test_space"} if "getEmailGuestlist" in endpoint else None,
                timeout=10
            )
            
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Content: {response.text}")
            
            # Check for successful responses
            if response.status_code in [200, 204]:
                return True
            
        except requests.exceptions.RequestException as e:
            print(f"Request error for {endpoint}: {e}")
    
    return False

def main():
    # Initialize console for rich output
    console = Console()

    # API Key (replace with actual key or environment variable)
    API_KEY = "d01GKxrWSon1GgzR"

    # Verify API key first
    console.print("[bold blue]Verificando API Key:[/bold blue]")
    if not verify_api_key(API_KEY):
        console.print("[red]Error: API Key inválida o no autorizada[/red]")
        return

    try:
        # Initialize Gather Integration
        gather_integration = GatherIntegration(API_KEY)

        # Test: Attempt to list spaces or perform a basic operation
        console.print("[bold blue]Realizando prueba de integración:[/bold blue]")
        
        # Attempt to get a list of spaces or perform a basic API call
        console.print("[yellow]Intentando obtener lista de espacios...[/yellow]")
        
        # Use requests directly to get more detailed error information
        response = requests.get(
            "https://api.gather.town/api/v2/spaces", 
            headers={"apiKey": API_KEY},
            timeout=10
        )
        
        # Print response details
        console.print("[bold green]Detalles de la respuesta:[/bold green]")
        console.print(Panel(json.dumps({
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": response.text
        }, indent=2, ensure_ascii=False)))

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error de conexión: {e}[/red]")
    except json.JSONDecodeError as e:
        console.print(f"[red]Error decodificando respuesta: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Error inesperado: {e}[/red]")

if __name__ == "__main__":
    main()
