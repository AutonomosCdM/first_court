# Eventos WebSocket

## Conexión

### Endpoint
```
ws://localhost:3333/api/ws
```

### Autenticación
El token JWT debe enviarse en el header `Authorization`:
```
Authorization: Bearer <token>
```

## Tipos de Eventos

### 1. Eventos de Documento

#### `document_update`
Emitido cuando un documento es actualizado.

```json
{
  "type": "document_update",
  "data": {
    "documentId": "doc123",
    "action": "update|delete|create",
    "metadata": {
      "id": "doc123",
      "name": "Documento.pdf",
      "modifiedTime": "2025-02-15T19:21:30Z"
    }
  }
}
```

#### `document_chunk_ready`
Emitido cuando un chunk está listo para ser descargado.

```json
{
  "type": "document_chunk_ready",
  "data": {
    "documentId": "doc123",
    "chunkIndex": 2,
    "totalChunks": 5
  }
}
```

### 2. Eventos de Notificación

#### `notification`
Emitido cuando hay una nueva notificación.

```json
{
  "type": "notification",
  "data": {
    "id": "notif123",
    "title": "Documento Actualizado",
    "message": "El documento 'Contrato.pdf' ha sido modificado",
    "type": "info",
    "created_at": "2025-02-15T19:21:30Z",
    "data": {
      "documentId": "doc123",
      "action": "update"
    }
  }
}
```

#### `notification_read`
Emitido cuando una notificación es marcada como leída.

```json
{
  "type": "notification_read",
  "data": {
    "notificationId": "notif123",
    "userId": "user456"
  }
}
```

### 3. Eventos de Caché

#### `cache_status`
Emitido cuando cambia el estado del caché de un documento.

```json
{
  "type": "cache_status",
  "data": {
    "documentId": "doc123",
    "status": "cached|caching|error",
    "progress": 75,
    "error": null
  }
}
```

## Manejo de Errores

### Formato de Error
```json
{
  "type": "error",
  "data": {
    "code": "ERROR_CODE",
    "message": "Descripción del error",
    "details": {}
  }
}
```

### Códigos de Error Comunes
- `CONNECTION_ERROR`: Error de conexión
- `AUTH_ERROR`: Error de autenticación
- `RATE_LIMIT`: Límite de tasa excedido
- `INVALID_MESSAGE`: Mensaje inválido
- `SERVER_ERROR`: Error interno del servidor

## Recomendaciones de Implementación

### 1. Reconexión Automática
```typescript
class WebSocketClient {
  private ws: WebSocket;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  
  connect() {
    this.ws = new WebSocket('ws://localhost:3333/api/ws');
    this.ws.onclose = this.handleClose.bind(this);
    this.ws.onerror = this.handleError.bind(this);
  }
  
  private handleClose() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        this.reconnectAttempts++;
        this.connect();
      }, this.getReconnectDelay());
    }
  }
  
  private getReconnectDelay() {
    return Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
  }
}
```

### 2. Manejo de Eventos
```typescript
class EventHandler {
  private handlers: Map<string, Function[]> = new Map();
  
  on(eventType: string, handler: Function) {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, []);
    }
    this.handlers.get(eventType)?.push(handler);
  }
  
  handle(message: WebSocketMessage) {
    const handlers = this.handlers.get(message.type) || [];
    handlers.forEach(handler => handler(message.data));
  }
}
```

### 3. Cola de Mensajes
```typescript
class MessageQueue {
  private queue: WebSocketMessage[] = [];
  private processing = false;
  
  async add(message: WebSocketMessage) {
    this.queue.push(message);
    if (!this.processing) {
      this.process();
    }
  }
  
  private async process() {
    this.processing = true;
    while (this.queue.length > 0) {
      const message = this.queue.shift();
      await this.handleMessage(message);
    }
    this.processing = false;
  }
}
```

## Ejemplos de Uso

### 1. Conexión Básica
```typescript
const ws = new WebSocket('ws://localhost:3333/api/ws');

ws.onopen = () => {
  console.log('Conectado al servidor');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  switch (message.type) {
    case 'notification':
      handleNotification(message.data);
      break;
    case 'document_update':
      handleDocumentUpdate(message.data);
      break;
    case 'error':
      handleError(message.data);
      break;
  }
};
```

### 2. Manejo de Notificaciones
```typescript
function handleNotification(data: NotificationData) {
  // Mostrar notificación
  showToast({
    title: data.title,
    message: data.message,
    type: data.type
  });
  
  // Actualizar contador
  updateUnreadCount();
  
  // Si es una notificación de documento
  if (data.data?.documentId) {
    // Actualizar vista de documento si está abierto
    updateDocumentIfOpen(data.data.documentId);
  }
}
```

### 3. Manejo de Actualizaciones de Documento
```typescript
function handleDocumentUpdate(data: DocumentUpdateData) {
  switch (data.action) {
    case 'update':
      refreshDocument(data.documentId);
      break;
    case 'delete':
      removeDocument(data.documentId);
      break;
    case 'create':
      addNewDocument(data.metadata);
      break;
  }
}
```
