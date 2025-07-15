# main.py - Versión actualizada para estructura modular
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Agregar el directorio actual al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Crear instancia de FastAPI primero
app = FastAPI(
    title="LunaJoy Matching Engine",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Intentar importar los módulos
USE_MODULAR = False
try:
    from app.config import settings
    from app.api.routes import health, match, user
    USE_MODULAR = True
    print("✅ Módulos cargados correctamente")
except ImportError as e:
    print(f"⚠️ Módulos no encontrados, usando rutas básicas: {e}")

# Si tenemos la estructura modular, usar los routers
if USE_MODULAR:
    # Incluir routers de la nueva estructura
    app.include_router(health.router, prefix="/api", tags=["health"])
    app.include_router(match.router, prefix="/api/v1", tags=["matching"])
    app.include_router(user.router, prefix="/api/v1", tags=["users"])
else:
    # Mantener las rutas actuales mientras migramos
    @app.get("/api/health")
    def health_check():
        return {"status": "healthy", "service": "FastAPI + React"}

    @app.get("/api/hello")
    def hello():
        return {"message": "Hello from FastAPI!"}

# Endpoint raíz de la API
@app.get("/api")
def api_root():
    return {
        "message": "LunaJoy Matching Engine API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "matching": "/api/v1/match",
            "users": "/api/v1/users",
            "interactions": "/api/v1/interactions"
        } if USE_MODULAR else {
            "health": "/api/health",
            "message": "Full API coming soon"
        }
    }

# Servir archivos estáticos de React (sin cambios)
if os.path.exists("static"):
    # Montar la subcarpeta static/static en la ruta /static
    if os.path.exists("static/static"):
        app.mount("/static", StaticFiles(directory="static/static"), name="static")
    
    # Servir index.html para las rutas raíz
    @app.get("/")
    async def serve_react_root():
        return FileResponse("static/index.html")
    
    # Catch-all route para React Router
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        # Primero intentar servir archivos estáticos directamente
        file_path = os.path.join("static", full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        # Si no existe, servir index.html para React Router
        return FileResponse("static/index.html")