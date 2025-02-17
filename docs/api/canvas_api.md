# Canvas API Documentation

## REST Endpoints

### 1. Get Case Nodes
```http
GET /api/canvas/nodes/{case_id}
```
Returns all nodes for a specific case.

### 2. Get Case Edges
```http
GET /api/canvas/edges/{case_id}
```
Returns all edges (connections) for a specific case.

### 3. Create Node
```http
POST /api/canvas/nodes/{case_id}
```
Create a new node in the canvas.

Request body:
```json
{
  "type": "document",
  "position": {"x": 100, "y": 200},
  "data": {
    "title": "Document Title",
    "content": "Document content..."
  }
}
```

### 4. Create Edge
```http
POST /api/canvas/edges/{case_id}
```
Create a new connection between nodes.

Request body:
```json
{
  "source_id": "uuid-source",
  "target_id": "uuid-target",
  "type": "references",
  "data": {
    "label": "References"
  }
}
```

### 5. Update Layout
```http
PUT /api/canvas/layout/{case_id}
```
Update canvas layout information.

Request body:
```json
{
  "nodes": {
    "node-uuid-1": {"x": 100, "y": 200},
    "node-uuid-2": {"x": 300, "y": 400}
  },
  "zoom": 1.5,
  "pan": {"x": 0, "y": 0}
}
```

### 6. Get Canvas State
```http
GET /api/canvas/state/{case_id}
```
Get complete canvas state including nodes, edges, and layout.

## WebSocket API

### Connection
Connect to:
```
ws://your-domain/ws/canvas/{case_id}
```

### Events

#### Node Created
```json
{
  "type": "node_created",
  "data": {
    "node": {
      "id": "uuid",
      "type": "document",
      "position": {"x": 100, "y": 200},
      "data": {}
    }
  }
}
```

#### Edge Created
```json
{
  "type": "edge_created",
  "data": {
    "edge": {
      "id": "uuid",
      "source_id": "uuid-source",
      "target_id": "uuid-target",
      "type": "references"
    }
  }
}
```

#### Layout Updated
```json
{
  "type": "layout_updated",
  "data": {
    "nodes": {},
    "zoom": 1.0,
    "pan": {"x": 0, "y": 0}
  }
}
```

## Error Handling
All endpoints return standard HTTP status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Server Error

## Authentication
All endpoints require authentication via Bearer token:
```http
Authorization: Bearer your-jwt-token
```
