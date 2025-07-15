# main.py - Backend API Only
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Información de inicio
print("🚀 Iniciando LunaJoy API Backend...")
print(f"📍 Working directory: {os.getcwd()}")
print(f"📂 Directory contents: {os.listdir('.')}")

# Agregar el directorio actual al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Crear instancia de FastAPI
app = FastAPI(
    title="LunaJoy Matching Engine API",
    version="1.0.0",
    description="Backend API for LunaJoy mental health professional matching",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://lunajoymatchingengine.azurewebsites.net",
        "http://localhost:3000",  # Para desarrollo local
        "http://localhost:3001",  # Puerto alternativo
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Intentar importar los módulos
USE_MODULAR = False
try:
    from app.config import settings
    from app.api.routes import health, match, user, clinician, interaction, system
    from app.services.data_loader import data_loader
    USE_MODULAR = True
    print("✅ Módulos cargados correctamente")
    
    # Cargar datos al inicio
    print("📊 Cargando datos...")
    data_loader.load_all_data()
    stats = data_loader.get_stats()
    print(f"📈 Datos cargados: {stats}")
    
except ImportError as e:
    print(f"⚠️ Módulos no encontrados, usando rutas básicas: {e}")

# Si tenemos la estructura modular, usar los routers
if USE_MODULAR:
    # Incluir todos los routers
    app.include_router(health.router, prefix="/api", tags=["health"])
    app.include_router(system.router, prefix="/api/system", tags=["system"])
    app.include_router(match.router, prefix="/api/v1", tags=["matching"])
    app.include_router(user.router, prefix="/api/v1", tags=["users"])
    app.include_router(clinician.router, prefix="/api/v1", tags=["clinicians"])
    app.include_router(interaction.router, prefix="/api/v1", tags=["interactions"])
else:
    # Rutas básicas de fallback
    @app.get("/api/health")
    def health_check():
        return {
            "status": "healthy",
            "service": "LunaJoy API Backend",
            "version": "1.0.0"
        }
    
    @app.get("/api/system/info")
    def system_info():
        return {
            "environment": "production" if os.environ.get('WEBSITE_INSTANCE_ID') else "development",
            "modular": False,
            "message": "Running in basic mode"
        }

# Endpoint raíz
@app.get("/")
def root():
    return {
        "name": "LunaJoy Matching Engine API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs",
        "health": "/api/health"
    }

# Endpoint raíz de la API
@app.get("/api")
def api_root():
    return {
        "message": "LunaJoy Matching Engine API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "system": {
                "info": "/api/system/info",
                "stats": "/api/system/stats",
                "ui-config": "/api/system/ui-config"
            },
            "matching": {
                "anonymous": "/api/v1/match",
                "basic": "/api/v1/match/basic",
                "complete": "/api/v1/match/complete",
                "explain": "/api/v1/match/explain",
                "stats": "/api/v1/match/stats"
            },
            "users": {
                "list": "/api/v1/users",
                "detail": "/api/v1/users/{user_id}",
                "login": "/api/v1/users/login",
                "history": "/api/v1/users/{user_id}/match-history"
            },
            "clinicians": {
                "list": "/api/v1/clinicians",
                "detail": "/api/v1/clinicians/{clinician_id}"
            },
            "interactions": {
                "view": "/api/v1/interactions/view",
                "contact": "/api/v1/interactions/contact",
                "book": "/api/v1/interactions/book"
            }
        }
    }

print("✅ API Backend configurado y listo")
print(f"📡 CORS configurado para: {[origin for origin in app.middleware[1].kwargs['allow_origins']]}")  