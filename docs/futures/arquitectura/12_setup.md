# Configuración del Sistema ⚙️

## 1. Requisitos del Sistema

### 1.1 Hardware
- CPU: 4+ cores
- RAM: 16GB+ 
- Almacenamiento: 100GB+ SSD
- GPU: Opcional, para modelos locales

### 1.2 Software
- Python 3.10+
- Node.js 18+
- Docker
- Git

### 1.3 Servicios Cloud
- Google Cloud Platform
- Supabase
- GitHub

## 2. Configuración de Desarrollo

### 2.1 Entorno Local
```bash
# Clonar repositorio
git clone https://github.com/AutonomosCdM/first_court.git
cd first_court

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
npm install
```

### 2.2 Variables de Entorno
```bash
# Crear archivo .env
cp .env.example .env

# Variables requeridas
SUPABASE_URL=
SUPABASE_KEY=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
DEEPSEEK_API_KEY=
```

### 2.3 Base de Datos
```bash
# Iniciar Supabase
supabase start

# Ejecutar migraciones
supabase db reset
```

## 3. Configuración de Producción

### 3.1 Despliegue
```bash
# Construir imágenes
docker-compose build

# Iniciar servicios
docker-compose up -d
```

### 3.2 SSL/TLS
- Certificados generados automáticamente
- Renovación automática con Let's Encrypt
- Configuración de Nginx incluida

### 3.3 Monitoreo
- Prometheus para métricas
- Grafana para visualización
- Alertmanager para notificaciones

## 4. Seguridad

### 4.1 Autenticación
- OAuth2 con Google
- JWT para sesiones
- MFA habilitado

### 4.2 Autorización
- RBAC implementado
- Políticas por recurso
- Auditoría de accesos

### 4.3 Datos
- Encriptación en tránsito
- Encriptación en reposo
- Backups automáticos

## 5. Integraciones

### 5.1 Google Workspace
```bash
# Configurar credenciales
gcloud auth application-default login

# Habilitar APIs
gcloud services enable \
  calendar.googleapis.com \
  drive.googleapis.com \
  gmail.googleapis.com
```

### 5.2 Supabase
```bash
# Configurar CLI
supabase login

# Vincular proyecto
supabase link --project-ref <ref>
```

### 5.3 GitHub Actions
```bash
# Secretos requeridos
SUPABASE_URL=
SUPABASE_KEY=
GOOGLE_CREDENTIALS=
DOCKER_USERNAME=
DOCKER_PASSWORD=
```

## 6. Monitoreo

### 6.1 Logs
- Formato estructurado
- Rotación configurada
- Retención definida

### 6.2 Métricas
- Uso de recursos
- Latencia de APIs
- Errores y excepciones

### 6.3 Alertas
- Umbrales definidos
- Escalamiento configurado
- Notificaciones por email/Slack

## 7. Mantenimiento

### 7.1 Backups
```bash
# Backup manual
supabase db dump -f backup.sql

# Restaurar backup
supabase db reset --db-url=$DATABASE_URL
```

### 7.2 Actualizaciones
```bash
# Actualizar dependencias
pip install --upgrade -r requirements.txt
npm update

# Actualizar contenedores
docker-compose pull
docker-compose up -d
```

### 7.3 Limpieza
```bash
# Limpiar logs antiguos
find /var/log -name "*.log" -mtime +30 -delete

# Limpiar caché
docker system prune -af
```

## 8. Troubleshooting

### 8.1 Logs
```bash
# Ver logs de servicios
docker-compose logs -f [service]

# Ver logs de aplicación
tail -f /var/log/first_court/*.log
```

### 8.2 Diagnóstico
```bash
# Verificar servicios
docker-compose ps

# Verificar recursos
docker stats

# Verificar conectividad
nc -zv host port
```

### 8.3 Recuperación
```bash
# Reiniciar servicios
docker-compose restart [service]

# Reconstruir contenedores
docker-compose up -d --force-recreate

# Restaurar backup
supabase db reset --db-url=$DATABASE_URL
```
