# Configuración de Webhook para Slack Events API

## Pasos para Configurar el Webhook

1. **Despliegue del Servidor**
   - El webhook se ejecuta en `http://[tu-dominio]/slack/events`
   - Requiere estar accesible públicamente desde internet

2. **Configuraciones Necesarias**
   - Variable de entorno `SLACK_SIGNING_SECRET` debe estar configurada
   - Endpoint debe manejar:
     - Verificación de URL
     - Eventos

3. **Configuración en Slack App**
   - Ir a <https://api.slack.com/apps>
   - Seleccionar tu aplicación
   - Ir a "Event Subscriptions"
   - Habilitar "Enable Events"
   - Ingresar Request URL: `https://[tu-dominio]/slack/events`

4. **Suscripciones de Eventos**
   - Suscribirse a eventos de bot:
     - `app_mention`
     - `message.channels`
     - `message.groups`
     - `message.im`

5. **Verificación**
   - Slack enviará un desafío de verificación
   - El webhook debe responder con el valor del desafío
   - Verificar que la URL sea accesible públicamente

## Consideraciones de Seguridad

- Usar HTTPS
- Implementar verificación de firma de Slack
- Proteger el secreto de firma

## Despliegue

- Usar Gunicorn para producción
- Configurar variables de entorno
- Implementar manejo de errores
- Monitorear logs de eventos
