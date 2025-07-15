# app/api/routes/health.py
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health")
def health_check():
    """
    Health check endpoint para verificar el estado del servicio.
    """
    return {
        "status": "healthy",
        "service": "LunaJoy Matching Engine",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/hello")
def hello():
    """
    Endpoint de prueba simple.
    """
    return {"message": "Hello from LunaJoy Matching Engine!"}