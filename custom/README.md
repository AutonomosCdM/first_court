# Personalizaciones de First Court

Este directorio contiene todas las personalizaciones y extensiones de Open Canvas para el sistema judicial.

## Estructura

```
custom/
├── agents/           # Configuración de agentes DeepSeek
│   ├── legal/       # Agente Analista Legal
│   ├── docs/        # Agente de Documentación
│   └── admin/       # Agente Secretario
├── integrations/    # Integraciones con servicios externos
│   ├── google/      # Integraciones con Google Workspace
│   └── supabase/    # Configuración de Supabase
└── extensions/      # Extensiones de Open Canvas
    └── actions/     # Acciones personalizadas
```

## Actualización de Open Canvas

Para actualizar Open Canvas:
```bash
git submodule update --remote open-canvas
```

## Mantenimiento

1. Las personalizaciones se mantienen separadas del código base de Open Canvas
2. Los cambios en este directorio no afectan al submódulo
3. Las actualizaciones de Open Canvas no afectan nuestras personalizaciones
