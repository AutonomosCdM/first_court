# First Court 🏛️

## Descripción
Sistema de gestión judicial basado en agentes inteligentes, con interfaz moderna y capacidades colaborativas para el sistema judicial chileno.

## 🚀 Características Principales

- **Agentes Inteligentes**: Sistema basado en DeepSeek para análisis legal y gestión documental
- **Interfaz Moderna**: UI/UX diseñada para eficiencia y usabilidad
- **Colaboración en Tiempo Real**: Sistema de WebSockets para trabajo colaborativo
- **Integración con Google Workspace**: Calendar, Drive, Gmail
- **Sistema RAG**: Recuperación y generación aumentada de documentos

## 🛠️ Tecnologías

### Backend
- Python 3.11+
- FastAPI
- PostgreSQL
- Redis (WebSockets)
- DeepSeek Models

### Frontend
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Zustand

## 📋 Estructura del Proyecto

```
first_court/
├── backend/
│   ├── app/
│   │   ├── api/          # Endpoints REST y WebSocket
│   │   ├── core/         # Configuración y utilidades
│   │   ├── models/       # Modelos de datos
│   │   └── services/     # Lógica de negocio
│   └── alembic/          # Migraciones de base de datos
├── frontend/
│   ├── src/
│   │   ├── components/   # Componentes React
│   │   ├── hooks/        # Custom hooks
│   │   ├── stores/       # Estado global
│   │   └── styles/       # Estilos y tema
│   └── public/           # Assets estáticos
└── docs/
    ├── arquitectura/     # Documentación técnica
    ├── agentes/          # Configuración de agentes
    ├── integraciones/    # Integraciones externas
    ├── mejoras/          # Mejoras planificadas
    └── ui_ux/            # Guías de diseño
```

## ⚙️ Configuración

### Variables de Entorno

#### Backend (.env)
```env
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=firstcourt
SECRET_KEY=your-secret-key
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
WS_MESSAGE_QUEUE=redis://localhost
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Instalación

1. **Backend**
```bash
# Instalar dependencias
pip install poetry
poetry install

# Configurar base de datos
poetry run alembic upgrade head

# Iniciar servidor
poetry run uvicorn app.main:app --reload
```

2. **Frontend**
```bash
# Instalar dependencias
cd frontend
yarn install

# Iniciar servidor de desarrollo
yarn dev
```

## 🚀 Ejecución

### Desarrollo
```bash
# Terminal 1 - Backend
cd backend
poetry run uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
yarn dev
```

### Producción
```bash
# Construir y ejecutar con Docker
docker-compose up --build -d
```

La aplicación estará disponible en:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Documentación API: http://localhost:8000/docs

## 🤝 Contribución

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📚 Documentación

Consulta la carpeta `/docs` para documentación detallada sobre:
- Arquitectura del sistema
- Configuración de agentes
- Integraciones con servicios externos
- Guías de UI/UX
- Mejoras planificadas
./scripts/setup_canvas.sh
```

3. Iniciar el servidor de desarrollo:
```bash
cd vendor/open-canvas
yarn dev
```

### Estructura del Proyecto

- `/vendor/open-canvas`: Submódulo de Open Canvas
- `/custom`: Extensiones personalizadas para Open Canvas
  - `/agents`: Configuración de agentes
  - `/integrations`: Integraciones con servicios externos
  - `/extensions`: Acciones personalizadas
  - `/types`: Tipos compartidos

### Desarrollo

Para desarrollar nuevas funcionalidades:

1. No modificar directamente el código en `/vendor/open-canvas`
2. Crear extensiones en `/custom`
3. Utilizar los tipos compartidos en `/custom/types`
4. Seguir la guía de estilo en la documentación
