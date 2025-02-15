# Document Viewer API 📄

## Thumbnails

### Get Thumbnail
```http
GET /api/documents/{id}/thumbnails/{page}
```

Obtiene la miniatura de una página específica de un documento.

#### Parameters

| Name     | Type    | In    | Description                           |
|----------|---------|-------|---------------------------------------|
| id       | string  | path  | ID del documento                      |
| page     | integer | path  | Número de página                      |
| size     | string  | query | Tamaño (small, medium, large)        |
| format   | string  | query | Formato (webp, jpeg)                 |
| quality  | integer | query | Calidad (1-100)                      |

#### Response

```json
{
  "url": "string",
  "size": {
    "width": "integer",
    "height": "integer"
  },
  "format": "string",
  "expires": "ISO8601"
}
```

## User Preferences

### Get Preferences
```http
GET /api/users/preferences
```

Obtiene las preferencias del usuario actual.

#### Response

```json
{
  "viewer": {
    "theme": "light | dark | system",
    "fontSize": "number",
    "zoom": "number",
    "showMinimap": "boolean",
    "showLineNumbers": "boolean",
    "wordWrap": "boolean"
  },
  "thumbnails": {
    "viewMode": "grid | list",
    "size": "small | medium | large",
    "showLabels": "boolean"
  },
  "annotations": {
    "defaultColor": "string",
    "defaultType": "highlight | comment | drawing",
    "autoShow": "boolean"
  },
  "collaboration": {
    "showCursors": "boolean",
    "showPresence": "boolean",
    "notificationsEnabled": "boolean"
  },
  "keyboard": {
    "shortcuts": "Record<string, string>",
    "enabledFeatures": "string[]"
  },
  "sync": {
    "frequency": "number",
    "autoSave": "boolean",
    "offlineMode": "aggressive | conservative"
  }
}
```

### Sync Preferences
```http
PUT /api/users/preferences
```

Sincroniza las preferencias del usuario.

#### Request Body

```json
{
  "preferences": "Partial<UserPreferences>",
  "lastSyncTimestamp": "ISO8601",
  "deviceId": "string"
}
```

#### Response

```json
{
  "preferences": "UserPreferences",
  "conflicts": [
    {
      "path": "string[]",
      "serverValue": "any",
      "clientValue": "any",
      "resolution": "server | client | merged"
    }
  ],
  "syncTimestamp": "ISO8601"
}
```

## Offline Sync

### Sync Operations
```http
POST /api/sync
```

Sincroniza operaciones pendientes.

#### Request Body

```json
{
  "operations": [
    {
      "type": "document | annotation | preference",
      "action": "create | update | delete",
      "data": "any",
      "timestamp": "ISO8601",
      "deviceId": "string",
      "priority": "CRITICAL | HIGH | NORMAL"
    }
  ],
  "lastSyncTimestamp": "ISO8601"
}
```

#### Response

```json
{
  "success": "boolean",
  "conflicts": [
    {
      "operation": "SyncOperation",
      "serverState": "any",
      "resolution": "client | server | merge",
      "mergedData": "any?"
    }
  ],
  "syncTimestamp": "ISO8601"
}
```

## Códigos de Error

| Código | Descripción                    |
|--------|--------------------------------|
| 400    | DEVICE_ID_REQUIRED            |
| 404    | THUMBNAIL_NOT_FOUND           |
| 500    | PREFERENCES_ERROR             |
| 500    | SYNC_ERROR                    |

## Rate Limiting

- Thumbnails: 100 requests/min
- Preferences: 60 requests/min
- Sync: 30 requests/min

## Notas

1. Todas las respuestas incluyen un `trace-id` en los headers
2. Los timestamps deben estar en formato ISO8601
3. Las URLs de miniaturas expiran en 1 hora
4. El caché de miniaturas expira en 7 días
