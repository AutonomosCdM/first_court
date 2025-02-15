"""API routes package."""
from fastapi import APIRouter
from .documents import router as documents_router

api_router = APIRouter()
api_router.include_router(documents_router)
