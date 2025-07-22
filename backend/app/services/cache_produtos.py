"""
Serviço de cache de produtos PH no Redis
Mantém um índice rápido de código -> ID para produtos PH
"""
import json
from typing import Dict, Any, Optional, List
from ..core.redis_client import redis_client
from .tiny_api import tiny_client
import logging

logger = logging.getLogger(__name__)

class CacheProdutos:
    """Gerencia cache de produtos no Redis"""
    
    def __init__(self):
        self.prefix = "produto:"
        self.index_prefix = "produto:index:"
        
    async def cachear_produto(self, produto: Dict[str, Any]) -> bool:
        """Cacheia um produto no Redis"""
        try:
            codigo = produto.get('codigo')
            produto_id = produto.get('id')
            
            if not codigo or not produto_id:
                return False
            
            # Salvar produto completo
            key = f"{self.prefix}{codigo}"
            await redis_client.set(key, produto, ex=86400)  # 24 horas
            
            # Criar índice código -> ID
            index_key = f"{self.index_prefix}{codigo}"
            await redis_client.set(index_key, produto_id, ex=86400)
            
            logger.info(f"Produto {codigo} cacheado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao cachear produto: {e}")
            return False
    
    async def obter_id_por_codigo(self, codigo: str) -> Optional[str]:
        """Obtém ID do produto pelo código (cache rápido)"""
        try:
            index_key = f"{self.index_prefix}{codigo}"
            produto_id = await redis_client.get(index_key)
            
            if produto_id:
                logger.debug(f"ID do produto {codigo} encontrado no cache: {produto_id}")
                return produto_id
            
            # Se não está no cache, buscar na API
            logger.info(f"Produto {codigo} não está no cache, buscando na API...")
            produto = await tiny_client.buscar_produto_por_codigo(codigo)
            
            if produto:
                # Cachear para próximas buscas
                await self.cachear_produto(produto)
                return produto.get('id')
                
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter ID do produto: {e}")
            return None
    
    async def obter_produto(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Obtém produto completo do cache ou API"""
        try:
            # Tentar cache primeiro
            key = f"{self.prefix}{codigo}"
            produto = await redis_client.get(key)
            
            if produto:
                logger.debug(f"Produto {codigo} encontrado no cache")
                return produto
            
            # Se não está no cache, buscar na API
            logger.info(f"Produto {codigo} não está no cache, buscando na API...")
            produto = await tiny_client.buscar_produto_por_codigo(codigo)
            
            if produto:
                # Cachear para próximas buscas
                await self.cachear_produto(produto)
                return produto
                
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter produto: {e}")
            return None
    
    async def popular_cache_produtos_ph(self, inicio: int = 1, fim: int = 999) -> Dict[str, Any]:
        """
        Popula cache com produtos PH-XXX
        Busca produtos de PH-001 até PH-999
        """
        logger.info(f"Iniciando população de cache PH-{inicio:03d} até PH-{fim:03d}")
        
        produtos_encontrados = 0
        produtos_cacheados = 0
        erros = 0
        
        for num in range(inicio, fim + 1):
            codigo = f"PH-{num}"
            
            try:
                # Verificar se já está no cache
                if await self.obter_id_por_codigo(codigo):
                    produtos_encontrados += 1
                    produtos_cacheados += 1
                    continue
                
                # Buscar na API
                produto = await tiny_client.buscar_produto_por_codigo(codigo)
                
                if produto:
                    produtos_encontrados += 1
                    if await self.cachear_produto(produto):
                        produtos_cacheados += 1
                        logger.info(f"✓ {codigo}: {produto.get('nome', 'Sem nome')}")
                    
            except Exception as e:
                logger.error(f"Erro ao processar {codigo}: {e}")
                erros += 1
            
            # Pequena pausa para não sobrecarregar API
            if num % 10 == 0:
                import asyncio
                await asyncio.sleep(0.5)
        
        resultado = {
            'total_buscados': fim - inicio + 1,
            'produtos_encontrados': produtos_encontrados,
            'produtos_cacheados': produtos_cacheados,
            'erros': erros
        }
        
        logger.info(f"População de cache concluída: {resultado}")
        return resultado
    
    async def salvar_produto_cache(self, codigo: str, produto_id: str) -> bool:
        """Salva ID do produto no cache"""
        try:
            chave = f"{self.prefix}{codigo}"
            await redis_client.set(chave, produto_id, ex=self.ttl)
            logger.info(f"Produto {codigo} (ID: {produto_id}) salvo no cache")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar produto no cache: {e}")
            return False
    
    async def listar_produtos_cacheados(self, prefixo: str = "PH") -> List[Dict[str, str]]:
        """Lista produtos cacheados com determinado prefixo"""
        try:
            produtos = []
            pattern = f"{self.prefix}{prefixo}*"
            
            # Usar scan para buscar chaves
            async for key in redis_client.scan_iter(match=pattern):
                produto = await redis_client.get(key)
                if produto:
                    produtos.append({
                        'codigo': produto.get('codigo'),
                        'nome': produto.get('nome'),
                        'id': produto.get('id')
                    })
            
            return sorted(produtos, key=lambda x: x['codigo'])
            
        except Exception as e:
            logger.error(f"Erro ao listar produtos: {e}")
            return []
    
    async def limpar_cache(self, prefixo: Optional[str] = None):
        """Limpa cache de produtos"""
        try:
            if prefixo:
                pattern = f"{self.prefix}{prefixo}*"
            else:
                pattern = f"{self.prefix}*"
            
            count = 0
            async for key in redis_client.scan_iter(match=pattern):
                await redis_client.delete(key)
                count += 1
            
            # Limpar índices também
            if prefixo:
                pattern = f"{self.index_prefix}{prefixo}*"
            else:
                pattern = f"{self.index_prefix}*"
                
            async for key in redis_client.scan_iter(match=pattern):
                await redis_client.delete(key)
                count += 1
            
            logger.info(f"Cache limpo: {count} chaves removidas")
            return count
            
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
            return 0

# Instância global
cache_produtos = CacheProdutos()