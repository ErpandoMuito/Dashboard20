#!/usr/bin/env python3
"""
Script para testar a API de estoque - Adicionar e remover 1 unidade do PH-510
"""
import httpx
import asyncio
import json
from datetime import datetime

API_URL = "http://localhost:8000/api/v2/estoque"
PRODUTO_CODIGO = "PH-510"

async def test_buscar_produto():
    """Testa busca do produto"""
    async with httpx.AsyncClient() as client:
        print("1. Buscando informações do produto PH-510...")
        response = await client.get(f"{API_URL}/produto/{PRODUTO_CODIGO}")
        
        if response.status_code == 200:
            produto = response.json()
            print(f"✅ Produto encontrado:")
            print(f"   - Nome: {produto['nome']}")
            print(f"   - Código: {produto['codigo']}")
            print(f"   - Saldo atual: {produto['saldo']} unidades")
            return produto
        else:
            print(f"❌ Erro ao buscar produto: {response.status_code}")
            print(f"   {response.text}")
            return None

async def test_adicionar_estoque():
    """Testa adição de 1 unidade ao estoque"""
    async with httpx.AsyncClient() as client:
        print("\n2. Adicionando 1 unidade ao estoque...")
        
        data = {
            "codigo_produto": PRODUTO_CODIGO,
            "quantidade": 1,
            "tipo": "E",
            "descricao": "Teste de adição via API - Script Python",
            "data": datetime.now().isoformat(),
            "deposito": "FUNDIÇÃO"
        }
        
        response = await client.post(
            f"{API_URL}/entrada",
            json=data
        )
        
        if response.status_code == 200:
            resultado = response.json()
            print(f"✅ {resultado['message']}")
            if resultado.get('saldo_atual') is not None:
                print(f"   - Novo saldo: {resultado['saldo_atual']} unidades")
            return True
        else:
            print(f"❌ Erro ao adicionar estoque: {response.status_code}")
            print(f"   {response.text}")
            return False

async def test_remover_estoque():
    """Testa remoção de 1 unidade do estoque"""
    async with httpx.AsyncClient() as client:
        print("\n3. Removendo 1 unidade do estoque...")
        
        data = {
            "codigo_produto": PRODUTO_CODIGO,
            "quantidade": 1,
            "tipo": "S",
            "descricao": "Teste de remoção via API - Script Python",
            "data": datetime.now().isoformat(),
            "deposito": "FUNDIÇÃO"
        }
        
        response = await client.post(
            f"{API_URL}/saida",
            json=data
        )
        
        if response.status_code == 200:
            resultado = response.json()
            print(f"✅ {resultado['message']}")
            if resultado.get('saldo_atual') is not None:
                print(f"   - Novo saldo: {resultado['saldo_atual']} unidades")
            return True
        else:
            print(f"❌ Erro ao remover estoque: {response.status_code}")
            print(f"   {response.text}")
            return False

async def main():
    """Função principal"""
    print("=== Teste da API de Estoque - PH-510 ===\n")
    
    # Verificar se API está rodando
    try:
        async with httpx.AsyncClient() as client:
            health = await client.get("http://localhost:8000/api/health")
            if health.status_code != 200:
                print("❌ API não está respondendo. Execute ./start-services.sh primeiro!")
                return
    except:
        print("❌ Não foi possível conectar à API. Execute ./start-services.sh primeiro!")
        return
    
    # Executar testes
    produto_inicial = await test_buscar_produto()
    if not produto_inicial:
        return
    
    saldo_inicial = produto_inicial['saldo']
    
    # Adicionar 1 unidade
    if await test_adicionar_estoque():
        await asyncio.sleep(1)
        
        # Verificar novo saldo
        produto_apos_adicao = await test_buscar_produto()
        if produto_apos_adicao:
            print(f"\n✅ Saldo aumentou de {saldo_inicial} para {produto_apos_adicao['saldo']}")
    
    # Remover 1 unidade
    if await test_remover_estoque():
        await asyncio.sleep(1)
        
        # Verificar saldo final
        produto_final = await test_buscar_produto()
        if produto_final:
            print(f"\n✅ Saldo final: {produto_final['saldo']} unidades")
            print(f"   (Inicial: {saldo_inicial}, Final: {produto_final['saldo']})")

if __name__ == "__main__":
    asyncio.run(main())