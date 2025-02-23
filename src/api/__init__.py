"""
API Module.
Contains FastAPI routes and endpoint implementations.
"""

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app instance
app = FastAPI(
    title="First Court API",
    description="API for judicial process management with AI integration",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
v1_router = APIRouter(prefix="/api/v1")

# Import and include routers
# Example: from .routes import cases, documents
# v1_router.include_router(cases.router, prefix="/cases", tags=["cases"])
# v1_router.include_router(documents.router, prefix="/documents", tags=["documents"])

# Include versioned router
app.include_router(v1_router)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
