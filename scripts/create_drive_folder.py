"""
Script para crear la estructura de carpetas en Google Drive
"""
from src.auth.oauth_client import OAuth2Client

def main():
    """Función principal"""
    print("\n=== Creando estructura de carpetas en Drive ===\n")
    
    # Obtener cliente
    client = OAuth2Client()
    drive_service = client.drive
    
    try:
        # Crear carpeta principal
        file_metadata = {
            'name': 'Documentos Judiciales',
            'mimeType': 'application/vnd.google-apps.folder',
            'description': 'Carpeta principal para documentos judiciales del Tribunal Autónomo'
        }
        
        folder = drive_service.files().create(
            body=file_metadata,
            fields='id, name, webViewLink'
        ).execute()
        
        folder_id = folder['id']
        folder_url = folder['webViewLink']
        
        print(f"✓ Carpeta creada exitosamente:")
        print(f"  - Nombre: {folder['name']}")
        print(f"  - ID: {folder_id}")
        print(f"  - URL: {folder_url}")
        
        # Crear subcarpetas
        subcarpetas = [
            'Actas de Audiencia',
            'Resoluciones',
            'Notificaciones',
            'Otros Documentos'
        ]
        
        print("\nCreando subcarpetas:")
        
        for subcarpeta in subcarpetas:
            subfolder_metadata = {
                'name': subcarpeta,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [folder_id]
            }
            
            subfolder = drive_service.files().create(
                body=subfolder_metadata,
                fields='id, name, webViewLink'
            ).execute()
            
            print(f"\n✓ Subcarpeta creada:")
            print(f"  - Nombre: {subfolder['name']}")
            print(f"  - ID: {subfolder['id']}")
            print(f"  - URL: {subfolder['webViewLink']}")
        
        print("\n=== Estructura de carpetas creada exitosamente ===")
        
    except Exception as e:
        print(f"\n⚠ Error al crear carpetas: {str(e)}")

if __name__ == '__main__':
    main()
