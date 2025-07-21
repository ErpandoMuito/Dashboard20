from fastapi import APIRouter, HTTPException
from typing import Optional
import logging
from ..models.estoque import EntradaEstoqueRequest, EntradaEstoqueResponse, ProdutoInfo
from ..services.tiny_api import tiny_client
from ..core.redis_client import redis_client

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/entrada", response_model=EntradaEstoqueResponse)
async def entrada_estoque(entrada: EntradaEstoqueRequest):
    """
    Realiza entrada de estoque no sistema
    """
    try:
        # 1. Buscar produto pelo código
        logger.info(f"Buscando produto: {entrada.codigo_produto}")
        produto = await tiny_client.buscar_produto_por_codigo(entrada.codigo_produto)
        
        if not produto:
            raise HTTPException(
                status_code=404,
                detail=f"Produto com código {entrada.codigo_produto} não encontrado"
            )
        
        produto_id = produto.get('id')
        produto_nome = produto.get('nome', 'Sem nome')
        
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
            await redis_client.set(cache_key, cache_data, ex=3600)  # Cache por 1 hora
        
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
        await redis_client.set(historico_key, historico_data)
        
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
        logger.error(f"Erro ao processar entrada de estoque: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao processar entrada: {str(e)}"
        )

@router.get("/produto/{codigo}", response_model=Optional[ProdutoInfo])
async def buscar_produto(codigo: str):
    """
    Busca informações do produto pelo código
    """
    try:
        # Tentar buscar do cache primeiro
        cache_key = f"estoque:produto:{codigo}"
        cached = await redis_client.get(cache_key)
        
        if cached:
            return ProdutoInfo(**cached)
        
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
        
        # Salvar no cache
        await redis_client.set(cache_key, produto_info.dict(), ex=3600)
        
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