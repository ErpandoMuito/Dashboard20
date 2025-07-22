from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

router = APIRouter()

# Configurar diretórios base
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

# Função helper para servir React apps
def serve_react_app(teste_name: str):
    """Tenta servir um app React buildado ou retorna JSON de fallback"""
    
    # Caminhos possíveis para build do React
    build_paths = [
        PROJECT_ROOT / teste_name / "build" / "index.html",
        PROJECT_ROOT / teste_name / "dist" / "index.html",
        f"/app/{teste_name}/build/index.html",
        f"/app/dashboard-v2/{teste_name}/build/index.html"
    ]
    
    for build_path in build_paths:
        if Path(build_path).exists():
            return FileResponse(str(build_path), media_type="text/html")
    
    # Fallback para HTML simples
    html_paths = [
        PROJECT_ROOT / teste_name / "index.html",
        f"/app/{teste_name}/index.html",
        f"/app/dashboard-v2/{teste_name}/index.html"
    ]
    
    for html_path in html_paths:
        if Path(html_path).exists():
            return FileResponse(str(html_path), media_type="text/html")
    
    # Retornar info da API se não encontrar frontend
    endpoints_map = {
        "teste1": ["/teste1/api/v2/health", "/teste1/api/v2/estoque/produto/{codigo}"],
        "teste2": ["/teste2/api/health", "/teste2/debug/env"],
        "teste3": ["/teste3/api/health", "/teste3/api/notas"],
        "teste4": ["/teste4/api/health", "/teste4/api/produtos"],
        "teste5": ["/teste5/api/health", "/teste5/api/dashboard"]
    }
    
    return JSONResponse({
        "message": f"Dashboard {teste_name.upper()}",
        "status": "API funcionando - Frontend não encontrado",
        "endpoints": endpoints_map.get(teste_name, []),
        "hint": f"Execute 'cd {teste_name} && npm install && npm run build' para criar o frontend"
    })

# Rotas para cada teste
@router.get("/teste1")
async def serve_teste1():
    return serve_react_app("teste1")

@router.get("/teste2")
async def serve_teste2():
    return serve_react_app("teste2")

@router.get("/teste3")
async def serve_teste3():
    return serve_react_app("teste3")

@router.get("/teste4")
async def serve_teste4():
    return serve_react_app("teste4")

@router.get("/teste5")
async def serve_teste5():
    return serve_react_app("teste5")

# Montar arquivos estáticos para cada teste (se existirem)
def mount_static_files(app):
    """Monta os arquivos estáticos dos builds React"""
    
    for i in range(1, 6):
        teste_name = f"teste{i}"
        static_dir = PROJECT_ROOT / teste_name / "build" / "static"
        
        if static_dir.exists():
            app.mount(
                f"/{teste_name}/static",
                StaticFiles(directory=str(static_dir)),
                name=f"{teste_name}_static"
            )
            print(f"✅ Montado static files para {teste_name}")
        else:
            # Tentar diretório dist também
            dist_static = PROJECT_ROOT / teste_name / "dist" / "static"
            if dist_static.exists():
                app.mount(
                    f"/{teste_name}/static",
                    StaticFiles(directory=str(dist_static)),
                    name=f"{teste_name}_static"
                )
                print(f"✅ Montado dist files para {teste_name}")