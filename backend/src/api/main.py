from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import uvicorn

from src.agents.judge import JudgeAgent
from src.agents.secretary import SecretaryAgent
from src.agents.prosecutor import ProsecutorAgent
from src.agents.defender import DefenderAgent

app = FastAPI(title="First Court API")

@app.get("/oauth2callback")
async def oauth2callback(code: str, state: str):
    """Endpoint para manejar el callback de OAuth2 de Google"""
    try:
        # Almacenar el código de autorización de forma segura
        # Este código será usado por los clientes de Google para obtener tokens
        return {"message": "Autorización exitosa. Puede cerrar esta ventana."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
judge = JudgeAgent()
secretary = SecretaryAgent()
prosecutor = ProsecutorAgent()
defender = DefenderAgent()

@app.get("/")
async def root():
    return {"message": "First Court API is running"}

@app.post("/api/cases/analyze")
async def analyze_case(case_data: Dict[str, Any]):
    try:
        # Get analysis from each agent
        judge_analysis = await judge.analyze_case(case_data)
        prosecutor_analysis = await prosecutor.analyze_case(case_data)
        defender_analysis = await defender.analyze_case(case_data)
        
        return {
            "judge_analysis": judge_analysis,
            "prosecutor_analysis": prosecutor_analysis,
            "defender_analysis": defender_analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/hearings/schedule")
async def schedule_hearing(hearing_data: Dict[str, Any]):
    try:
        return await secretary.schedule_hearing(hearing_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
