# Integraciones de First Court

## Google Workspace

### Google Docs
La integración con Google Docs permite la gestión de documentos legales y plantillas del sistema.

#### Funcionalidades Implementadas
- Creación de documentos
- Obtención de documentos por ID
- Inserción de texto
- Reemplazo de texto
- Exportación a PDF
- Uso de plantillas

#### Configuración
Las credenciales se manejan a través de:
- `/credentials.json`: Credenciales OAuth2
- `token.pickle`: Token de acceso (generado automáticamente)

Los scopes necesarios están definidos en `src/config/google_api_config.py`

#### Ejemplo de Uso
```python
from src.integrations.google_docs import GoogleDocsClient

# Crear cliente
client = GoogleDocsClient()

# Crear documento
doc = client.create_document("Título del Documento")
print(f"Documento creado: {doc['webViewLink']}")

# Insertar texto
client.insert_text(doc['id'], "Contenido del documento")
```

### Google Drive
Se utiliza para almacenamiento y organización de documentos.

### Google Calendar
Gestión de audiencias y plazos legales.

### Gmail
Sistema de notificaciones y comunicaciones.

## Supabase
Autenticación y almacenamiento de datos del sistema.
