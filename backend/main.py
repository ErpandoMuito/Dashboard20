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

# Incluir rotas
app.include_router(estoque.router, prefix="/api/v2/estoque", tags=["estoque"])

@app.get("/")
async def root():
    return {"message": "Dashboard Estoque API v2.0", "status": "online"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Servir arquivos estáticos do React em produção
if os.path.exists("./static"):
    # Montar o diretório static inteiro, permitindo subdiretórios
    app.mount("/static", StaticFiles(directory="./static"), name="static")
    
    # Servir o app React para todas as rotas não-API
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        # Se for uma rota de API, deixar passar
        if full_path.startswith("api/"):
            return {"detail": "Not Found"}, 404
        
        # Verificar se é um arquivo estático
        static_file = os.path.join("./static", full_path)
        if os.path.exists(static_file) and os.path.isfile(static_file):
            return FileResponse(static_file)
        
        # Para qualquer outra rota, servir o index.html (React Router)
        return FileResponse('./static/index.html')

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)