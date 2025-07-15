# app/config.py
from typing import List
import os

class Settings:
    """
    Configuración central de la aplicación.
    Por ahora, valores hardcodeados. Luego migraremos a pydantic-settings.
    """
    # API Settings
    APP_NAME: str = "LunaJoy Matching Engine"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]  # En producción, especificar dominios
    
    # Matching Engine Settings (para el futuro)
    DEFAULT_RESULTS_LIMIT: int = 10
    MAX_RESULTS_LIMIT: int = 50
    
    # Performance Settings
    RESPONSE_TIME_TARGET_MS: int = 200
    
    # Feature Flags
    ENABLE_DIVERSITY_BOOST: bool = True
    ENABLE_NEW_CLINICIAN_BOOST: bool = True
    NEW_CLINICIAN_DAYS: int = 30
    NEW_CLINICIAN_BOOST_FACTOR: float = 1.1
    
    # Load Balancing
    OVERLOAD_THRESHOLD: float = 0.85  # 85% capacity
    OVERLOAD_PENALTY_FACTOR: float = 0.7
    
    # Scoring Weights para usuarios anónimos urgentes
    WEIGHTS_ANONYMOUS_URGENT: dict = {
        "availability": 0.40,
        "insurance": 0.20,
        "specialties": 0.20,
        "load_balance": 0.10,
        "preferences": 0.10
    }
    
    # Scoring Weights para usuarios anónimos flexibles
    WEIGHTS_ANONYMOUS_FLEXIBLE: dict = {
        "availability": 0.25,
        "insurance": 0.25,
        "specialties": 0.25,
        "load_balance": 0.15,
        "preferences": 0.10
    }

# Instancia global de configuración
settings = Settings()