# Configuración del Sistema Judicial

## Arquitectura

El sistema utiliza Open Canvas como interfaz principal, integrado con:

### Agentes Especializados

1. **Agente Analista Legal**
   - Modelo: DeepSeek-R1 (37B parámetros)
   - Uso: Análisis legal y razonamiento jurídico
   - Tracking: `legal_analysis`

2. **Agente de Documentación**
   - Modelo: DeepSeek-Coder-V2-Instruct (21B parámetros)
   - Uso: Generación y mantenimiento de documentos
   - Tracking: `documentation`

3. **Agente Secretario**
   - Modelo: DeepSeek-R1-Distill-Qwen-32B
   - Uso: Tareas administrativas
   - Tracking: `administrative`

### Integraciones

- **LangSmith**: Trazabilidad y monitoreo
- **Supabase**: Autenticación y base de datos
- **Google Workspace**:
  - Calendar: Gestión de audiencias
  - Forms: Recopilación de datos
  - Sheets: Dashboards y reportes
  - Drive: Almacenamiento de documentos
  - Gmail: Notificaciones

## Configuración Inicial

1. **Clonar el Repositorio**:
   ```bash
   git clone https://github.com/AutonomosCdM/first_court.git
   cd first_court
   ```

2. **Instalar Dependencias**:
   ```bash
   yarn install
   ```

3. **Configuración de GitHub Actions**:
   - Los secrets se manejan automáticamente vía GitHub Actions
   - No se requiere configuración local de .env

4. **Desarrollo Local**:
   ```bash
   # Iniciar servidor de desarrollo
   cd open-canvas/apps/web
   yarn dev
   ```

## Monitoreo y Métricas

- Cada agente tiene tracking independiente en LangSmith
- Métricas disponibles:
  - Uso de tokens
  - Latencia
  - Tipos de operaciones
  - Costos por área

## Seguridad

- Credenciales manejadas vía GitHub Secrets
- Autenticación con Supabase
- OAuth2 para servicios de Google
- No se almacenan credenciales localmente

## Mantenimiento

- Los logs están disponibles en LangSmith
- Backups automáticos en Google Drive
- Monitoreo de uso de API por agente
