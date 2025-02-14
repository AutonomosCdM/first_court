"""
Script para verificar la autenticación y regenerar el token si es necesario
"""
from src.auth.oauth_client import OAuth2Client
import os

def main():
    """Función principal de verificación"""
    print("\n=== Verificando autenticación de Google APIs ===\n")
    
    client = OAuth2Client()
    
    # Verificar scopes
    if not client.verify_scopes():
        print("⚠ El token actual no tiene todos los scopes necesarios")
        print("Regenerando token...")
        client.refresh_token()
        print("✓ Token regenerado con todos los scopes necesarios")
    else:
        print("✓ Token actual tiene todos los scopes necesarios")
    
    # Probar cada servicio
    services = [
        ('Calendar', client.calendar),
        ('Drive', client.drive),
        ('Docs', client.docs),
        ('Gmail', client.gmail)
    ]
    
    print("\nVerificando acceso a servicios:")
    
    for name, service in services:
        try:
            if name == 'Calendar':
                service.calendarList().list().execute()
            elif name == 'Drive':
                service.files().list().execute()
            elif name == 'Docs':
                # Para Docs API, intentamos obtener un documento
                service.documents().get(documentId='1XDTzWTakpl66WLUyrKum81BjWUUgQAfXolrYLc-SjY4').execute()
            elif name == 'Gmail':
                service.users().getProfile(userId='me').execute()
                
            print(f"✓ {name}: Acceso verificado")
        except Exception as e:
            print(f"⚠ {name}: Error de acceso - {str(e)}")
    
    print("\n=== Verificación completada ===")

if __name__ == '__main__':
    main()
