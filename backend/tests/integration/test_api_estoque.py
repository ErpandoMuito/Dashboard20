"""
Testes de integração para API de estoque
"""
import pytest
from httpx import AsyncClient
from datetime import datetime
import json

from app.models.estoque import EntradaEstoqueRequest


class TestAPIEstoque:
    """Testes de integração para endpoints de estoque"""
    
    @pytest.mark.integration
    async def test_entrada_estoque_completa(self, test_client: AsyncClient, mock_tiny_client):
        """Teste completo de entrada de estoque com mock"""
        payload = {
            "codigo_produto": "PH-510",
            "quantidade": 100,
            "descricao": "Teste de integração",
            "data": datetime.now().isoformat(),
            "deposito": "Geral"
        }
        
        response = await test_client.post("/api/v2/estoque/entrada", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "Entrada de 100 unidades realizada com sucesso" in data["message"]
        assert data["produto_id"] == "123456"
        assert data["saldo_atual"] == 1000
        
        # Verificar que os mocks foram chamados
        mock_tiny_client.buscar_produto_por_codigo.assert_called_once_with("PH-510")
        mock_tiny_client.alterar_estoque.assert_called_once()
        mock_tiny_client.obter_estoque.assert_called_once()
    
    @pytest.mark.integration
    async def test_entrada_produto_nao_encontrado(self, test_client: AsyncClient, mock_tiny_client):
        """Deve retornar 404 quando produto não existe"""
        # Configurar mock para retornar None
        mock_tiny_client.buscar_produto_por_codigo.return_value = None
        
        payload = {
            "codigo_produto": "INEXISTENTE",
            "quantidade": 50
        }
        
        response = await test_client.post("/api/v2/estoque/entrada", json=payload)
        
        assert response.status_code == 404
        data = response.json()
        assert "não encontrado" in data["detail"]
    
    @pytest.mark.integration
    async def test_entrada_erro_tiny_api(self, test_client: AsyncClient, mock_tiny_client):
        """Deve retornar erro quando Tiny API falha"""
        # Configurar mock para retornar erro
        mock_tiny_client.alterar_estoque.return_value = {
            'success': False,
            'message': 'Erro ao conectar com Tiny'
        }
        
        payload = {
            "codigo_produto": "PH-510",
            "quantidade": 100
        }
        
        response = await test_client.post("/api/v2/estoque/entrada", json=payload)
        
        assert response.status_code == 400
        data = response.json()
        assert "Erro ao conectar com Tiny" in data["detail"]
    
    @pytest.mark.integration
    async def test_buscar_produto(self, test_client: AsyncClient, mock_tiny_client):
        """Teste de busca de produto"""
        response = await test_client.get("/api/v2/estoque/produto/PH-510")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == "123456"
        assert data["codigo"] == "PH-510"
        assert data["nome"] == "Produto de Teste"
        assert data["unidade"] == "UN"
        assert data["saldo"] == 1000
    
    @pytest.mark.integration
    async def test_buscar_produto_cache(self, test_client: AsyncClient, mock_tiny_client, redis_client):
        """Deve usar cache na segunda busca"""
        # Primeira busca
        response1 = await test_client.get("/api/v2/estoque/produto/PH-CACHE")
        assert response1.status_code == 200
        
        # Verificar que foi salvo no cache
        cached = await redis_client.get("estoque:produto:PH-CACHE")
        assert cached is not None
        assert cached["codigo"] == "PH-CACHE"
        
        # Segunda busca (deve vir do cache)
        mock_tiny_client.buscar_produto_por_codigo.reset_mock()
        response2 = await test_client.get("/api/v2/estoque/produto/PH-CACHE")
        assert response2.status_code == 200
        
        # Mock não deve ter sido chamado novamente
        mock_tiny_client.buscar_produto_por_codigo.assert_not_called()
    
    @pytest.mark.integration
    async def test_validacao_quantidade_invalida(self, test_client: AsyncClient):
        """Deve validar quantidade inválida"""
        payload = {
            "codigo_produto": "PH-510",
            "quantidade": -10  # Quantidade negativa
        }
        
        response = await test_client.post("/api/v2/estoque/entrada", json=payload)
        
        assert response.status_code == 422
        data = response.json()
        assert "quantity" in str(data["detail"])
    
    @pytest.mark.integration
    async def test_validacao_campos_obrigatorios(self, test_client: AsyncClient):
        """Deve validar campos obrigatórios"""
        payload = {
            "quantidade": 100
            # Faltando codigo_produto
        }
        
        response = await test_client.post("/api/v2/estoque/entrada", json=payload)
        
        assert response.status_code == 422
        data = response.json()
        assert any("codigo_produto" in str(error) for error in data["detail"])
    
    @pytest.mark.integration
    async def test_historico_produto(self, test_client: AsyncClient):
        """Teste do endpoint de histórico (em desenvolvimento)"""
        response = await test_client.get("/api/v2/estoque/historico/PH-510?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["codigo"] == "PH-510"
        assert isinstance(data["historico"], list)
        assert "desenvolvimento" in data["message"]
    
    @pytest.mark.integration
    async def test_entrada_com_cache_redis(self, test_client: AsyncClient, mock_tiny_client, redis_client):
        """Teste de entrada salvando no cache Redis"""
        payload = {
            "codigo_produto": "PH-REDIS",
            "quantidade": 200,
            "descricao": "Teste Redis"
        }
        
        response = await test_client.post("/api/v2/estoque/entrada", json=payload)
        assert response.status_code == 200
        
        # Verificar cache do produto
        cache_key = "estoque:produto:PH-REDIS"
        cached_product = await redis_client.get(cache_key)
        assert cached_product is not None
        assert cached_product["saldo"] == 1000
        
        # Verificar histórico
        historico_keys = await redis_client.client.keys("estoque:historico:PH-REDIS:*")
        assert len(historico_keys) > 0