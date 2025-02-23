# Guía de Desarrollo de Webhook con ngrok

## ¿Qué es ngrok?

ngrok es una herramienta que crea túneles seguros hacia servidores locales, permitiendo exponer aplicaciones locales a internet.

## Configuración Básica

1. **Instalación**

   ```bash
   brew install ngrok  # macOS
   # o
   pip install pyngrok
   ```

2. **Iniciar Túnel**

   ```bash
   ngrok http 3000  # Expone servidor local en puerto 3000
   ```

3. **Configuración en Slack**
   - Usar URL generada por ngrok como Request URL
   - La URL cambia en cada reinicio de ngrok

## Consideraciones de Seguridad

- URLs de ngrok son temporales
- No usar en producción
- Rotar URLs frecuentemente

## Ejemplo de Uso con Slack

1. Iniciar servidor local
2. Ejecutar ngrok
3. Copiar URL generada
4. Configurar en Slack App Events

## Resolución de Problemas

- Verificar que el puerto coincida
- Comprobar conectividad
- Revisar logs de ngrok

## Mejores Prácticas

- Usar para desarrollo y pruebas
- Implementar verificación de firma de Slack
- Tener un plan de despliegue en producción
