# Guía Estándar de Integración de Slack para Proyectos

## 1. Estructura de Directorios

```
project_root/
│
└── src/
    └── integrations/
        └── slack/
            ├── __init__.py
            ├── base/
            │   ├── __init__.py
            │   ├── event_handler.py
            │   └── command_router.py
            ├── utils/
            │   ├── __init__.py
            │   ├── message_broker.py
            │   ├── notification.py
            │   └── document_handler.py
            ├── agents/
            │   ├── __init__.py
            │   └── [specific_agent]_app.py
            ├── run_agents.py
            ├── README.md
            └── requirements.txt
```

## 2. Componentes Clave

### 2.1 Base Event Handler (`base/event_handler.py`)

- Clase base para manejo de eventos de Slack
- Métodos abstractos para manejar mensajes, menciones y comandos
- Inicialización de cliente Slack
- Gestión de sesiones asíncronas

```python
class BaseSlackHandler(ABC):
    def __init__(self, env_prefix: str):
        # Inicialización del cliente Slack
        # Carga de credenciales desde variables de entorno
        # Configuración de sesión asíncrona

    @abstractmethod
    async def handle_message(self, event: Dict[str, Any]):
        # Manejo de mensajes generales

    @abstractmethod
    async def handle_mention(self, event: Dict[str, Any]):
        # Manejo de menciones al bot

    @abstractmethod
    async def handle_command(self, command: str, args: str, event: Dict[str, Any]):
        # Manejo de comandos slash
```

### 2.2 Command Router (`base/command_router.py`)

- Enrutamiento de comandos mediante expresiones regulares
- Soporte para comandos personalizados
- Validación de patrones de comando

```python
class CommandRouter:
    def command(self, pattern: str):
        # Decorador para registrar manejadores de comandos
        # Usa expresiones regulares para matchear comandos

    async def handle_command(self, text: str, event: Dict[str, Any]) -> bool:
        # Enruta comandos a sus manejadores correspondientes
```

### 2.3 Utilidades

#### Message Broker (`utils/message_broker.py`)

- Gestión de comunicación entre agentes
- Creación de canales
- Envío de mensajes

#### Notification Manager (`utils/notification.py`)

- Sistema de notificaciones
- Soporte para diferentes tipos de notificaciones
- Integración con canales de Slack

#### Document Handler (`utils/document_handler.py`)

- Manejo de subida y procesamiento de documentos
- Soporte para diferentes tipos de archivos
- Integración con servicios de almacenamiento

## 3. Estructura de Agentes

### 3.1 Plantilla de Agente

```python
class [Agent]SlackApp(BaseSlackHandler):
    def __init__(self):
        super().__init__(env_prefix="[AGENT]")
        self.router = CommandRouter()
        self.register_commands()

    def register_commands(self):
        # Registro de comandos específicos del agente
        @self.router.command(r"comando (.*)")
        async def handle_command(text: str, event: Dict[str, Any]):
            # Lógica del comando

    async def handle_message(self, event: Dict[str, Any]):
        # Lógica de manejo de mensajes generales

    async def handle_mention(self, event: Dict[str, Any]):
        # Lógica de manejo de menciones
```

## 4. Configuración de Entorno

### 4.1 Variables de Entorno (`.env`)

```
[AGENT]_SLACK_APP_ID=
[AGENT]_BOT_TOKEN=
[AGENT]_SIGNING_SECRET=
SLACK_GENERAL_CHANNEL=
DEFAULT_WORKSPACE=
DEFAULT_LOCALE=
DEFAULT_TIMEZONE=
```

### 4.2 Archivo de Requisitos (`requirements.txt`)

- Incluir dependencias estándar
- Versiones específicas
- Separar dependencias por categoría

## 5. Pruebas

### 5.1 Estructura de Pruebas

- Pruebas unitarias para cada agente
- Cobertura de casos de uso
- Validación de patrones de comando
- Mocking de interacciones de Slack

## 6. Mejores Prácticas

### 6.1 Desarrollo

- Usar typing y anotaciones de tipos
- Implementar manejo de errores robusto
- Logging estructurado
- Código asíncrono eficiente

### 6.2 Seguridad

- Validación de credenciales
- Manejo seguro de tokens
- Control de acceso basado en roles
- Auditoría de acciones

### 6.3 Documentación

- README detallado
- Comentarios en código
- Documentación de comandos
- Guía de contribución

## 7. Despliegue y Configuración

### 7.1 Pasos de Instalación

1. Clonar repositorio
2. Crear entorno virtual
3. Instalar dependencias
4. Configurar variables de entorno
5. Ejecutar pruebas
6. Iniciar agentes

### 7.2 Configuración de Slack

- Crear aplicación de Slack
- Configurar scopes y permisos
- Generar tokens
- Configurar webhooks

## 8. Extensibilidad

### 8.1 Puntos de Extensión

- Fácil adición de nuevos agentes
- Personalización de comandos
- Integración con otros servicios

## 9. Mantenimiento

### 9.1 Actualización

- Revisiones periódicas de dependencias
- Seguimiento de mejores prácticas
- Actualización de bibliotecas

## 10. Contribución

### 10.1 Guía para Contribuidores

- Estándares de código
- Proceso de revisión
- Guías de desarrollo
