"""
Configurações globais dos testes e fixtures compartilhadas
"""
import pytest
import asyncio
from typing import AsyncGenerator, Dict, Any
import os
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from datetime import datetime
import json

from app.core.redis_client import RedisClient
from app.services.tiny_api import TinyAPIClient
from main import app

# Configurar ambiente de teste
os.environ["TEST_ENV"] = "true"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"  # DB 15 para testes

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    """Cliente HTTP para testar a API"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def redis_client() -> RedisClient:
    """Cliente Redis para testes"""
    client = RedisClient()
    # Limpar DB de teste antes
    await client.client.flushdb()
    yield client
    # Limpar depois
    await client.client.flushdb()

@pytest.fixture
def mock_tiny_client():
    """Mock do cliente Tiny API"""
    with patch('app.api.estoque.tiny_client') as mock:
        # Configurar respostas padrão
        mock.buscar_produto_por_codigo = AsyncMock(return_value={
            'id': '123456',
            'codigo': 'PH-TEST',
            'nome': 'Produto de Teste',
            'unidade': 'UN',
            'preco': '10.00'
        })
        
        mock.alterar_estoque = AsyncMock(return_value={
            'success': True,
            'message': 'Estoque atualizado com sucesso',
            'response': {'retorno': {'status': 'OK'}}
        })
        
        mock.obter_estoque = AsyncMock(return_value={
            'produto': {
                'id': '123456',
                'codigo': 'PH-TEST',
                'saldo': '1000'
            }
        })
        
        yield mock

@pytest.fixture
def produto_teste():
    """Dados de produto para teste"""
    return {
        'codigo': 'PH-TEST-AUTO',  # Código único para testes
        'nome': 'Produto Teste Automatizado',
        'quantidade_inicial': 1000,
        'quantidade_entrada': 50,
        'quantidade_saida': 50  # Para reverter
    }

@pytest.fixture
async def tiny_test_manager():
    """
    Manager para testes reais com Tiny API
    Garante que alterações sejam revertidas
    """
    class TinyTestManager:
        def __init__(self):
            self.client = TinyAPIClient()
            self.alteracoes = []
            
        async def entrada_estoque(self, codigo: str, quantidade: int, deposito: str = "Teste"):
            """Registra entrada e marca para reversão"""
            produto = await self.client.buscar_produto_por_codigo(codigo)
            if not produto:
                raise ValueError(f"Produto {codigo} não encontrado")
                
            resultado = await self.client.alterar_estoque(
                produto_id=produto['id'],
                quantidade=quantidade,
                tipo='E',
                deposito=deposito,
                observacoes=f'Teste automatizado - {datetime.now()}'
            )
            
            if resultado['success']:
                # Registrar para reverter depois
                self.alteracoes.append({
                    'produto_id': produto['id'],
                    'quantidade': quantidade,
                    'tipo': 'S'  # Saída para reverter entrada
                })
            
            return resultado
            
        async def limpar(self):
            """Reverte todas as alterações"""
            for alteracao in reversed(self.alteracoes):
                try:
                    await self.client.alterar_estoque(
                        produto_id=alteracao['produto_id'],
                        quantidade=alteracao['quantidade'],
                        tipo=alteracao['tipo'],
                        deposito='Teste',
                        observacoes='Reversão de teste automatizado'
                    )
                except Exception as e:
                    print(f"Erro ao reverter alteração: {e}")
            
            self.alteracoes.clear()
            
        async def __aenter__(self):
            return self
            
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            await self.limpar()
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
    
    async with TinyTestManager() as manager:
        yield manager

@pytest.fixture
def entrada_estoque_payload():
    """Payload padrão para testes de entrada"""
    return {
        "codigo_produto": "PH-TEST",
        "quantidade": 100,
        "descricao": "Teste automatizado",
        "data": datetime.now().isoformat(),
        "deposito": "Teste"
    }

@pytest.fixture
def mock_datetime():
    """Mock para data/hora fixa"""
    with patch('app.api.estoque.datetime') as mock_dt:
        fixed_time = datetime(2025, 7, 21, 10, 0, 0)
        mock_dt.now.return_value = fixed_time
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        yield fixed_time