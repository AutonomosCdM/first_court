# Solución de Problemas de Webhook de Slack

## Errores Comunes

### 1. URL de Verificación Inválida

- Asegúrate de que la URL sea accesible públicamente
- Usa servicios como ngrok para pruebas locales
- Verifica que la URL use HTTPS

### 2. Problemas de Autenticación

- Confirmar que el Token de Bot es correcto
- Verificar que los scopes sean los adecuados
- Revisar el Signing Secret

### 3. Eventos no Recibidos

- Comprobar configuración de Event Subscriptions
- Validar que los eventos estén suscritos correctamente
- Verificar logs de la aplicación

## Herramientas de Diagnóstico

### Verificación de Webhook

```bash
# Probar conexión básica
curl -X POST https://[tu-dominio]/slack/events
```

### Registro de Eventos

- Implementar logging detallado
- Capturar y registrar todos los eventos recibidos
- Analizar contenido de los eventos

## Configuración de Depuración

### Variables de Entorno

```bash
export SLACK_DEBUG=true
export SLACK_LOG_LEVEL=DEBUG
```

### Comandos Útiles

- `slack-cli`: Herramienta para pruebas de Slack
- Usar ngrok para tunelización temporal
