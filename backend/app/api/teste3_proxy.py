from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
import httpx
import logging
import os

logger = logging.getLogger(__name__)

router = APIRouter()

# URL do backend do teste3 - pode ser configurado via variável de ambiente
TESTE3_BACKEND_URL = os.getenv("TESTE3_BACKEND_URL", "http://localhost:8003")

# Cliente HTTP assíncrono
client = httpx.AsyncClient(timeout=30.0)

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_to_teste3(path: str, request: Request):
    """Proxy reverso para o backend do teste3"""
    
    # Construir URL completa
    url = f"{TESTE3_BACKEND_URL}/api/{path}"
    
    # Preparar headers
    headers = dict(request.headers)
    headers.pop("host", None)  # Remover host header
    
    try:
        # Fazer a requisição para o backend do teste3
        response = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=await request.body() if request.method in ["POST", "PUT", "PATCH"] else None,
            params=dict(request.query_params)
        )
        
        # Retornar a resposta
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
    except httpx.ConnectError:
        logger.error(f"Não foi possível conectar ao backend do teste3: {url}")
        return JSONResponse(
            status_code=503,
            content={"detail": "Serviço teste3 indisponível"}
        )
    except Exception as e:
        logger.error(f"Erro ao fazer proxy para teste3: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Erro interno do servidor"}
        )