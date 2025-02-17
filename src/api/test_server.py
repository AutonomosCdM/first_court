from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import jwt
from datetime import datetime, timedelta
from routes.canvas import router as canvas_router
from websockets.canvas_manager import canvas_manager, init_canvas_manager

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir rutas del canvas
app.include_router(canvas_router)

@app.get("/")
async def root():
    return FileResponse("static/index.html")

# Configuración JWT simple
JWT_SECRET = "dev-secret-do-not-use-in-production"
JWT_ALGORITHM = "HS256"

def create_token(user_id: str) -> str:
    payload = {
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

@app.get("/api/auth/token/{user_id}")
async def get_token(user_id: str):
    return {"token": create_token(user_id)}

# Inicializar canvas manager
init_canvas_manager()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9001)







if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9001)

