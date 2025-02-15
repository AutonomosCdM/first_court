# Arquitectura de Agentes - First Court

## 1. Estructura de Agentes

### 1.1 Agente Analista Legal (/custom/agents/legal)
- **Modelo**: DeepSeek-R1 (37B parámetros)
- **Características**:
  * Razonamiento jurídico avanzado
  * Auto-verificación y reflexión
  * Cadenas de pensamiento (CoT)
  * Contexto de 128K tokens
- **Responsabilidades**:
  * Análisis legal complejo
  * Evaluación de jurisprudencia
  * Generación de dictámenes
  * Verificación de cumplimiento legal

### 1.2 Agente de Documentación (/custom/agents/docs)
- **Modelo**: DeepSeek-Coder-V2-Instruct (21B parámetros)
- **Características**:
  * Especialización en documentación
  * Soporte multi-formato
  * Integración con APIs
  * Procesamiento eficiente
- **Responsabilidades**:
  * Generación de documentos
  * Mantenimiento de registros
  * Gestión de plantillas
  * Indexación de contenido

### 1.3 Agente Secretario (/custom/agents/admin)
- **Modelo**: DeepSeek-R1-Distill-Qwen-32B
- **Características**:
  * Eficiencia en tareas rutinarias
  * Razonamiento moderado
  * Optimización de recursos
  * Gestión de flujos de trabajo
- **Responsabilidades**:
  * Coordinación administrativa
  * Gestión de calendarios
  * Manejo de comunicaciones
  * Seguimiento de procesos

## 2. Sistema de Comunicación

### 2.1 Mensajería
- **Broker Central**: Gestión de mensajes entre agentes
- **Colas de Mensajes**: Por agente y prioridad
- **Tipos de Mensajes**:
  * REQUEST: Solicitudes
  * RESPONSE: Respuestas
  * NOTIFICATION: Notificaciones
  * UPDATE: Actualizaciones
  * DECISION: Decisiones
  * ERROR: Errores

### 2.2 Protocolos
- Comunicación asíncrona
- Manejo de estados
- Priorización de mensajes
- Registro de interacciones

## 3. Integración con Servicios

### 3.1 Supabase
- Autenticación de usuarios
- Almacenamiento de datos
- Gestión de sesiones
- Control de acceso

### 3.2 Google Workspace
- Calendar: Gestión de audiencias
- Drive: Almacenamiento de documentos
- Gmail: Comunicaciones oficiales
- Docs: Generación de documentos

## 4. Flujos de Trabajo

### 4.1 Procesamiento de Casos
1. Recepción inicial (Secretario)
2. Análisis legal (Analista Legal)
3. Documentación (Agente de Documentación)
4. Seguimiento (Secretario)

### 4.2 Generación de Documentos
1. Solicitud de documento
2. Análisis de requisitos
3. Generación de contenido
4. Revisión y validación
5. Almacenamiento y distribución

## 5. Configuración

### 5.1 Variables de Entorno
- Credenciales de API
- URLs de servicios
- Configuraciones de modelos
- Parámetros de sistema

### 5.2 Gestión de Secretos
- GitHub Secrets
- Tokens de API
- Claves de servicio
- Certificados

## 6. Monitoreo y Mantenimiento

### 6.1 Logs
- Registro de actividades
- Errores y excepciones
- Métricas de rendimiento
- Uso de recursos

### 6.2 Alertas
- Errores críticos
- Sobrecarga de sistema
- Problemas de comunicación
- Fallos de integración

## 7. Desarrollo y Pruebas

### 7.1 Entorno de Desarrollo
- Puerto 3333 para desarrollo
- Autenticación opcional
- Logs detallados
- Recarga en caliente

### 7.2 Testing
- Pruebas unitarias
- Pruebas de integración
- Simulaciones de casos
- Pruebas de carga

## 8. Próximos Pasos

### 8.1 Corto Plazo
1. Verificar configuraciones de agentes
2. Validar integraciones
3. Comprobar tipos compartidos
4. Optimizar comunicación

### 8.2 Mediano Plazo
1. Implementar nuevas funcionalidades
2. Mejorar rendimiento
3. Ampliar capacidades
4. Refinar interacciones
