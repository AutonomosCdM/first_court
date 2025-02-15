# Arquitectura Core - First Court

## 1. Visión General
First Court es un sistema de justicia automatizado que utiliza agentes de IA especializados para manejar casos judiciales. El sistema está diseñado para ser modular, escalable y adaptable al sistema judicial chileno.

## 2. Componentes Principales

### 2.1 Agentes Judiciales
El sistema se basa en cuatro agentes principales:

#### Juez (JudgeAgent)
- **Responsabilidades**:
  - Evaluación de casos
  - Toma de decisiones judiciales
  - Emisión de resoluciones
  - Supervisión del proceso judicial

#### Fiscal (ProsecutorAgent)
- **Responsabilidades**:
  - Presentación de cargos
  - Solicitud y análisis de evidencia
  - Peticiones al tribunal
  - Representación del interés público

#### Defensor (DefenderAgent)
- **Responsabilidades**:
  - Representación del acusado
  - Presentación de mociones de defensa
  - Análisis de evidencia
  - Estrategia de defensa

#### Secretario (SecretaryAgent)
- **Responsabilidades**:
  - Gestión de documentación
  - Coordinación entre agentes
  - Mantenimiento de registros
  - Programación de audiencias

### 2.2 Sistema de Mensajería
- **MessageBroker**: Sistema central de mensajería
- **MessageQueue**: Cola de mensajes por agente
- **MessageTypes**:
  - REQUEST: Solicitudes
  - RESPONSE: Respuestas
  - NOTIFICATION: Notificaciones
  - UPDATE: Actualizaciones
  - DECISION: Decisiones
  - ERROR: Errores

### 2.3 Integración con Supabase
- Autenticación de usuarios
- Almacenamiento de datos
- Gestión de sesiones

## 3. Flujo de Trabajo

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

## 4. Estándares y Prácticas

### 4.1 Código
- Python para los agentes y lógica de negocio
- TypeScript/Next.js para la interfaz web
- Documentación en español

### 4.2 Base de Datos
- Supabase como plataforma principal
- Esquemas bien definidos
- Migraciones controladas

### 4.3 Seguridad
- Autenticación obligatoria
- Roles y permisos específicos
- Encriptación de datos sensibles

## 5. Próximos Pasos

1. **Fase Actual**
   - Implementación de autenticación
   - Configuración de agentes base
   - Pruebas de integración

2. **Siguientes Fases**
   - Mejora de la interacción entre agentes
   - Implementación de flujos específicos
   - Adaptación a casos reales

## 6. Notas Importantes

- Mantener la simplicidad en el diseño
- Priorizar la confiabilidad sobre la velocidad
- Documentar todos los cambios significativos
- Seguir las regulaciones legales chilenas

---

Este documento debe ser actualizado regularmente para reflejar cambios en la arquitectura y nuevas decisiones de diseño.
