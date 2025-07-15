# main_simple.py - Para probar que el servidor funciona
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LunaJoy Test")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "LunaJoy API is running"}

@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "LunaJoy"}

# Probar si podemos importar los módulos
try:
    from app.api.routes import health as health_router
    from app.api.routes import match as match_router
    
    app.include_router(health_router.router, prefix="/api", tags=["health"])
    app.include_router(match_router.router, prefix="/api/v1", tags=["matching"])
    
    @app.get("/api/status")
    def status():
        return {"modules": "loaded", "matching": "available"}
except Exception as e:
    @app.get("/api/status")
    def status():
        return {"modules": "error", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)