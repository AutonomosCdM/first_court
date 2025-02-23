# Solución de Problemas con Tokens de Slack

## Token Revocado

### Síntomas

- Error: `token_revoked`
- Aplicación de Slack no funciona
- Autenticación fallida

### Pasos de Solución

1. **Reinstalar Aplicación**
   - Ir a <https://api.slack.com/apps>
   - Seleccionar tu aplicación
   - Ir a "Install App"
   - Hacer clic en "Reinstall to Workspace"

2. **Obtener Nuevo Token**
   - Después de reinstalar, copiar nuevo Bot Token
   - Actualizar en `.env`:

     ```
     SLACK_BOT_TOKEN=xoxb-nuevo-token
     ```

3. **Verificar Permisos**
   - Revisar "OAuth & Permissions"
   - Confirmar que todos los scopes necesarios estén presentes
     - chat:write
     - app_mentions:read
     - channels:read

4. **Configuración de Scopes**
   - Añadir scopes necesarios:

     ```
     - chat:write
     - app_mentions:read
     - channels:read
     - groups:read
     - im:read
     ```

5. **Solución de Errores Comunes**
   - Verificar que el token no haya expirado
   - Comprobar que la aplicación esté instalada en el workspace
   - Regenerar token si es necesario

## Buenas Prácticas

- Almacenar tokens de forma segura
- Usar variables de entorno
- Rotar tokens periódicamente
- Implementar manejo de errores en la aplicación

## Recursos Adicionales

- [Slack API Documentation](https://api.slack.com/authentication)
- [Token Management Guide](https://api.slack.com/authentication/token-types)
