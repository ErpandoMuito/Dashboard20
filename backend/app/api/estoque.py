from fastapi import APIRouter, HTTPException
from typing import Optional
import logging
from ..models.estoque import EntradaEstoqueRequest, EntradaEstoqueResponse, ProdutoInfo
from ..services.tiny_api import tiny_client
from ..core.redis_client import redis_client
from ..services.cache_produtos import cache_produtos

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/entrada", response_model=EntradaEstoqueResponse)
async def entrada_estoque(entrada: EntradaEstoqueRequest):
    """
    Realiza entrada de estoque no sistema
    """
    try:
        # 1. Buscar produto pelo código (primeiro no cache)
        logger.info(f"Buscando produto: {entrada.codigo_produto}")
        
        # Tentar cache primeiro (muito mais rápido!)
        produto_id = await cache_produtos.obter_id_por_codigo(entrada.codigo_produto)
        
        if not produto_id:
            raise HTTPException(
                status_code=404,
                detail=f"Produto com código {entrada.codigo_produto} não encontrado"
            )
        
        # Obter dados completos do produto
        produto = await cache_produtos.obter_produto(entrada.codigo_produto)
        produto_nome = produto.get('nome', 'Sem nome') if produto else entrada.codigo_produto
        
        # 2. Alterar estoque no Tiny
        logger.info(f"Alterando estoque do produto {produto_id}: +{entrada.quantidade}")
        resultado = await tiny_client.alterar_estoque(
            produto_id=produto_id,
            quantidade=entrada.quantidade,
            tipo=entrada.tipo,
            deposito=entrada.deposito,
            observacoes=entrada.descricao or f"Entrada via Dashboard - {entrada.data.strftime('%d/%m/%Y %H:%M')}"
        )
        
        if not resultado['success']:
            raise HTTPException(
                status_code=400,
                detail=resultado['message']
            )
        
        # 3. Buscar estoque atualizado
        estoque_info = await tiny_client.obter_estoque(produto_id)
        saldo_atual = None
        
        if estoque_info:
            saldo_atual = int(float(estoque_info.get('produto', {}).get('saldo', '0')))
            
            # 4. Salvar no cache Redis
            cache_key = f"estoque:produto:{entrada.codigo_produto}"
            cache_data = {
                'produto_id': produto_id,
                'codigo': entrada.codigo_produto,
                'nome': produto_nome,
                'saldo': saldo_atual,
                'ultima_atualizacao': entrada.data.isoformat()
            }
            try:
                await redis_client.set(cache_key, cache_data, ex=3600)  # Cache por 1 hora
            except Exception as e:
                logger.debug(f"Não foi possível cachear produto: {e}")
        
        # 5. Registrar operação no histórico
        historico_key = f"estoque:historico:{entrada.codigo_produto}:{entrada.data.timestamp()}"
        historico_data = {
            'tipo': 'entrada',
            'quantidade': entrada.quantidade,
            'deposito': entrada.deposito,
            'descricao': entrada.descricao,
            'data': entrada.data.isoformat(),
            'usuario': 'sistema'  # Futuramente pegar do auth
        }
        try:
            await redis_client.set(historico_key, historico_data)
        except Exception as e:
            logger.debug(f"Não foi possível salvar histórico: {e}")
        
        return EntradaEstoqueResponse(
            success=True,
            message=f"Entrada de {entrada.quantidade} unidades realizada com sucesso para o produto {produto_nome}",
            produto_id=produto_id,
            saldo_atual=saldo_atual,
            tiny_response=resultado.get('response')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erro detalhado ao processar entrada de estoque")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao processar entrada: {str(e)}"
        )

