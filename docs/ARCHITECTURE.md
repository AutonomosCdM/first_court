# Arquitectura del Sistema

## Estructura del Proyecto

```
first_court/
├── open-canvas/     # Submódulo de Open Canvas (actualizable)
├── custom/          # Nuestras personalizaciones
│   ├── agents/      # Configuración de agentes
│   ├── integrations/# Integraciones externas
│   └── extensions/  # Extensiones personalizadas
├── docs/           # Documentación
└── scripts/        # Scripts de utilidad
```

## Componentes Principales

1. **Open Canvas (Submódulo)**
   - Framework base para la interfaz
   - Actualizable independientemente
   - No modificado directamente

2. **Personalizaciones (custom/)**
   - Agentes DeepSeek especializados
   - Integraciones con Google Workspace
   - Acciones personalizadas para el sistema judicial

3. **Integraciones**
   - Google Calendar para audiencias
   - Google Forms para intake
   - Google Sheets para dashboards
   - Supabase para autenticación

## Flujo de Actualizaciones

1. **Open Canvas**
   ```bash
   git submodule update --remote open-canvas
   ```

2. **Personalizaciones**
   - Se mantienen en custom/
   - No afectadas por actualizaciones
   - Versionadas con el proyecto principal

## Seguridad

- Secrets manejados vía GitHub Actions
- No hay credenciales en el código
- Separación clara de configuraciones
