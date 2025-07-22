from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
from ..core.redis_client import redis_manager
from ..services.tiny_client import tiny_client
from ..models.nota import NotaFiscal

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/")
async def listar_notas(
    data_inicial: Optional[str] = Query(None, description="Data inicial (dd/mm/yyyy)"),
    data_final: Optional[str] = Query(None, description="Data final (dd/mm/yyyy)"),
    situacao: Optional[int] = Query(None, description="Situação da nota"),
    usar_cache: bool = Query(True, description="Usar cache Redis")
) -> Dict[str, Any]:
    """Lista notas fiscais com cache inteligente"""
    try:
        # Gera chave de cache
        cache_key = f"notas:lista:{data_inicial}:{data_final}:{situacao}"
        
        # Tenta buscar do cache
        if usar_cache:
            cached = await redis_manager.get(cache_key)
            if cached:
                logger.info(f"Notas recuperadas do cache: {cache_key}")
                return {
                    "status": "success",
                    "source": "cache",
                    "data": cached
                }
        
        # Busca da API Tiny
        logger.info(f"Buscando notas da API Tiny: {data_inicial} até {data_final}")
        
        todas_notas = []
        pagina = 1
        total_paginas = 1
        
        while pagina <= total_paginas:
            response = await tiny_client.buscar_notas(
                data_inicial=data_inicial,
                data_final=data_final,
                situacao=situacao,
                pagina=pagina
            )
            
            if response.get("retorno", {}).get("status") == "Erro":
                raise HTTPException(
                    status_code=500,
                    detail=response["retorno"]["erros"][0]["erro"]
                )
            
            retorno = response.get("retorno", {})
            notas = retorno.get("notas_fiscais", [])
            
            if notas:
                todas_notas.extend(notas)
            
            # Paginação
            total_paginas = int(retorno.get("numero_paginas", 1))
            pagina += 1
        
        # Salva no cache por 5 minutos
        await redis_manager.set(cache_key, todas_notas, ex=300)
        
        return {
            "status": "success",
            "source": "api",
            "data": todas_notas,
            "total": len(todas_notas)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar notas: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar notas fiscais")

@router.get("/{id_nota}")
async def obter_nota(id_nota: str) -> Dict[str, Any]:
    """Obtém detalhes de uma nota específica"""
    try:
        # Cache key
        cache_key = f"nota:detalhe:{id_nota}"
        
        # Tenta cache
        cached = await redis_manager.get(cache_key)
        if cached:
            return {
                "status": "success",
                "source": "cache",
                "data": cached
            }
        
        # Busca da API
        response = await tiny_client.obter_nota(id_nota)
        
        if response.get("retorno", {}).get("status") == "Erro":
            raise HTTPException(
                status_code=404,
                detail="Nota fiscal não encontrada"
            )
        
        nota = response["retorno"]["nota_fiscal"]
        
        # Cache por 1 hora
        await redis_manager.set(cache_key, nota, ex=3600)
        
        return {
            "status": "success",
            "source": "api",
            "data": nota
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter nota {id_nota}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar nota fiscal")

@router.post("/sync")
async def sincronizar_notas(
    dias: int = Query(7, description="Número de dias para sincronizar")
) -> Dict[str, Any]:
    """Sincroniza notas dos últimos N dias"""
    try:
        # Calcula datas
        data_final = datetime.now()
        data_inicial = data_final - timedelta(days=dias)
        
        # Formata para API Tiny
        data_inicial_str = data_inicial.strftime("%d/%m/%Y")
        data_final_str = data_final.strftime("%d/%m/%Y")
        
        logger.info(f"Sincronizando notas de {data_inicial_str} até {data_final_str}")
        
        # Busca notas
        resultado = await listar_notas(
            data_inicial=data_inicial_str,
            data_final=data_final_str,
            usar_cache=False  # Força busca na API
        )
        
        notas = resultado.get("data", [])
        
        # Salva individualmente no Redis
        salvos = 0
        for nota_item in notas:
            nota = nota_item.get("nota_fiscal", {})
            id_nota = nota.get("id")
            if id_nota:
                key = f"nota:{id_nota}"
                await redis_manager.set(key, nota, ex=86400)  # 24h
                salvos += 1
        
        return {
            "status": "success",
            "message": f"Sincronização concluída",
            "periodo": f"{data_inicial_str} até {data_final_str}",
            "notas_encontradas": len(notas),
            "notas_salvas": salvos
        }
        
    except Exception as e:
        logger.error(f"Erro na sincronização: {e}")
        raise HTTPException(status_code=500, detail="Erro ao sincronizar notas")