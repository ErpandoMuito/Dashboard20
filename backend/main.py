from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import os
import logging
from app.api import estoque

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Servir arquivos estáticos do frontend em produção
static_path = Path("static")
logger.info(f"Verificando pasta static: {static_path.absolute()}")
logger.info(f"Static existe: {static_path.exists()}")

if static_path.exists():
    # Listar conteúdo da pasta static
    logger.info(f"Conteúdo de static: {list(static_path.iterdir())}")
    
    # Verificar se existe a subpasta static/static
    static_static = static_path / "static"
    if static_static.exists():
        logger.info(f"Encontrada subpasta static/static com: {list(static_static.iterdir())}")
    
    # Montar arquivos estáticos na raiz também
    app.mount("/static", StaticFiles(directory="static/static"), name="static_files")
    app.mount("/js", StaticFiles(directory="static/static/js"), name="js")
    app.mount("/css", StaticFiles(directory="static/static/css"), name="css")
    
    # Servir arquivos da raiz static também
    @app.get("/static/{file_path:path}")
    async def serve_static(file_path: str):
        logger.info(f"Requisição para static: {file_path}")
        file = static_path / file_path
        if file.exists():
            return FileResponse(file)
        # Tentar na subpasta
        file = static_path / "static" / file_path
        if file.exists():
            return FileResponse(file)
        logger.warning(f"Arquivo não encontrado: {file_path}")
        return {"error": "Not found"}, 404
    
    # Catch-all para React Router
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        logger.info(f"Requisição para: {full_path}")
        
        # Se for uma rota da API, deixar passar
        if full_path.startswith("api/"):
            return {"error": "Not found"}, 404
            
        # Servir index.html para todas as outras rotas
        index_path = static_path / "index.html"
        if index_path.exists():
            logger.info(f"Servindo index.html de: {index_path}")
            return FileResponse(index_path)
        
        logger.error(f"index.html não encontrado em: {index_path}")
        return {"error": "Frontend not found"}, 404
else:
    logger.error(f"Pasta static não encontrada em: {static_path.absolute()}")

