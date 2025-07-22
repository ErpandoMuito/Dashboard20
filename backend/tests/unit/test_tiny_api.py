"""
Testes unitários para o serviço TinyAPI
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
import json

from app.services.tiny_api import TinyAPIClient


class TestTinyAPIClient:
    """Testes para o cliente da API Tiny"""
    
    @pytest.fixture
    def tiny_client(self):
        """Cliente Tiny para testes"""
        return TinyAPIClient()
    
    @pytest.fixture
    def mock_httpx_client(self):
        """Mock do cliente HTTP"""
        with patch('app.services.tiny_api.httpx.AsyncClient') as mock_class:
            mock_instance = AsyncMock()
            mock_class.return_value = mock_instance
            yield mock_instance
    
    @pytest.mark.unit
    async def test_buscar_produto_sucesso(self, tiny_client, mock_httpx_client):
        """Deve buscar produto com sucesso"""
        # Configurar resposta mock
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'retorno': {
                'status': 'OK',
                'produtos': [{
                    'produto': {
                        'id': '123',
                        'codigo': 'PH-510',
                        'nome': 'Arruela Trava',
                        'unidade': 'UN'
                    }
                }]
            }
        }
        mock_response.raise_for_status = MagicMock()
        
        tiny_client.client.post = AsyncMock(return_value=mock_response)
        
        # Executar busca
        produto = await tiny_client.buscar_produto_por_codigo('PH-510')
        
        # Verificar resultado
        assert produto is not None
        assert produto['id'] == '123'
        assert produto['codigo'] == 'PH-510'
        assert produto['nome'] == 'Arruela Trava'
        
        # Verificar chamada
        tiny_client.client.post.assert_called_once()
        call_args = tiny_client.client.post.call_args
        assert 'produtos.pesquisa.php' in call_args[0][0]
    
    @pytest.mark.unit
    async def test_buscar_produto_nao_encontrado(self, tiny_client, mock_httpx_client):
        """Deve retornar None quando produto não encontrado"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'retorno': {
                'status': 'OK',
                'produtos': []
            }
        }
        mock_response.raise_for_status = MagicMock()
        
        tiny_client.client.post = AsyncMock(return_value=mock_response)
        
        produto = await tiny_client.buscar_produto_por_codigo('INEXISTENTE')
        
        assert produto is None
    
    @pytest.mark.unit
    async def test_alterar_estoque_sucesso(self, tiny_client, mock_httpx_client):
        """Deve alterar estoque com sucesso"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'retorno': {
                'status': 'OK',
                'registros': 1
            }
        }
        mock_response.raise_for_status = MagicMock()
        
        tiny_client.client.post = AsyncMock(return_value=mock_response)
        
        resultado = await tiny_client.alterar_estoque(
            produto_id='123',
            quantidade=100,
            tipo='E',
            deposito='Geral'
        )
        
        assert resultado['success'] is True
        assert 'Estoque atualizado com sucesso' in resultado['message']
        assert resultado['response']['retorno']['status'] == 'OK'
    
    @pytest.mark.unit
    async def test_alterar_estoque_erro_api(self, tiny_client, mock_httpx_client):
        """Deve tratar erro da API Tiny"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'retorno': {
                'status': 'Erro',
                'erros': [{'erro': 'Produto não encontrado'}]
            }
        }
        mock_response.raise_for_status = MagicMock()
        
        tiny_client.client.post = AsyncMock(return_value=mock_response)
        
        resultado = await tiny_client.alterar_estoque(
            produto_id='999',
            quantidade=100
        )
        
        assert resultado['success'] is False
        assert 'Produto não encontrado' in resultado['message']
    
    @pytest.mark.unit
    async def test_erro_http(self, tiny_client, mock_httpx_client):
        """Deve tratar erros HTTP"""
        tiny_client.client.post = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "Error", 
                request=MagicMock(), 
                response=MagicMock(status_code=500)
            )
        )
        
        produto = await tiny_client.buscar_produto_por_codigo('PH-510')
        
        assert produto is None
    
    @pytest.mark.unit
    async def test_erro_json_decode(self, tiny_client, mock_httpx_client):
        """Deve tratar erro ao decodificar JSON"""
        mock_response = MagicMock()
        mock_response.json.side_effect = json.JSONDecodeError("Error", "doc", 0)
        mock_response.raise_for_status = MagicMock()
        
        tiny_client.client.post = AsyncMock(return_value=mock_response)
        
        produto = await tiny_client.buscar_produto_por_codigo('PH-510')
        
        assert produto is None
    
    @pytest.mark.unit
    async def test_parametros_request(self, tiny_client, mock_httpx_client):
        """Deve enviar parâmetros corretos na requisição"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'retorno': {'status': 'OK'}}
        mock_response.raise_for_status = MagicMock()
        
        tiny_client.client.post = AsyncMock(return_value=mock_response)
        
        await tiny_client._make_request('test.php', {'campo': 'valor'})
        
        # Verificar chamada
        tiny_client.client.post.assert_called_once()
        call_args = tiny_client.client.post.call_args
        
        # Verificar URL
        assert call_args[0][0].endswith('/test.php')
        
        # Verificar headers
        assert call_args.kwargs['headers']['Content-Type'] == 'application/x-www-form-urlencoded'
        
        # Verificar conteúdo (deve incluir token e formato)
        content = call_args.kwargs['content']
        assert 'token=' in content
        assert 'formato=JSON' in content
        assert 'campo=valor' in content