# main.py - Backend API Only
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Startup information
print("🚀 Starting LunaJoy API Backend...")
print(f"📍 Working directory: {os.getcwd()}")
print(f"📂 Directory contents: {os.listdir('.')}")

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, '..'))

# Create FastAPI instance
app = FastAPI(
    title="LunaJoy Matching Engine API",
    version="1.0.0",
    description="Backend API for LunaJoy mental health professional matching",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://lunajoymatchingengine.azurewebsites.net",
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attempt to import modules
USE_MODULAR = False
LOADED_ROUTES = []

try:
    from app.config import settings
    print("✅ Config loaded")
except ImportError as e:
    print(f"⚠️ Config not found: {e}")

try:
    from app.services.data_loader import data_loader
    print("✅ Data loader imported")
    
    # Load data on startup
    print("📊 Loading data...")
    data_loader.load_all_data()
    stats = data_loader.get_stats()
    print(f"📈 Data loaded: {stats}")
except ImportError as e:
    print(f"⚠️ Data loader not found: {e}")
    data_loader = None

# Import available routes
try:
    from app.api.routes import health
    app.include_router(health.router, prefix="/api", tags=["health"])
    LOADED_ROUTES.append("health")
    print("✅ Health routes loaded")
except ImportError as e:
    print(f"⚠️ Health routes not found: {e}")

try:
    from app.api.routes import match
    app.include_router(match.router, prefix="/api/v1", tags=["matching"])
    LOADED_ROUTES.append("match")
    print("✅ Match routes loaded")
except ImportError as e:
    print(f"⚠️ Match routes not found: {e}")

try:
    from app.api.routes import user
    app.include_router(user.router, prefix="/api/v1", tags=["users"])
    LOADED_ROUTES.append("user")
    print("✅ User routes loaded")
except ImportError as e:
    print(f"⚠️ User routes not found: {e}")

# Try to import optional routes that might exist
try:
    from app.api.routes import clinician
    app.include_router(clinician.router, prefix="/api/v1", tags=["clinicians"])
    LOADED_ROUTES.append("clinician")
    print("✅ Clinician routes loaded")
except ImportError:
    pass  # Optional

try:
    from app.api.routes import interaction
    app.include_router(interaction.router, prefix="/api/v1", tags=["interactions"])
    LOADED_ROUTES.append("interaction")
    print("✅ Interaction routes loaded")
except ImportError:
    pass  # Optional

try:
    from app.api.routes import system
    app.include_router(system.router, prefix="/api/system", tags=["system"])
    LOADED_ROUTES.append("system")
    print("✅ System routes loaded")
except ImportError:
    pass  # Optional

USE_MODULAR = len(LOADED_ROUTES) > 0

# Root endpoint
@app.get("/")
def root():
    return {
        "name": "LunaJoy Matching Engine API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs",
        "health": "/api/health",
        "modular": USE_MODULAR,
        "loaded_routes": LOADED_ROUTES
    }

# Fallback health endpoint if health router not loaded
if "health" not in LOADED_ROUTES:
    @app.get("/api/health")
    def health_check():
        return {
            "status": "healthy",
            "service": "LunaJoy API Backend",
            "version": "1.0.0",
            "modular": USE_MODULAR,
            "data_loaded": data_loader is not None
        }

# API info endpoint
@app.get("/api")
def api_root():
    endpoints = {
        "health": "/api/health",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }
    
    if "match" in LOADED_ROUTES:
        endpoints["matching"] = {
            "anonymous": "/api/v1/match",
            "basic": "/api/v1/match/basic",
            "complete": "/api/v1/match/complete",
            "explain": "/api/v1/match/explain",
            "stats": "/api/v1/match/stats"
        }
    
    if "user" in LOADED_ROUTES:
        endpoints["users"] = {
            "list": "/api/v1/users",
            "detail": "/api/v1/users/{user_id}",
            "login": "/api/v1/users/login",
            "history": "/api/v1/users/{user_id}/match-history"
        }
    
    if "clinician" in LOADED_ROUTES:
        endpoints["clinicians"] = {
            "list": "/api/v1/clinicians",
            "detail": "/api/v1/clinicians/{clinician_id}"
        }
    

    
    if "system" in LOADED_ROUTES:
        endpoints["system"] = {
            "info": "/api/system/info",
            "stats": "/api/system/stats",
            "ui-config": "/api/system/ui-config"
        }
    
    return {
        "message": "LunaJoy Matching Engine API",
        "version": "1.0.0",
        "modular": USE_MODULAR,
        "loaded_routes": LOADED_ROUTES,
        "endpoints": endpoints
    }

# System endpoints fallback
if "system" not in LOADED_ROUTES:
    @app.get("/api/system/ui-config")
    def ui_config():
        """Endpoint que el frontend necesita para las estadísticas"""
        return {
            "animated_stats": {
                "active_professionals": 500,
                "total_matches": 10000,
                "success_rate": 94,
                "states_covered": 50
            }
        }
    
    @app.get("/api/system/stats")
    def system_stats():
        if data_loader:
            return data_loader.get_stats()
        return {
            "clinicians": 0,
            "users": 0,
            "interactions": 0,
            "data_loaded": False
        }

print("✅ API Backend configured and ready")
print(f"📡 CORS configured for frontend")
print(f"📦 Loaded routes: {LOADED_ROUTES}")
print(f"🔧 Running in {'modular' if USE_MODULAR else 'basic'} mode")