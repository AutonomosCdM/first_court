"""Script para probar la integración con Google Docs."""
from src.integrations.google_docs import GoogleDocsClient

def main():
    """Función principal para probar la integración."""
    # Crear cliente
    client = GoogleDocsClient()
    
    # Crear un documento nuevo
    print("Creando documento...")
    doc = client.create_document("Documento de Prueba")
    print(f"Documento creado: {doc['name']} (ID: {doc['id']})")
    print(f"Link: {doc['webViewLink']}")
    
    # Obtener el documento
    print("\nObteniendo documento...")
    doc_info = client.get_document(doc['id'])
    print(f"Título: {doc_info['title']}")
    
    # Insertar texto
    print("\nInsertando texto...")
    client.insert_text(doc['id'], "Este es un texto de prueba.")
    
    print("\nPruebas completadas con éxito!")

if __name__ == "__main__":
    main()
