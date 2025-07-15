# Azure deployment with build
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# API routes
@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "FastAPI + React"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from FastAPI!"}

# Servir archivos estáticos de React
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