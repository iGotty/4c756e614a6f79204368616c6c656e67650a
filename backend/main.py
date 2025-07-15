# main.py - Backend API Only
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Startup information
print("🚀 Starting LunaJoy API Backend...")
print(f"📍 Working directory: {os.getcwd()}")
print(f"📂 Directory contents: {os.listdir('.')}")

# Add the current directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create FastAPI instance
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
        "http://localhost:3000",  # For local development
        "http://localhost:3001",  # Alternate port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attempt to import modules
USE_MODULAR = False
try:
    from app.config import settings
    from app.api.routes import health, match, user, clinician, interaction, system
    from app.services.data_loader import data_loader
    USE_MODULAR = True
    print("✅ Modules loaded successfully")
    
    # Load data on startup
    print("📊 Loading data...")
    data_loader.load_all_data()
    stats = data_loader.get_stats()
    print(f"📈 Data loaded: {stats}")
    
except ImportError as e:
    print(f"⚠️ Modules not found, using basic routes: {e}")

# Use routers if modular structure is available
if USE_MODULAR:
    # Include all routers
    app.include_router(health.router, prefix="/api", tags=["health"])
    app.include_router(system.router, prefix="/api/system", tags=["system"])
    app.include_router(match.router, prefix="/api/v1", tags=["matching"])
    app.include_router(user.router, prefix="/api/v1", tags=["users"])
    app.include_router(clinician.router, prefix="/api/v1", tags=["clinicians"])
    app.include_router(interaction.router, prefix="/api/v1", tags=["interactions"])
else:
    # Basic fallback routes
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

# Root endpoint
@app.get("/")
def root():
    return {
        "name": "LunaJoy Matching Engine API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs",
        "health": "/api/health"
    }

# API root endpoint
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

print("✅ API Backend configured and ready")
print(f"📡 CORS configured for: {[origin for origin in app.middleware[1].kwargs['allow_origins']]}")