# Pruebas de First Court

## Configuración de Pruebas

### Configuración de Credenciales

Las pruebas de integración utilizan los siguientes secrets de GitHub:

1. `TEST_GOOGLE_CREDENTIALS`: Credenciales OAuth 2.0 en formato JSON
2. `TEST_GOOGLE_TOKEN`: Token de acceso OAuth 2.0
3. `TEST_DRIVE_ROOT_FOLDER`: ID de la carpeta de pruebas en Google Drive

### Configuración Local

Para ejecutar las pruebas localmente, necesitas:

1. Obtener las credenciales del equipo
2. Crear el archivo `tests/credentials/test_google_credentials.json`
3. Configurar las variables de entorno:
   ```bash
   export TEST_GOOGLE_TOKEN='token_de_prueba'
   export TEST_DRIVE_ROOT_FOLDER='id_carpeta_pruebas'
   ```

### Usuarios de Prueba

Las pruebas utilizan las siguientes cuentas:
- test.juez@autonomos.dev
- test.fiscal@autonomos.dev
- test.defensor@autonomos.dev

Estas cuentas ya tienen acceso a la carpeta de pruebas configurada en `TEST_DRIVE_ROOT_FOLDER`.

## Ejecutar Pruebas

```bash
# Todas las pruebas
pytest

# Solo pruebas de Google Drive
pytest tests/integrations/test_google_drive.py -v

# Con cobertura
pytest --cov=src tests/
```

## Estructura de Pruebas

- `tests/config/`: Configuración de pruebas
- `tests/credentials/`: Credenciales (gitignored)
- `tests/integrations/`: Pruebas de integraciones
- `tests/agents/`: Pruebas de agentes
- `tests/temp/`: Archivos temporales (gitignored)
