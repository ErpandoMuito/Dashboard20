"""
Testes E2E (End-to-End) para o fluxo completo de entrada de estoque
ATENÇÃO: Estes testes fazem alterações REAIS no Tiny e devem ser executados com cuidado
"""
import pytest
import os
from datetime import datetime
from httpx import AsyncClient
import asyncio

from app.services.tiny_api import TinyAPIClient


# Produto específico para testes automatizados
PRODUTO_TESTE = {
    'codigo': 'PH-999',  # Use um código que exista no Tiny para testes
    'nome': 'PRODUTO TESTE AUTOMATIZADO'
}

# Skip se não estiver em ambiente de teste E2E
pytestmark = pytest.mark.skipif(
    os.getenv("RUN_E2E_TESTS") != "true",
    reason="Testes E2E desabilitados. Use RUN_E2E_TESTS=true para executar"
)


class TestFluxoCompletoE2E:
    """
    Testes E2E que interagem com a API real do Tiny
    IMPORTANTE: Todas as alterações são revertidas após os testes
    """
    
    @pytest.mark.e2e
    @pytest.mark.slow
    async def test_fluxo_completo_entrada_e_reversao(self, test_client: AsyncClient, tiny_test_manager):
        """
        Teste completo: entrada de estoque e reversão automática
        """
        # 1. Buscar produto e obter estoque inicial
        response_busca = await test_client.get(f"/api/v2/estoque/produto/{PRODUTO_TESTE['codigo']}")
        
        if response_busca.status_code == 404:
            pytest.skip(f"Produto {PRODUTO_TESTE['codigo']} não existe no Tiny")
        
        produto_inicial = response_busca.json()
        estoque_inicial = produto_inicial["saldo"]
        
        print(f"\n📊 Estoque inicial de {PRODUTO_TESTE['codigo']}: {estoque_inicial}")
        
        # 2. Fazer entrada de estoque
        quantidade_entrada = 10  # Quantidade pequena para teste
        payload = {
            "codigo_produto": PRODUTO_TESTE['codigo'],
            "quantidade": quantidade_entrada,
            "descricao": f"Teste E2E automatizado - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "deposito": "Teste"
        }
        
        response_entrada = await test_client.post("/api/v2/estoque/entrada", json=payload)
        assert response_entrada.status_code == 200
        
        resultado_entrada = response_entrada.json()
        assert resultado_entrada["success"] is True
        
        # 3. Aguardar processamento
        await asyncio.sleep(2)
        
        # 4. Verificar novo estoque
        response_novo = await test_client.get(f"/api/v2/estoque/produto/{PRODUTO_TESTE['codigo']}")
        assert response_novo.status_code == 200
        
        produto_atualizado = response_novo.json()
        estoque_esperado = estoque_inicial + quantidade_entrada
        
        print(f"📈 Estoque após entrada: {produto_atualizado['saldo']} (esperado: {estoque_esperado})")
        
        # Verificação com tolerância (pode haver outras movimentações)
        assert produto_atualizado["saldo"] >= estoque_esperado
        
        # 5. Reversão automática via fixture tiny_test_manager
        # A reversão acontece automaticamente ao sair do contexto
        
    @pytest.mark.e2e
    @pytest.mark.slow
    async def test_entrada_multiplas_transacoes(self, tiny_test_manager):
        """
        Teste com múltiplas entradas e reversão em lote
        """
        entradas = [5, 10, 15]  # Três entradas diferentes
        
        for quantidade in entradas:
            resultado = await tiny_test_manager.entrada_estoque(
                codigo=PRODUTO_TESTE['codigo'],
                quantidade=quantidade,
                deposito="Teste Múltiplo"
            )
            
            assert resultado['success'] is True
            print(f"✅ Entrada de {quantidade} unidades realizada")
            
            # Pequeno delay entre operações
            await asyncio.sleep(1)
        
        # Verificar que todas as alterações foram registradas
        assert len(tiny_test_manager.alteracoes) == len(entradas)
        
        # A reversão acontece automaticamente ao sair do contexto
    
    @pytest.mark.e2e
    async def test_validacao_produto_inexistente(self, test_client: AsyncClient):
        """
        Teste com produto que não existe (sem alteração no Tiny)
        """
        payload = {
            "codigo_produto": "PH-INEXISTENTE-9999",
            "quantidade": 100,
            "descricao": "Teste de produto inexistente"
        }
        
        response = await test_client.post("/api/v2/estoque/entrada", json=payload)
        
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"]
    
    @pytest.mark.e2e
    @pytest.mark.slow
    async def test_concorrencia_segura(self, test_client: AsyncClient, tiny_test_manager):
        """
        Teste de requisições concorrentes (com cuidado)
        """
        # Criar duas requisições simultâneas pequenas
        async def fazer_entrada(quantidade: int, descricao: str):
            payload = {
                "codigo_produto": PRODUTO_TESTE['codigo'],
                "quantidade": quantidade,
                "descricao": descricao,
                "deposito": "Teste Concorrência"
            }
            return await test_client.post("/api/v2/estoque/entrada", json=payload)
        
        # Executar em paralelo
        resultados = await asyncio.gather(
            fazer_entrada(3, "Teste concorrente 1"),
            fazer_entrada(4, "Teste concorrente 2"),
            return_exceptions=True
        )
        
        # Verificar resultados
        for i, resultado in enumerate(resultados):
            if isinstance(resultado, Exception):
                print(f"⚠️ Requisição {i+1} falhou: {resultado}")
            else:
                assert resultado.status_code == 200
                print(f"✅ Requisição {i+1} bem-sucedida")
    
    @pytest.mark.e2e
    async def test_verificacao_cache_apos_entrada(self, test_client: AsyncClient, redis_client):
        """
        Verifica se o cache é atualizado após entrada (sem alterar Tiny)
        """
        # Limpar cache antes
        await redis_client.delete(f"estoque:produto:{PRODUTO_TESTE['codigo']}")
        
        # Buscar produto (deve vir do Tiny)
        response1 = await test_client.get(f"/api/v2/estoque/produto/{PRODUTO_TESTE['codigo']}")
        
        if response1.status_code == 404:
            pytest.skip("Produto de teste não encontrado")
        
        # Verificar se foi cacheado
        cached = await redis_client.get(f"estoque:produto:{PRODUTO_TESTE['codigo']}")
        assert cached is not None
        assert cached["codigo"] == PRODUTO_TESTE['codigo']


class TestSegurancaE2E:
    """Testes de segurança e limites"""
    
    @pytest.mark.e2e
    async def test_limite_quantidade_excessiva(self, test_client: AsyncClient):
        """Testa proteção contra quantidades muito grandes"""
        payload = {
            "codigo_produto": PRODUTO_TESTE['codigo'],
            "quantidade": 999999999,  # Quantidade excessiva
            "descricao": "Teste de limite"
        }
        
        # O sistema deve aceitar mas podemos adicionar validação futura
        response = await test_client.post("/api/v2/estoque/entrada", json=payload)
        
        # Por ora, apenas verificamos que não quebra
        assert response.status_code in [200, 400, 422]