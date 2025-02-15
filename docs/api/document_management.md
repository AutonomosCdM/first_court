# APIs de Gestión Documental

## 1. Carga Progresiva de Documentos

### Endpoints

#### `GET /api/documents/{document_id}`
Obtiene los metadatos del documento.

```typescript
interface DocumentMetadata {
  id: string;
  name: string;
  mimeType: string;
  size: number;
  pageCount: number;
  modifiedTime: string;
  chunks: ChunkMetadata[];
}

interface ChunkMetadata {
  index: number;
  startPage: number;
  endPage: number;
  size: number;
  checksum: string;
}
```

#### `GET /api/documents/{document_id}/chunks/{chunk_index}`
Obtiene un chunk específico del documento.

```typescript
interface ChunkResponse {
  content: string;
  index: number;
  totalChunks: number;
  nextChunkAvailable: boolean;
}
```

### WebSocket Events

#### `document_update`
Emitido cuando un documento es actualizado.

```typescript
interface DocumentUpdateEvent {
  type: 'document_update';
  documentId: string;
  metadata: DocumentMetadata;
}
```

### Estados de UI Recomendados

```typescript
enum DocumentLoadingState {
  INITIAL = 'initial',
  LOADING_METADATA = 'loading_metadata',
  LOADING_CHUNK = 'loading_chunk',
  READY = 'ready',
  ERROR = 'error'
}
```

## 2. Sistema de Notificaciones

### Endpoints

#### `GET /api/notifications`
Obtiene las notificaciones no leídas.

```typescript
interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'success';
  created_at: string;
  read: boolean;
  data?: Record<string, any>;
}
```

#### `POST /api/notifications/{notification_id}/read`
Marca una notificación como leída.

### WebSocket Events

#### `notification`
Emitido cuando hay una nueva notificación.

```typescript
interface NotificationEvent {
  type: 'notification';
  notification: Notification;
}
```

### Estados de UI Recomendados

```typescript
interface NotificationState {
  unreadCount: number;
  notifications: Notification[];
  loading: boolean;
  error: string | null;
}
```

## 3. Caché de Documentos

### Indicadores de Estado

```typescript
interface CacheStatus {
  inCache: boolean;
  compressionEnabled: boolean;
  lastAccessed: string;
  size: number;
}
```

### Estados de UI Recomendados

```typescript
enum CacheIndicator {
  NOT_CACHED = 'not_cached',
  CACHING = 'caching',
  CACHED = 'cached',
  ERROR = 'error'
}
```

## 4. Ejemplos de Uso

### Carga de Documento
```typescript
// 1. Obtener metadatos
const metadata = await api.get(`/api/documents/${documentId}`);

// 2. Iniciar carga progresiva
for (const chunk of metadata.chunks) {
  const chunkData = await api.get(`/api/documents/${documentId}/chunks/${chunk.index}`);
  // Actualizar UI con nuevo contenido
  updateDocumentView(chunkData.content);
  
  if (chunkData.nextChunkAvailable) {
    // Pre-cargar siguiente chunk
    prefetchNextChunk(documentId, chunk.index + 1);
  }
}
```

### Manejo de Notificaciones
```typescript
// 1. Conectar WebSocket
const ws = new WebSocket('/api/ws/notifications');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'notification') {
    // Mostrar notificación
    showNotification(data.notification);
    // Actualizar contador
    updateUnreadCount(data.notification);
  }
};

// 2. Marcar como leída
async function markAsRead(notificationId: string) {
  await api.post(`/api/notifications/${notificationId}/read`);
  // Actualizar UI
  updateNotificationsList();
}
```

## 5. Recomendaciones de Implementación

### Visor de Documentos
1. Implementar scroll infinito para chunks
2. Mostrar barra de progreso por chunk
3. Implementar vista previa mientras se carga
4. Caché de chunks en memoria para navegación rápida

### Notificaciones
1. Usar toast/snackbar para notificaciones nuevas
2. Implementar badge con contador de no leídas
3. Permitir descarte rápido de notificaciones
4. Agrupar notificaciones por tipo/fecha

### Indicadores de Caché
1. Icono de estado en la lista de documentos
2. Tooltip con información detallada
3. Opción de recargar desde origen
4. Indicador de ahorro de datos
