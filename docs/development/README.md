# Guía de Desarrollo 👩‍💻

## Setup del Entorno

### 1. Requisitos Previos
```bash
# Python 3.11+
python --version

# Node.js 18+
node --version

# PostgreSQL 14+
psql --version

# Redis 6+
redis-cli --version
```

### 2. Variables de Entorno
```bash
# .env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
S3_BUCKET=your_bucket_name
REDIS_URL=redis://localhost:6379
ES_URL=http://localhost:9200
```

### 3. Instalación
```bash
# Backend
poetry install
poetry shell

# Frontend
yarn install
```

## Estructura del Proyecto

```
first_court/
├── docs/                  # Documentación
├── src/
│   ├── agents/           # Agentes IA
│   ├── api/              # API endpoints
│   ├── auth/             # Autenticación
│   ├── cache/            # Sistema de caché
│   ├── custom/           # Personalizaciones
│   ├── database/         # Modelos y migrations
│   ├── documents/        # Gestión documental
│   ├── integrations/     # Integraciones externas
│   ├── middleware/       # Middleware
│   ├── models/           # Modelos de datos
│   ├── monitoring/       # Monitoreo y logs
│   ├── notifications/    # Sistema de notificaciones
│   ├── realtime/        # WebSocket y tiempo real
│   ├── routes/          # Rutas API
│   ├── schemas/         # Schemas y validación
│   ├── search/          # Motor de búsqueda
│   ├── services/        # Lógica de negocio
│   ├── storage/         # Almacenamiento
│   ├── types/           # TypeScript types
│   └── utils/           # Utilidades
├── tests/               # Tests
└── ui/                 # Frontend
```

## Guías de Estilo

### Python
```python
# Usar type hints
def get_document(document_id: str) -> Dict[str, Any]:
    pass

# Docstrings
def process_document(document: Document) -> None:
    """Procesa un documento.
    
    Args:
        document: Documento a procesar
        
    Raises:
        DocumentError: Si hay error en el procesamiento
    """
    pass

# Logging estructurado
logger.info("Processing document", extra={
    "document_id": doc.id,
    "user_id": user.id
})
```

### TypeScript
```typescript
// Interfaces
interface Document {
  id: string;
  title: string;
  content: string;
  metadata: DocumentMetadata;
}

// Types
type DocumentStatus = 'draft' | 'published' | 'archived';

// React Components
const DocumentViewer: React.FC<DocumentViewerProps> = ({
  document,
  onUpdate
}) => {
  // ...
};
```

## Testing

### Backend
```python
# tests/services/test_thumbnails.py
def test_thumbnail_generation():
    service = ThumbnailService()
    result = await service.get_thumbnail(
        document_id="123",
        page=1,
        size="medium"
    )
    assert result["format"] == "webp"
    assert result["size"]["width"] == 300
```

### Frontend
```typescript
// tests/components/DocumentViewer.test.tsx
describe('DocumentViewer', () => {
  it('renders document content', () => {
    const { getByText } = render(<DocumentViewer doc={mockDoc} />);
    expect(getByText(mockDoc.title)).toBeInTheDocument();
  });
});
```

## CI/CD

### GitHub Actions
```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Tests
        run: poetry run pytest
```

## Monitoreo

### Métricas
```python
# src/monitoring/metrics.py
with thumbnail_metrics.measure_latency("get_thumbnail"):
    result = await service.get_thumbnail(...)
```

### Logging
```python
# src/monitoring/logger.py
logger.info("Thumbnail generated", extra={
    "document_id": doc_id,
    "page": page,
    "size": size,
    "format": format
})
```

## Integración con UI/UX

### 1. Componentes Requeridos

#### Document Viewer
```typescript
interface DocumentViewerProps {
  document: Document;
  preferences: UserPreferences;
  onAnnotationCreate: (annotation: Annotation) => void;
  onPreferenceUpdate: (prefs: Partial<UserPreferences>) => void;
}
```

#### Thumbnail Grid
```typescript
interface ThumbnailGridProps {
  documentId: string;
  totalPages: number;
  viewMode: 'grid' | 'list';
  size: 'small' | 'medium' | 'large';
  onPageSelect: (page: number) => void;
}
```

#### Preferences Panel
```typescript
interface PreferencesPanelProps {
  preferences: UserPreferences;
  onChange: (changes: Partial<UserPreferences>) => void;
  onReset: () => void;
}
```

### 2. Estados de UI

#### Loading
```typescript
const LoadingState: React.FC = () => (
  <div className="loading-skeleton">
    <div className="thumbnail-grid animate-pulse">
      {/* Grid placeholder */}
    </div>
  </div>
);
```

#### Error
```typescript
const ErrorState: React.FC<{ error: Error }> = ({ error }) => (
  <div className="error-container">
    <Icon name="error" />
    <h3>Error loading document</h3>
    <p>{error.message}</p>
    <Button onClick={retry}>Retry</Button>
  </div>
);
```

#### Offline
```typescript
const OfflineState: React.FC = () => (
  <div className="offline-banner">
    <Icon name="offline" />
    <p>Working offline - Changes will sync when online</p>
  </div>
);
```

## Flujo de Trabajo

1. Crear rama desde `develop`
2. Implementar cambios
3. Escribir/actualizar tests
4. Crear PR
5. Code review
6. Merge a `develop`
7. Deploy a staging
8. QA
9. Deploy a producción

## Contacto

- Backend: backend@firstcourt.legal
- Frontend: frontend@firstcourt.legal
- DevOps: devops@firstcourt.legal
- UI/UX: design@firstcourt.legal
