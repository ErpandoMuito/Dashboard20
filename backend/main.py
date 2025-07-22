from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
import os
import sys
import json
from datetime import datetime
import httpx
from urllib.parse import quote
from pydantic import BaseModel
from app.api import estoque
from app.core.config import settings

# Adicionar o diretório teste3 ao path para poder importar
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'teste3', 'backend'))

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

# ===============================
# MODELOS PARA OS TESTES
# ===============================
class EntradaEstoque(BaseModel):
    codigo: str
    quantidade: int
    observacao: str = ""

# ===============================
# ROTAS TESTE1 - Estoque Minimalista
# ===============================
@app.get("/teste1/api/v2/health")
async def teste1_health():
    return {"status": "ok", "minimalista": True}

@app.get("/teste1/api/v2/estoque/produto/{codigo}")
async def teste1_buscar_produto(codigo: str):
    token = os.getenv("TINY_API_TOKEN", "")
    if not token:
        raise HTTPException(status_code=500, detail="Token não configurado")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.tiny.com.br/api2/produto.obter.php",
            data={
                "token": token,
                "formato": "json",
                "codigo": codigo
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        data = response.json()
        if data["retorno"]["status"] == "OK":
            produto = data["retorno"]["produto"]
            return {
                "codigo": produto.get("codigo", ""),
                "nome": produto.get("nome", ""),
                "estoque": float(produto.get("estoqueAtual", 0)),
                "unidade": produto.get("unidade", "UN")
            }
        else:
            raise HTTPException(status_code=404, detail="Produto não encontrado")

@app.post("/teste1/api/v2/estoque/entrada")
async def teste1_entrada_estoque(entrada: EntradaEstoque):
    produto = await teste1_buscar_produto(entrada.codigo)
    novo_estoque = produto["estoque"] + entrada.quantidade
    
    if novo_estoque < 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Estoque insuficiente. Disponível: {produto['estoque']}"
        )
    
    token = os.getenv("TINY_API_TOKEN", "")
    async with httpx.AsyncClient() as client:
        produto_xml = f"""<produto>
            <codigo>{entrada.codigo}</codigo>
            <estoqueAtual>{novo_estoque}</estoqueAtual>
        </produto>"""
        
        response = await client.post(
            "https://api.tiny.com.br/api2/produto.alterar.php",
            data={
                "token": token,
                "formato": "json",
                "produto": quote(produto_xml)
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        data = response.json()
        if data["retorno"]["status"] == "OK":
            return {
                "sucesso": True,
                "estoque_anterior": produto["estoque"],
                "estoque_novo": novo_estoque,
                "observacao": entrada.observacao
            }
        else:
            raise HTTPException(status_code=400, detail="Erro ao atualizar estoque")

# ===============================
# ROTAS TESTE2 - Debug System
# ===============================
@app.get("/teste2/debug/env")
async def teste2_debug_env():
    env_vars = {}
    for key, value in os.environ.items():
        if any(sensitive in key.upper() for sensitive in ['TOKEN', 'SECRET', 'PASSWORD', 'KEY']):
            env_vars[key] = value[:4] + '*' * (len(value) - 4) if len(value) > 4 else '***'
        else:
            env_vars[key] = value
    
    return {
        "environment_variables": env_vars,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/teste2/api/health")
async def teste2_health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "debug_mode": True
    }

# ===============================
# ROTAS TESTE5 - Hacker API
# ===============================
@app.get("/teste5/api/health")
async def teste5_health():
    return {
        "api": "online",
        "timestamp": datetime.now().isoformat(),
        "hacker_mode": True
    }

@app.get("/teste5/api/dashboard")
async def teste5_dashboard():
    return {
        "metricas": {
            "total_notas": 1234,
            "faturamento_mes": 150000.00,
            "pedidos_pendentes": 45,
            "produtos_estoque": 789
        },
        "graficos": {
            "vendas_semana": [
                {"dia": "Seg", "valor": 15000},
                {"dia": "Ter", "valor": 22000},
                {"dia": "Qua", "valor": 18000},
                {"dia": "Qui", "valor": 25000},
                {"dia": "Sex", "valor": 30000}
            ]
        },
        "timestamp": datetime.now().isoformat()
    }

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
    # Montar todos os arquivos estáticos
    app.mount("/static", StaticFiles(directory="./static/static"), name="static")

# ===============================
# ROTAS PARA SERVIR OS HTMLs DOS TESTES
# ===============================
@app.get("/teste1")
async def serve_teste1():
    teste1_html = os.path.join(os.path.dirname(__file__), "..", "teste1", "index.html")
    if os.path.exists(teste1_html):
        return FileResponse(teste1_html)
    return JSONResponse({"error": "Teste1 HTML não encontrado"}, status_code=404)

@app.get("/teste2")
async def serve_teste2():
    teste2_html = os.path.join(os.path.dirname(__file__), "..", "teste2", "static", "index.html")
    if os.path.exists(teste2_html):
        return FileResponse(teste2_html)
    return JSONResponse({"error": "Teste2 HTML não encontrado"}, status_code=404)

@app.get("/teste3")
async def serve_teste3():
    # Teste3 tem frontend React complexo - vamos servir um HTML simples por enquanto
    return JSONResponse({
        "message": "Teste3 - Dashboard completo",
        "status": "Em desenvolvimento", 
        "api_endpoints": ["/teste3/api/health", "/teste3/api/notas"]
    })

@app.get("/teste4")
async def serve_teste4():
    return JSONResponse({
        "message": "Teste4 - Sistema avançado", 
        "status": "Em desenvolvimento",
        "features": ["Tailwind", "PostgreSQL", "Celery"]
    })

@app.get("/teste5")
async def serve_teste5():
    teste5_html = os.path.join(os.path.dirname(__file__), "..", "teste5", "index.html")
    if os.path.exists(teste5_html):
        return FileResponse(teste5_html)
    return JSONResponse({
        "message": "Teste5 - Hacker API",
        "status": "API funcionando",
        "endpoints": ["/teste5/api/health", "/teste5/api/dashboard"]
    })

# Servir o app React principal
@app.get("/")
@app.get("/estoque")
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str = ""):
    # Se for uma rota de API, retornar 404
    if full_path.startswith("api/"):
        return {"detail": "Not Found"}
    
    # Se for uma rota de teste, já foi tratada acima
    if full_path.startswith("teste"):
        return {"detail": "Not Found"}
    
    # Servir o React app se existe
    if os.path.exists("./static/index.html"):
        return FileResponse('./static/index.html')
    
    # Senão, mostrar info da API
    return JSONResponse({
        "message": "Dashboard Estoque API v2.0",
        "status": "online",
        "tests": ["/teste1", "/teste2", "/teste3", "/teste4", "/teste5"],
        "api": ["/api/health", "/api/v2/estoque"]
    })

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)