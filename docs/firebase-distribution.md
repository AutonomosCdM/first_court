# Guía de Distribución con Firebase

Esta guía detalla el proceso de distribución y testing usando Firebase App Distribution.

## Configuración Inicial

1. Instalar dependencias:

```bash
npm install
```

2. Configurar variables de entorno:

```bash
cp .env.template .env
# Editar .env con las credenciales de Firebase
```

3. Inicializar Firebase:

```bash
npm install -g firebase-tools
firebase login
firebase init
```

## Grupos de Testing

El sistema maneja tres grupos de testers:

1. **Internal Testers** (`internal-testers`)
   - Equipo de desarrollo
   - Acceso temprano a todas las builds
   - Feedback prioritario

2. **Alpha Testers** (`alpha-testers`)
   - Testers dedicados
   - Builds inestables/experimentales
   - Feedback detallado

3. **Beta Testers** (`beta-testers`)
   - Usuarios seleccionados
   - Builds más estables
   - Feedback de usuario final

## Scripts de Automatización

### Preparar Build

```bash
# Desarrollo
npm run build

# Staging
npm run build:staging

# Producción
npm run build:prod
```

### Desplegar a Firebase

```bash
# Despliegue rápido a internal-testers
npm run deploy

# Despliegue a staging (beta-testers)
npm run deploy:staging

# Despliegue a producción (todos los grupos)
npm run deploy:prod
```

### Gestionar Testers

```bash
# Agregar testers
npm run testers:add -- -a "email1@example.com,email2@example.com" -g "internal-testers"

# Generar notas de versión
npm run notes:gen
```

## Pipeline CI/CD

El pipeline automatiza:

1. **Testing**
   - Tests unitarios
   - Tests de integración
   - Análisis de código

2. **Build**
   - Compilación de assets
   - Generación de bundle
   - Optimización

3. **Distribución**
   - Upload a Firebase
   - Generación de notas de versión
   - Notificación a testers

4. **Release**
   - Tagging de versión
   - Changelog automático
   - Notificaciones Slack

## Sistema de Feedback

### Componente FeedbackForm

El componente `FeedbackForm` permite:

- Reportar bugs
- Sugerir mejoras
- Solicitar features

### Recolección de Datos

Cada feedback incluye:

- Información del dispositivo
- Versión de la app
- Screenshots (opcional)
- Logs relevantes

### Visualización

Los datos se almacenan en Firestore y son accesibles via:

- Dashboard de Firebase
- Panel de administración interno
- Reportes automatizados

## Proceso de Release

1. **Preparación**

   ```bash
   # Generar notas de versión
   npm run notes:gen -- -o release-notes.md
   
   # Review y edición
   vim release-notes.md
   ```

2. **Testing Interno**

   ```bash
   # Deploy a internal-testers
   npm run deploy -- -g internal-testers
   ```

3. **Beta Testing**

   ```bash
   # Deploy a beta después de aprobación interna
   npm run deploy -- -g beta-testers -n release-notes.md
   ```

4. **Release Final**

   ```bash
   # Deploy a todos los grupos
   npm run deploy:prod
   ```

## Troubleshooting

### Problemas Comunes

1. **Error de Upload**
   - Verificar tamaño del bundle
   - Confirmar permisos Firebase
   - Validar token de autenticación

2. **Notificaciones**
   - Revisar configuración de email
   - Verificar grupos de testers
   - Confirmar permisos de Slack

3. **Feedback Form**
   - Validar conexión Firestore
   - Verificar permisos de usuario
   - Revisar cuotas de almacenamiento

### Soporte

Para problemas técnicos:

- Email: support@firstcourt.com
- Slack: #firebase-support
- Docs: [Firebase App Distribution](https://firebase.google.com/docs/app-distribution)
