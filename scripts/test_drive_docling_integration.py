import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.secretary import SecretaryAgent
from rich.console import Console
from rich.panel import Panel
import json

def main():
    # Initialize console for rich output
    console = Console()

    # Create Secretary Agent with Drive integration
    secretary = SecretaryAgent()

    # Folder ID from the shared link
    folder_id = "1fagq1gTX0E0v0g9AZ2e245t0vg8T3YIk"

    console.print("[bold blue]Listando documentos en la carpeta de Drive:[/bold blue]")
    drive_documents = secretary.list_drive_documents(folder_id)
    
    console.print(Panel(json.dumps(drive_documents, indent=2, ensure_ascii=False)))

    console.print("\n[bold blue]Procesando documentos de Drive:[/bold blue]")
    processed_docs = secretary.process_drive_documents(folder_id)
    
    console.print(Panel(json.dumps(processed_docs, indent=2, ensure_ascii=False)))

    console.print("\n[bold blue]Generando resumen de documentos:[/bold blue]")
    document_summary = secretary.generate_drive_document_summary(folder_id)
    
    console.print(Panel(json.dumps(document_summary, indent=2, ensure_ascii=False)))

if __name__ == "__main__":
    main()
