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

# Servir archivos estáticos de React (después del build)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Catch-all route para React Router
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        file_path = os.path.join("static", full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse("static/index.html")