"""
Configuración centralizada de scopes de OAuth2 para todas las APIs de Google
"""

# Todos los scopes necesarios para el sistema completo
ALL_SCOPES = [
    # Calendar y Meet
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
    
    # Drive y Docs
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/documents',
    
    # Gmail
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
]

# Función para obtener todos los scopes
def get_all_scopes():
    """Retorna la lista completa de scopes necesarios"""
    return ALL_SCOPES

# Función para verificar si un token tiene todos los scopes necesarios
def has_required_scopes(credentials):
    """Verifica si las credenciales tienen todos los scopes necesarios"""
    if not credentials or not credentials.scopes:
        return False
    
    return all(scope in credentials.scopes for scope in ALL_SCOPES)
