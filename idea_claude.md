# Sistema de Simulación Interactiva para Juicios Orales Penales

## 1. Visión General

El objetivo es crear un sistema de simulación interactiva para juicios orales penales en Chile que permita el entrenamiento y evaluación de estudiantes de derecho y profesionales del área judicial.

### 1.1 Capacidades Principales
- Permitir que estudiantes asuman cualquier rol
- Interacción entre humanos y agentes AI
- Análisis y retroalimentación del desempeño
- Aprendizaje de las interacciones

### 1.2 Base de Conocimiento
- Plan de estudios completo de Derecho UACH
- Enfoque en procedimientos penales y litigación

## 2. Arquitectura del Sistema

### 2.1 Agentes AI

#### Juez
- Dirección de la audiencia
- Evaluación de argumentos
- Toma de decisiones basada en ley
- Retroalimentación a estudiantes
- API: DeepSeek-R1 37B

#### Fiscal
- Presentación de cargos
- Argumentación legal
- Manejo de evidencia
- Técnicas de interrogatorio
- API: DeepSeek-R1 37B

#### Defensor
- Estrategias de defensa
- Contrainterrogatorio
- Argumentación legal
- Protección derechos del imputado
- API: DeepSeek-R1 37B

#### Secretario
- Gestión administrativa
- Registro de audiencia
- Apoyo procesal
- Control de tiempos
- API: DeepSeek-R1-Distill-Qwen-32B

### 2.2 Flujo de Audiencia
1. Inicio audiencia (Secretario)
2. Presentación del caso (Fiscal)
3. Alegatos (Fiscal/Defensor)
4. Decisiones y control (Juez)

## 3. Plan de Estudios e Integración

### 3.1 Niveles de Integración

#### Primer Semestre
- Sistema Jurídico: Conceptos básicos del marco legal
- Jurisdicción: Fundamentos de la función jurisdiccional

#### Tercer-Cuarto Semestre
- Proceso Civil Ordinario
- Derecho Procesal Constitucional
- Introducción básica a audiencias

#### Séptimo-Octavo Semestre (Punto Crítico)
- Proceso Penal
- Litigación Penal
- Técnicas avanzadas de simulación

### 3.2 Niveles de Aprendizaje

#### Básico (1-4 semestre)
- Observación de simulaciones
- Roles básicos
- Fundamentos teóricos

#### Intermedio (5-6 semestre)
- Participación activa
- Roles alternados
- Retroalimentación detallada

#### Avanzado (7-10 semestre)
- Simulaciones completas
- Casos complejos
- Evaluación profesional

### 3.3 Plan de Implementación

#### FASE 1 - INTRODUCCIÓN (Semestres 1-2)
- Módulo observacional
- Agentes AI demuestran audiencias básicas
- Estudiantes aprenden estructura y roles
- Integrado con "Sistema Jurídico" y "Jurisdicción"

#### FASE 2 - PARTICIPACIÓN BÁSICA (Semestres 3-4)
- Roles individuales con guía AI
- Enfoque en comunicación jurídica
- Retroalimentación automática
- Integrado con "Proceso Civil" y "Razonamiento Jurídico"

#### FASE 3 - PRÁCTICA INTERMEDIA (Semestres 5-6)
- Simulaciones parciales
- Interacción múltiples roles
- Análisis de desempeño
- Vinculado a "Derecho Penal" y "Procedimientos"

#### FASE 4 - PRÁCTICA AVANZADA (Semestres 7-8)
- Casos complejos completos
- Evaluación profesional
- Aprendizaje adaptativo
- Integrado con "Litigación Penal"

## 4. Características del Sistema

### 4.1 Sistema de Evaluación
- Rúbricas automatizadas
- Métricas de desempeño
- Feedback personalizado
- Análisis de lenguaje jurídico

### 4.2 Biblioteca de Casos
- Casos reales anonimizados
- Diferentes niveles de complejidad
- Categorización por materias
- Actualización periódica

### 4.3 Herramientas Complementarias
- Grabación de simulaciones
- Transcripciones automáticas
- Análisis de argumentación
- Repositorio de jurisprudencia

### 4.4 Módulo de Práctica Individual
- Ejercicios específicos por rol
- Simulaciones asincrónicas
- Preparación de argumentos
- Estrategias de litigación

## 5. Sistema de Evaluación Automatizado

### 5.1 Rúbricas Automatizadas
- Estructura argumentativa
- Uso de lenguaje jurídico
- Tiempo y ritmo de intervención
- Manejo procesal
- Interacción con otros agentes

### 5.2 Métricas Clave
- Precisión legal
- Calidad argumentativa
- Respuesta a objeciones
- Manejo del tiempo
- Seguimiento protocolar

## 6. Tecnologías

### 6.1 Backend
- Python 3.13+
- FastAPI
- Supabase (Base de datos y autenticación)
- DeepSeek APIs

### 6.2 Frontend
- React + TypeScript
- Material-UI
- Socket.io
- Redux

### 6.3 Integraciones
- Google Calendar: Gestión de audiencias
- Gmail: Sistema de notificaciones
- GitHub: CI/CD y secretos

## 7. Sistema de Feedback

### 7.1 Feedback en Tiempo Real
- Alertas de errores procesales
- Sugerencias de mejora
- Referencias a normativa
- Ejemplos de buenas prácticas

### 7.2 Análisis Post-Simulación
- Reporte detallado
- Puntos fuertes/débiles
- Recomendaciones específicas
- Plan de mejora personalizado
