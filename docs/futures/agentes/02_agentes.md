# Sistema de Agentes 🤖

## 1. Agentes Core

### 1.1 Agente Analista Legal (DeepSeek-R1 37B)
- **Modelo**: DeepSeek-R1 (37B parámetros activos)
- **Características**:
  * Razonamiento jurídico avanzado
  * Auto-verificación y reflexión
  * Cadenas de pensamiento (CoT)
  * Contexto de 128K tokens
  * Especializado en análisis legal complejo
- **Responsabilidades**:
  * Evaluación de casos
  * Toma de decisiones judiciales
  * Emisión de resoluciones
  * Control de calidad procesal
  * Gestión de audiencias
  * Coordinación con otros agentes
  * Supervisión del proceso judicial

### 1.2 Agente Secretario (DeepSeek-R1-Distill-Qwen-32B)
- **Modelo**: DeepSeek-R1-Distill-Qwen-32B
- **Características**:
  * Versión destilada eficiente
  * Mejor que OpenAI-o1-mini
  * Razonamiento moderado
  * Optimizado para tareas administrativas
- **Responsabilidades**:
  * Gestión de documentación
  * Coordinación entre agentes
  * Mantenimiento de registros
  * Programación de audiencias
  * Seguimiento de plazos procesales
  * Notificaciones legales
  * Mantenimiento de expedientes

### 1.3 Agente de Documentación (DeepSeek-Coder-V2-Instruct 21B)
- **Modelo**: DeepSeek-Coder-V2-Instruct (21B parámetros)
- **Características**:
  * Especializado en código y documentación
  * Soporte multi-formato
  * Integración con APIs
  * Optimizado para generación y mantenimiento
- **Responsabilidades**:
  * Generación de documentos legales
  * Mantenimiento de documentación
  * Integración con sistemas
  * Procesamiento de formatos
  * Gestión de plantillas
  * Control de versiones

### 1.4 Agente Fiscal (ProsecutorAgent)
- **Modelo**: Claude-3-Opus
- **Características**:
  * Análisis avanzado de evidencia
  * Razonamiento legal estructurado
  * Alta capacidad de procesamiento
  * Integración con bases de datos jurídicas
- **Responsabilidades**:
  * Presentación de cargos
  * Solicitud y análisis de evidencia
  * Peticiones al tribunal
  * Representación del interés público
  * Coordinación con autoridades
  * Estrategias de acusación

## 2. Sistema de Comunicación

### 2.1 MessageBroker
- Gestión centralizada de mensajes
- Colas de mensajes por agente
- Tipos de Mensajes:
  * REQUEST: Solicitudes
  * RESPONSE: Respuestas
  * NOTIFICATION: Notificaciones
  * UPDATE: Actualizaciones
  * DECISION: Decisiones
  * ERROR: Errores

### 2.2 Canales de Comunicación
- **Canal Judicial**: Juez-Secretario
- **Canal Procesal**: Defensor-Fiscal
- **Canal General**: Todos los agentes
- Registro y trazabilidad de todas las comunicaciones

## 3. Flujos de Trabajo

### 3.1 Procesamiento de Casos
1. Recepción inicial (Secretario)
2. Análisis preliminar (Fiscal)
3. Asignación de defensa (Defensor)
4. Evaluación judicial (Juez)
5. Seguimiento (Secretario)

### 3.2 Gestión Documental
1. Creación/Recepción de documentos
2. Validación y clasificación
3. Distribución a agentes relevantes
4. Procesamiento según tipo
5. Archivo y seguimiento

## 4. Monitoreo y Mantenimiento

### 4.1 Logs y Auditoría
- Registro de actividades
- Errores y excepciones
- Métricas de rendimiento
- Uso de recursos
- Trazabilidad de decisiones

### 4.2 Mejora Continua
- Retroalimentación de jueces humanos
- Actualización de conocimiento legal
- Refinamiento de criterios judiciales
- Adaptación a nuevas leyes
- Optimización de procedimientos

## 5. Estado Actual y Próximos Pasos

### 5.1 Implementado ✓
- Estructura base de agentes
- Sistema de mensajería central
- Protocolos de comunicación básicos
- Gestión documental básica

### 5.2 En Proceso 🔄
- Mejora en la interacción entre agentes
- Optimización de flujos de trabajo
- Integración con sistemas externos
- Refinamiento de modelos de IA

### 5.3 Pendiente ⏳
- Sistema avanzado de precedentes
- Análisis predictivo de casos
- Automatización completa de flujos
- Integración con tribunales externos
