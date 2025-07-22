from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
import os
from urllib.parse import quote
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Dashboard Estoque API", version="2.0")

# CORS simples
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Token do Tiny
TINY_TOKEN = os.getenv("TINY_API_TOKEN", "")
TINY_URL = "https://api.tiny.com.br/api2"

# Validar token na inicialização
if not TINY_TOKEN:
    logger.error("TINY_API_TOKEN não configurado!")
    raise ValueError("TINY_API_TOKEN deve ser configurado nas variáveis de ambiente")

# Handler global de exceções para garantir resposta JSON
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Erro não tratado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor", "error": str(exc)}
    )

# Modelos simples
class EntradaEstoque(BaseModel):
    codigo: str
    quantidade: int
    observacao: str = ""

# Buscar produto
@app.get("/api/v2/estoque/produto/{codigo}")
async def buscar_produto(codigo: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TINY_URL}/produto.obter.php",
            data={
                "token": TINY_TOKEN,
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

# Entrada de estoque
@app.post("/api/v2/estoque/entrada")
async def entrada_estoque(entrada: EntradaEstoque):
    # Buscar produto atual
    produto = await buscar_produto(entrada.codigo)
    novo_estoque = produto["estoque"] + entrada.quantidade
    
    # Validar estoque negativo
    if novo_estoque < 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Estoque insuficiente. Disponível: {produto['estoque']}"
        )
    
    # Atualizar no Tiny
    async with httpx.AsyncClient() as client:
        produto_xml = f"""<produto>
            <codigo>{entrada.codigo}</codigo>
            <estoqueAtual>{novo_estoque}</estoqueAtual>
        </produto>"""
        
        response = await client.post(
            f"{TINY_URL}/produto.alterar.php",
            data={
                "token": TINY_TOKEN,
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

# Teste de API
@app.get("/api/v2/health")
async def health():
    return {"status": "ok", "minimalista": True}