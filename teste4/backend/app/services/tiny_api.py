"""
Service for integration with Tiny ERP API.
"""
import asyncio
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime
import urllib.parse
from app.core.config import settings
from app.core.logging import get_logger
from app.services.redis_service import redis_service

logger = get_logger(__name__)


class TinyAPIClient:
    """Client for Tiny ERP API integration."""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = settings.TINY_API_URL
        self.rate_limit_seconds = settings.TINY_RATE_LIMIT_SECONDS
        
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make HTTP request to Tiny API with rate limiting.
        """
        # Check rate limit
        last_request_key = "tiny:last_request"
        last_request = await redis_service.get(last_request_key)
        
        if last_request:
            elapsed = datetime.now().timestamp() - float(last_request)
            if elapsed < self.rate_limit_seconds:
                wait_time = self.rate_limit_seconds - elapsed
                logger.info(f"Rate limit: waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
        
        # Prepare request
        url = f"{self.base_url}/{endpoint}"
        params["token"] = self.token
        params["formato"] = "json"
        
        # Convert params to form data
        form_data = urllib.parse.urlencode(params)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    content=form_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=30.0
                )
                
                # Update last request timestamp
                await redis_service.set(last_request_key, str(datetime.now().timestamp()))
                
                response.raise_for_status()
                data = response.json()
                
                # Check for Tiny API errors
                if data.get("retorno", {}).get("status") == "Erro":
                    error_msg = data["retorno"].get("erros", [{}])[0].get("erro", "Unknown error")
                    raise Exception(f"Tiny API error: {error_msg}")
                
                return data
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling Tiny API: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calling Tiny API: {e}")
            raise
    
    async def listar_notas_fiscais(
        self,
        data_inicial: str,
        data_final: str,
        situacao: Optional[int] = None,
        pagina: int = 1
    ) -> Dict[str, Any]:
        """
        Lista notas fiscais do Tiny.
        
        Args:
            data_inicial: Data inicial (dd/mm/yyyy)
            data_final: Data final (dd/mm/yyyy)
            situacao: Situação da nota (6=Autorizada)
            pagina: Número da página
        """
        params = {
            "dataInicial": data_inicial,
            "dataFinal": data_final,
            "pagina": pagina
        }
        
        if situacao:
            params["situacao"] = situacao
            
        return await self._make_request("notas.fiscais.pesquisa.php", params)
    
    async def obter_nota_fiscal(self, nota_id: str) -> Dict[str, Any]:
        """
        Obtém detalhes de uma nota fiscal específica.
        """
        params = {"id": nota_id}
        return await self._make_request("nota.fiscal.obter.php", params)
    
    async def listar_produtos(self, pagina: int = 1) -> Dict[str, Any]:
        """
        Lista produtos cadastrados no Tiny.
        """
        params = {"pagina": pagina}
        return await self._make_request("produtos.pesquisa.php", params)
    
    async def obter_produto(self, produto_id: str) -> Dict[str, Any]:
        """
        Obtém detalhes de um produto específico.
        """
        params = {"id": produto_id}
        return await self._make_request("produto.obter.php", params)
    
    async def sync_notas_fiscais(
        self,
        data_inicial: str,
        data_final: str
    ) -> Dict[str, int]:
        """
        Sincroniza notas fiscais do período especificado.
        """
        logger.info(f"Syncing notas from {data_inicial} to {data_final}")
        
        synced_count = 0
        pagina = 1
        
        while True:
            try:
                # Get page of notas
                response = await self.listar_notas_fiscais(
                    data_inicial=data_inicial,
                    data_final=data_final,
                    situacao=6,  # Apenas autorizadas
                    pagina=pagina
                )
                
                retorno = response.get("retorno", {})
                notas = retorno.get("notas_fiscais", [])
                
                if not notas:
                    break
                
                # Process each nota
                for nota_wrapper in notas:
                    nota = nota_wrapper.get("nota_fiscal", {})
                    nota_id = nota.get("id")
                    
                    if not nota_id:
                        continue
                    
                    # Get full nota details
                    try:
                        nota_details = await self.obter_nota_fiscal(nota_id)
                        nota_completa = nota_details.get("retorno", {}).get("nota_fiscal", {})
                        
                        # Store in Redis
                        redis_key = f"nota:{nota_id}"
                        await redis_service.set(
                            redis_key,
                            nota_completa,
                            ex=2592000  # 30 days
                        )
                        
                        # Add to indices
                        await self._update_indices(nota_completa)
                        
                        synced_count += 1
                        
                    except Exception as e:
                        logger.error(f"Error syncing nota {nota_id}: {e}")
                        continue
                
                # Check if there are more pages
                if len(notas) < 100:  # Tiny returns max 100 per page
                    break
                    
                pagina += 1
                
            except Exception as e:
                logger.error(f"Error syncing page {pagina}: {e}")
                break
        
        logger.info(f"Sync completed: {synced_count} notas synced")
        return {"count": synced_count}
    
    async def _update_indices(self, nota: Dict[str, Any]) -> None:
        """
        Atualiza índices no Redis para busca rápida.
        """
        nota_id = nota.get("id")
        if not nota_id:
            return
            
        # Index by cliente
        cliente = nota.get("cliente", {}).get("nome", "").upper()
        if cliente:
            await redis_service.sadd(f"idx:cliente:{cliente}", nota_id)
        
        # Index by data
        data_emissao = nota.get("data_emissao")
        if data_emissao:
            await redis_service.sadd(f"idx:data:{data_emissao}", nota_id)
        
        # Index by produto
        itens = nota.get("itens", [])
        for item_wrapper in itens:
            item = item_wrapper.get("item", {})
            codigo = item.get("codigo")
            if codigo:
                await redis_service.sadd(f"idx:produto:{codigo}", nota_id)