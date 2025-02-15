# Arquitectura del Sistema First Court

## 1. Visión General
First Court es un sistema de justicia automatizado que utiliza agentes de IA especializados para manejar casos judiciales. El sistema está diseñado para ser modular, escalable y adaptable al sistema judicial chileno.

## 2. Estructura del Proyecto
```
first_court/
├── custom/          # Nuestras personalizaciones
│   ├── agents/      # Configuración de agentes
│   ├── integrations/# Integraciones externas
│   └── extensions/  # Extensiones personalizadas
├── docs/           # Documentación
└── scripts/        # Scripts de utilidad
```

## 3. Componentes Principales

### 3.1 Agentes Core
El sistema se basa en tres agentes principales:

#### Agente Analista Legal (DeepSeek-R1 37B)
- **Responsabilidades**:
  - Análisis legal complejo
  - Razonamiento jurídico
  - Evaluación de casos
  - Toma de decisiones
  - Auto-verificación

#### Agente Secretario (DeepSeek-R1-Distill-Qwen-32B)
- **Responsabilidades**:
  - Tareas administrativas
  - Gestión de flujos de trabajo
  - Coordinación entre agentes
  - Mantenimiento de registros
  - Eficiencia operativa

#### Agente de Documentación (DeepSeek-Coder-V2-Instruct 21B)
- **Responsabilidades**:
  - Generación de documentos
  - Mantenimiento de código
  - Integración con APIs
  - Gestión documental
  - Soporte multi-formato

### 3.2 Sistema de Mensajería
- **MessageBroker**: Sistema central de mensajería
- **MessageQueue**: Cola de mensajes por agente
- **MessageTypes**:
  - REQUEST: Solicitudes
  - RESPONSE: Respuestas
  - NOTIFICATION: Notificaciones
  - UPDATE: Actualizaciones
  - DECISION: Decisiones
  - ERROR: Errores

### 3.3 Integraciones
- **Supabase**: Autenticación y almacenamiento
- **Google Workspace**: Calendar, Drive, Gmail, Docs
- **RAG**: Sistema de recuperación y generación aumentada

## 4. Flujo de Trabajo

1. **Inicio de Caso**
   - Recepción de documentación
   - Asignación al Secretario
   - Creación de expediente

2. **Procesamiento**
   - Análisis por el Fiscal
   - Asignación de Defensor
   - Recopilación de evidencia

3. **Evaluación Judicial**
   - Revisión por el Juez
   - Programación de audiencias
   - Emisión de resoluciones

4. **Cierre de Caso**
   - Decisión final
   - Documentación
   - Archivo

## 5. Estándares y Prácticas

### 5.1 Código
- Python para los agentes y lógica de negocio
- TypeScript para la interfaz web
- Documentación en español

### 5.2 Base de Datos
- Supabase como plataforma principal
- Esquemas bien definidos
- Migraciones controladas

### 5.3 Seguridad
- Autenticación obligatoria
- Roles y permisos específicos
- Encriptación de datos sensibles
- Secrets manejados vía GitHub Actions
- No hay credenciales en el código
- Separación clara de configuraciones

## 6. Estado Actual
- Servidor de desarrollo en puerto 3333
- Autenticación Supabase configurada
- Credenciales gestionadas vía GitHub Secrets
- APIs de Google configuradas
- Variables de entorno protegidas

## 7. Próximos Pasos

### 7.1 Corto Plazo
1. Verificar configuraciones de agentes
2. Validar integraciones
3. Optimizar comunicación entre agentes
4. Implementar flujos específicos

### 7.2 Mediano Plazo
1. Mejora de la interacción entre agentes
2. Implementación de flujos específicos
3. Adaptación a casos reales

### 7.3 Largo Plazo
1. Integración con sistemas externos
2. Implementación de IA avanzada
3. Optimización general del sistema

## 8. Notas Importantes
- Mantener la simplicidad en el diseño
- Priorizar la confiabilidad sobre la velocidad
- Documentar todos los cambios significativos
- Seguir las regulaciones legales chilenas
