from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os
from app.api import estoque
from app.core.config import settings

app = FastAPI(title="Dashboard Estoque API", version="2.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas da API
app.include_router(estoque.router, prefix="/api/v2/estoque", tags=["estoque"])

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# API info endpoint
@app.get("/api")
async def api_info():
    return {"message": "Dashboard Estoque API v2.0", "status": "online"}

# Servir arquivos estáticos do React em produção
if os.path.exists("./static"):
    # Montar os arquivos estáticos corretamente
    if os.path.exists("./static/static"):
        # Caso o React tenha criado static/static
        app.mount("/static", StaticFiles(directory="./static/static"), name="static")
    else:
        # Caso normal
        app.mount("/static", StaticFiles(directory="./static"), name="static")
    
    # Servir o app React
    @app.get("/")
    @app.get("/estoque")
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str = ""):
        # Se for uma rota de API, retornar 404
        if full_path.startswith("api/"):
            return {"detail": "Not Found"}
        
        # Sempre servir o index.html para o React Router
        return FileResponse('./static/index.html')

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)