# Guía de Despliegue

Esta guía detalla el proceso de despliegue para diferentes entornos.

## Entornos

El proyecto soporta tres entornos:

- Development (desarrollo local)
- Testing (pruebas)
- Production (producción)

## Variables de Entorno

Cada entorno requiere su propio archivo de configuración:

- `.env.development` - Desarrollo local
- `.env.test` - Entorno de pruebas
- `.env.production` - Producción

## Pipeline CI/CD

### GitHub Actions

El pipeline se ejecuta automáticamente en:

- Push a `main` o `develop`
- Pull Requests a `main` o `develop`

Etapas:

1. Tests
   - Pruebas unitarias
   - Pruebas de integración
   - Cobertura de código

2. Lint
   - Black (formato)
   - isort (imports)
   - flake8 (estilo)

3. Deploy Firebase
   - Solo en push a `main`
   - Requiere FIREBASE_TOKEN

4. Deploy Production
   - Solo en push a `main`
   - Despliega a AWS ECS
   - Requiere credenciales AWS

## Firebase

### Configuración Inicial

1. Crear proyecto en Firebase Console
2. Obtener credenciales:
   - API Key
   - Auth Domain
   - Project ID
   - Storage Bucket
   - Messaging Sender ID
   - App ID

3. Configurar en `.env`:

```
FIREBASE_API_KEY=xxx
FIREBASE_AUTH_DOMAIN=xxx
FIREBASE_PROJECT_ID=xxx
FIREBASE_STORAGE_BUCKET=xxx
FIREBASE_MESSAGING_SENDER_ID=xxx
FIREBASE_APP_ID=xxx
```

### Reglas de Storage

Las reglas en `storage.rules` definen:

- Acceso por autenticación
- Límites de tamaño
- Tipos de archivo permitidos
- Permisos por rol

### Despliegue Manual

```bash
# Login
firebase login

# Test local
firebase emulators:start

# Deploy
firebase deploy
```

## AWS ECS

### Prerrequisitos

- Cluster ECS configurado
- Repositorio ECR creado
- IAM roles y políticas

### Proceso de Despliegue

1. Build imagen Docker
2. Push a ECR
3. Update ECS service

### Variables Requeridas

```
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_REGION=us-west-2
```

## Monitoreo

- Logs en CloudWatch
- Firebase Analytics
- Error tracking

## Rollback

### Firebase

```bash
firebase hosting:clone <source-site> <target-site>
```

### ECS

```bash
aws ecs update-service --cluster xxx --service xxx --task-definition xxx
```

## Troubleshooting

### Problemas Comunes

1. Error de despliegue Firebase
   - Verificar token
   - Revisar permisos
   - Validar configuración

2. Fallo ECS
   - Revisar logs CloudWatch
   - Verificar definición de tarea
   - Comprobar IAM roles

### Contacto Soporte

Para problemas críticos:

- Email: <support@firstcourt.com>
- Slack: #deploy-support
