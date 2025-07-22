import httpx
from urllib.parse import urlencode
from typing import Optional, Dict, Any
import json
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

class TinyAPIClient:
    def __init__(self):
        self.base_url = settings.TINY_API_BASE_URL
        self.token = settings.TINY_API_TOKEN
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Faz requisição para API do Tiny"""
        data['token'] = self.token
        data['formato'] = 'JSON'
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/{endpoint}",
                content=urlencode(data),
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Erro na requisição Tiny: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar resposta: {e}")
            raise
    
    async def buscar_produto_por_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Busca produto pelo código"""
        try:
            data = {'pesquisa': codigo}
            response = await self._make_request('produtos.pesquisa.php', data)
            
            if response.get('retorno', {}).get('status') == 'OK':
                produtos = response['retorno'].get('produtos', [])
                if produtos:
                    # Retorna o primeiro produto encontrado
                    return produtos[0]['produto']
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar produto {codigo}: {e}")
            return None
    
    async def obter_produto(self, produto_id: str) -> Optional[Dict[str, Any]]:
        """Obtém detalhes do produto pelo ID"""
        try:
            data = {'id': produto_id}
            response = await self._make_request('produto.obter.php', data)
            
            if response.get('retorno', {}).get('status') == 'OK':
                return response['retorno'].get('produto')
            return None
        except Exception as e:
            logger.error(f"Erro ao obter produto {produto_id}: {e}")
            return None
    
    async def alterar_estoque(
        self,
        produto_id: str,
        quantidade: int,
        tipo: str = 'E',
        deposito: str = 'Geral',
        observacoes: str = ''
    ) -> Dict[str, Any]:
        """Altera estoque do produto no Tiny"""
        try:
            # Formatar data atual
            from datetime import datetime
            data_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # IMPORTANTE: Campo 'deposito' causa erro na API!
            estoque_data = {
                'estoque': {  # DEVE ter wrapper 'estoque'!
                    'idProduto': str(produto_id),  # String funciona!
                    'tipo': tipo,  # E=Entrada, S=Saída, B=Balanço
                    'quantidade': str(quantidade),  # String também!
                    'data': data_atual,
                    'precoUnitario': '25.78',  # Preço unitário
                    'observacoes': observacoes or f'Entrada via Dashboard v2.0'
                    # NÃO INCLUIR 'deposito' - causa erro!
                }
            }

            data = {
                'estoque': json.dumps(estoque_data)  # Tiny espera um objeto JSON
            }

            response = await self._make_request('produto.atualizar.estoque.php', data)
            
            # Debug: log da resposta completa
            logger.info(f"Resposta Tiny: {json.dumps(response, indent=2)}")

            if response.get('retorno', {}).get('status') == 'OK':
                return {
                    'success': True,
                    'message': 'Estoque atualizado com sucesso',
                    'response': response['retorno']
                }
            else:
                retorno = response.get('retorno', {})
                # Verificar se há erros no nível do retorno
                if 'erros' in retorno:
                    erros = retorno.get('erros', [])
                    erro_msg = erros[0]['erro'] if erros else 'Erro desconhecido'
                # Verificar se há erros no nível do registro
                elif 'registros' in retorno:
                    registros = retorno.get('registros', [])
                    if registros and isinstance(registros, list):
                        registro = registros[0].get('registro', {})
                    elif isinstance(registros, dict):
                        registro = registros.get('registro', {})
                    else:
                        registro = {}
                    
                    if registro.get('status') == 'Erro':
                        erros = registro.get('erros', [])
                        erro_msg = erros[0]['erro'] if erros else 'Erro no registro'
                    else:
                        erro_msg = 'Resposta inesperada da API'
                else:
                    erro_msg = f'Status: {retorno.get("status", "Desconhecido")}'
                    
                logger.error(f"Erro retornado pelo Tiny ao alterar estoque: {erro_msg}")
                logger.error(f"Resposta completa: {json.dumps(response, indent=2)}")
                return {
                    'success': False,
                    'message': f'Erro ao atualizar estoque: {erro_msg}',
                    'response': response
                }
        except Exception as e:
            logger.exception(f"Exceção ao alterar estoque: {e}")
            return {
                'success': False,
                'message': f'Erro na comunicação com Tiny: {str(e)}',
                'response': None
            }
    
    async def obter_estoque(self, produto_id: str) -> Optional[Dict[str, Any]]:
        """Obtém estoque atual do produto"""
        try:
            data = {'id': produto_id}
            response = await self._make_request('produto.obter.estoque.php', data)
            
            if response.get('retorno', {}).get('status') == 'OK':
                return response['retorno']
            return None
        except Exception as e:
            logger.error(f"Erro ao obter estoque: {e}")
            return None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

# Instância global
tiny_client = TinyAPIClient()