@router.post("/saida", response_model=EntradaEstoqueResponse)
async def saida_estoque(saida: EntradaEstoqueRequest):
    """
    Realiza saída de estoque no sistema
    """
    try:
        # 1. Buscar produto pelo código
        logger.info(f"Buscando produto: {saida.codigo_produto}")
        produto = await tiny_client.buscar_produto_por_codigo(saida.codigo_produto)

        if not produto:
            raise HTTPException(
                status_code=404,
                detail=f"Produto com código {saida.codigo_produto} não encontrado"
            )

        produto_id = produto.get('id')
        produto_nome = produto.get('nome', 'Sem nome')

        # 2. Alterar estoque no Tiny (subtraindo a quantidade)
        logger.info(f"Alterando estoque do produto {produto_id}: -{saida.quantidade}")
        resultado = await tiny_client.alterar_estoque(
            produto_id=produto_id,
            quantidade=saida.quantidade,
            tipo='S',  # 'S' para saída
            deposito=saida.deposito,
            observacoes=saida.descricao or f"Saída via Dashboard - {saida.data.strftime('%d/%m/%Y %H:%M')}"
        )

        if not resultado['success']:
            raise HTTPException(
                status_code=400,
                detail=resultado['message']
            )

        # 3. Buscar estoque atualizado
        estoque_info = await tiny_client.obter_estoque(produto_id)
        saldo_atual = None

        if estoque_info:
            saldo_atual = int(float(estoque_info.get('produto', {}).get('saldo', '0')))

            # 4. Salvar no cache Redis
            cache_key = f"estoque:produto:{saida.codigo_produto}"
            cache_data = {
                'produto_id': produto_id,
                'codigo': saida.codigo_produto,
                'nome': produto_nome,
                'saldo': saldo_atual,
                'ultima_atualizacao': saida.data.isoformat()
            }
            try:
                await redis_client.set(cache_key, cache_data, ex=3600)
            except Exception as e:
                logger.debug(f"Não foi possível cachear produto: {e}")

        # 5. Registrar operação no histórico
        historico_key = f"estoque:historico:{saida.codigo_produto}:{saida.data.timestamp()}"
        historico_data = {
            'tipo': 'saida',
            'quantidade': saida.quantidade,
            'deposito': saida.deposito,
            'descricao': saida.descricao,
            'data': saida.data.isoformat(),
            'usuario': 'sistema'
        }
        try:
            await redis_client.set(historico_key, historico_data)
        except Exception as e:
            logger.debug(f"Não foi possível salvar histórico: {e}")

        return EntradaEstoqueResponse(
            success=True,
            message=f"Saída de {saida.quantidade} unidades realizada com sucesso para o produto {produto_nome}",
            produto_id=produto_id,
            saldo_atual=saldo_atual,
            tiny_response=resultado.get('response')
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erro detalhado ao processar saida de estoque")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao processar saída: {str(e)}"
        )

@router.get("/produto/{codigo}", response_model=Optional[ProdutoInfo])
async def buscar_produto(codigo: str):
    """
    Busca informações do produto pelo código
    """
    try:
        # Tentar buscar do cache primeiro (se Redis estiver disponível)
        cache_key = f"estoque:produto:{codigo}"
        try:
            cached = await redis_client.get(cache_key)
            if cached:
                return ProdutoInfo(**cached)
        except Exception as e:
            logger.debug(f"Cache não disponível: {e}")
        
        # Buscar do Tiny
        produto = await tiny_client.buscar_produto_por_codigo(codigo)
        
        if not produto:
            raise HTTPException(
                status_code=404,
                detail=f"Produto {codigo} não encontrado"
            )
        
        # Buscar estoque
        estoque_info = await tiny_client.obter_estoque(produto['id'])
        saldo = 0
        
        if estoque_info:
            saldo = int(float(estoque_info.get('produto', {}).get('saldo', '0')))
        
        produto_info = ProdutoInfo(
            id=produto['id'],
            codigo=codigo,
            nome=produto.get('nome', 'Sem nome'),
            unidade=produto.get('unidade', 'UN'),
            saldo=saldo
        )
        
        # Salvar no cache (se Redis estiver disponível)
        try:
            await redis_client.set(cache_key, produto_info.dict(), ex=3600)
        except Exception as e:
            logger.debug(f"Não foi possível cachear: {e}")
        
        return produto_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar produto: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar produto: {str(e)}"
        )

@router.get("/historico/{codigo}")
async def historico_produto(codigo: str, limit: int = 10):
    """
    Retorna histórico de movimentações do produto
    """
    # TODO: Implementar busca de histórico do Redis
    return {
        "codigo": codigo,
        "historico": [],
        "message": "Funcionalidade em desenvolvimento"
    }

@router.post("/cache/popular")
async def popular_cache_produtos(inicio: int = 1, fim: int = 999):
    """
    Popula cache com produtos PH
    """
    try:
        logger.info(f"Iniciando população de cache: PH-{inicio:03d} até PH-{fim:03d}")
        resultado = await cache_produtos.popular_cache_produtos_ph(inicio, fim)
        
        return {
            "success": True,
            "message": f"Cache populado com sucesso",
            "detalhes": resultado
        }
        
    except Exception as e:
        logger.error(f"Erro ao popular cache: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao popular cache: {str(e)}"
        )

@router.get("/cache/produtos")
async def listar_produtos_cacheados(prefixo: str = "PH"):
    """
    Lista produtos no cache
    """
    try:
        produtos = await cache_produtos.listar_produtos_cacheados(prefixo)
        
        return {
            "total": len(produtos),
            "produtos": produtos
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar cache: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar cache: {str(e)}"
        )

@router.delete("/cache")
async def limpar_cache_produtos(prefixo: Optional[str] = None):
    """
    Limpa cache de produtos
    """
    try:
        count = await cache_produtos.limpar_cache(prefixo)
        
        return {
            "success": True,
            "message": f"{count} chaves removidas do cache"
        }
        
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao limpar cache: {str(e)}"
        )