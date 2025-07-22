from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
import logging
from ..core.redis_client import redis_manager
from ..services.tiny_client import tiny_client

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/")
async def listar_produtos(
    pagina: int = Query(1, ge=1),
    usar_cache: bool = Query(True)
) -> Dict[str, Any]:
    """Lista produtos com cache"""
    try:
        cache_key = f"produtos:lista:pagina:{pagina}"
        
        # Tenta cache
        if usar_cache:
            cached = await redis_manager.get(cache_key)
            if cached:
                return {
                    "status": "success",
                    "source": "cache",
                    "data": cached
                }
        
        # Busca da API
        response = await tiny_client.buscar_produtos(pagina=pagina)
        
        if response.get("retorno", {}).get("status") == "Erro":
            raise HTTPException(
                status_code=500,
                detail=response["retorno"]["erros"][0]["erro"]
            )
        
        produtos = response.get("retorno", {}).get("produtos", [])
        
        # Cache por 1 hora
        await redis_manager.set(cache_key, produtos, ex=3600)
        
        return {
            "status": "success",
            "source": "api",
            "data": produtos,
            "total": len(produtos),
            "pagina": pagina
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar produtos: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar produtos")

@router.get("/buscar")
async def buscar_produto(
    codigo: Optional[str] = Query(None),
    nome: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """Busca produto por código ou nome"""
    try:
        if not codigo and not nome:
            raise HTTPException(
                status_code=400,
                detail="Informe código ou nome do produto"
            )
        
        # Busca no cache
        if codigo:
            cache_key = f"produto:codigo:{codigo}"
            cached = await redis_manager.get(cache_key)
            if cached:
                return {
                    "status": "success",
                    "source": "cache",
                    "data": [cached]
                }
        
        # Busca produtos em cache por padrão
        produtos_encontrados = []
        
        # Scan de chaves de produto
        pattern = "produto:*"
        keys = await redis_manager.scan_keys(pattern, count=1000)
        
        if keys:
            produtos = await redis_manager.mget(keys)
            
            for key, produto in produtos.items():
                if not produto:
                    continue
                    
                # Filtra por código ou nome
                if codigo and produto.get("codigo") == codigo:
                    produtos_encontrados.append(produto)
                elif nome and nome.lower() in produto.get("nome", "").lower():
                    produtos_encontrados.append(produto)
        
        return {
            "status": "success",
            "source": "cache_search",
            "data": produtos_encontrados,
            "total": len(produtos_encontrados)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar produto: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar produto")

@router.get("/{id_produto}")
async def obter_produto(id_produto: str) -> Dict[str, Any]:
    """Obtém detalhes de um produto"""
    try:
        cache_key = f"produto:{id_produto}"
        
        # Cache
        cached = await redis_manager.get(cache_key)
        if cached:
            return {
                "status": "success",
                "source": "cache",
                "data": cached
            }
        
        # API
        response = await tiny_client.obter_produto(id_produto)
        
        if response.get("retorno", {}).get("status") == "Erro":
            raise HTTPException(
                status_code=404,
                detail="Produto não encontrado"
            )
        
        produto = response["retorno"]["produto"]
        
        # Salva no cache
        await redis_manager.set(cache_key, produto, ex=86400)  # 24h
        
        # Indexa por código
        if produto.get("codigo"):
            codigo_key = f"produto:codigo:{produto['codigo']}"
            await redis_manager.set(codigo_key, produto, ex=86400)
        
        return {
            "status": "success",
            "source": "api",
            "data": produto
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter produto {id_produto}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar produto")

@router.post("/sync")
async def sincronizar_produtos() -> Dict[str, Any]:
    """Sincroniza todos os produtos"""
    try:
        logger.info("Iniciando sincronização de produtos")
        
        todos_produtos = []
        pagina = 1
        total_paginas = 1
        
        while pagina <= total_paginas:
            response = await tiny_client.buscar_produtos(pagina=pagina)
            
            if response.get("retorno", {}).get("status") == "Erro":
                break
            
            retorno = response.get("retorno", {})
            produtos = retorno.get("produtos", [])
            
            if produtos:
                todos_produtos.extend(produtos)
            
            total_paginas = int(retorno.get("numero_paginas", 1))
            pagina += 1
            
            # Limite de segurança
            if pagina > 100:
                logger.warning("Limite de páginas atingido na sincronização")
                break
        
        # Salva produtos
        salvos = 0
        for produto_item in todos_produtos:
            produto = produto_item.get("produto", {})
            id_produto = produto.get("id")
            
            if id_produto:
                # Por ID
                await redis_manager.set(f"produto:{id_produto}", produto, ex=86400)
                
                # Por código
                if produto.get("codigo"):
                    await redis_manager.set(
                        f"produto:codigo:{produto['codigo']}", 
                        produto, 
                        ex=86400
                    )
                
                salvos += 1
        
        return {
            "status": "success",
            "message": "Sincronização concluída",
            "produtos_encontrados": len(todos_produtos),
            "produtos_salvos": salvos
        }
        
    except Exception as e:
        logger.error(f"Erro na sincronização de produtos: {e}")
        raise HTTPException(status_code=500, detail="Erro ao sincronizar produtos")