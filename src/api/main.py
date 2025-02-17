from fastapi import FastAPI
from routes import ws, canvas

app = FastAPI(title="First Court API")

# Incluir routers
app.include_router(ws.router)
app.include_router(canvas.router)

@app.get("/")
async def root():
    return {"message": "First Court API"}
