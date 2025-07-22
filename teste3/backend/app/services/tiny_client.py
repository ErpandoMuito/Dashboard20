import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import Optional, Dict, Any, List
import logging
from urllib.parse import urlencode
import json
from ..core.config import settings

logger = logging.getLogger(__name__)

class TinyAPIClient:
    """Cliente robusto para API Tiny com retry automático"""
    
    def __init__(self):
        self.base_url = settings.tiny_api_base_url
        self.token = settings.tiny_api_token
        self.timeout = httpx.Timeout(settings.tiny_api_timeout)
        
    @retry(
        stop=stop_after_attempt(settings.tiny_api_max_retries),
        wait=wait_exponential(multiplier=settings.tiny_api_retry_delay, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError))
    )
    async def _make_request(
        self, 
        endpoint: str, 
        params: Dict[str, Any],
        method: str = "POST"
    ) -> Dict[str, Any]:
        """Faz requisição com retry automático"""
        url = f"{self.base_url}/{endpoint}"
        
        # Adiciona token aos parâmetros
        params["token"] = self.token
        params["formato"] = "JSON"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                if method == "POST":
                    # Tiny API espera form-encoded
                    response = await client.post(
                        url,
                        data=urlencode(params),
                        headers={"Content-Type": "application/x-www-form-urlencoded"}
                    )
                else:
                    response = await client.get(url, params=params)
                
                response.raise_for_status()
                
                # Parse response
                data = response.json()
                
                # Verifica erro da API
                if data.get("retorno", {}).get("status") == "Erro":
                    error_msg = data["retorno"].get("erros", [{}])[0].get("erro", "Erro desconhecido")
                    logger.error(f"Erro Tiny API: {error_msg}")
                    raise Exception(f"Tiny API Error: {error_msg}")
                
                return data
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Erro na requisição Tiny: {e}")
                raise
    
    async def buscar_notas(
        self, 
        data_inicial: Optional[str] = None,
        data_final: Optional[str] = None,
        situacao: Optional[int] = None,
        pagina: int = 1
    ) -> Dict[str, Any]:
        """Busca notas fiscais com fallback"""
        try:
            params = {"pagina": pagina}
            
            if data_inicial:
                params["dataInicial"] = data_inicial
            if data_final:
                params["dataFinal"] = data_final
            if situacao:
                params["situacao"] = situacao
            
            return await self._make_request("notas.fiscais.pesquisar.php", params)
        except Exception as e:
            logger.error(f"Erro ao buscar notas: {e}")
            return {"retorno": {"status": "Erro", "erros": [{"erro": str(e)}]}}
    
    async def obter_nota(self, id_nota: str) -> Dict[str, Any]:
        """Obtém detalhes de uma nota específica"""
        try:
            params = {"id": id_nota}
            return await self._make_request("nota.fiscal.obter.php", params)
        except Exception as e:
            logger.error(f"Erro ao obter nota {id_nota}: {e}")
            return {"retorno": {"status": "Erro", "erros": [{"erro": str(e)}]}}
    
    async def buscar_produtos(self, pagina: int = 1) -> Dict[str, Any]:
        """Busca produtos"""
        try:
            params = {"pagina": pagina}
            return await self._make_request("produtos.pesquisar.php", params)
        except Exception as e:
            logger.error(f"Erro ao buscar produtos: {e}")
            return {"retorno": {"status": "Erro", "erros": [{"erro": str(e)}]}}
    
    async def obter_produto(self, id_produto: str) -> Dict[str, Any]:
        """Obtém detalhes de um produto"""
        try:
            params = {"id": id_produto}
            return await self._make_request("produto.obter.php", params)
        except Exception as e:
            logger.error(f"Erro ao obter produto {id_produto}: {e}")
            return {"retorno": {"status": "Erro", "erros": [{"erro": str(e)}]}}

# Singleton instance
tiny_client = TinyAPIClient()