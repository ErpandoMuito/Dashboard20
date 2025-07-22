#!/usr/bin/env python3
"""
Teste completo do sistema de gestão de estoque
"""
import httpx
import asyncio
import json
from datetime import datetime

API_URL = "http://localhost:8000/api/v2/estoque"

async def testar_sistema():
    """Testa o sistema completo"""
    async with httpx.AsyncClient() as client:
        print("=== TESTE DO SISTEMA DE GESTÃO DE ESTOQUE ===\n")
        
        # 1. Popular cache
        print("1. Populando cache com produtos PH-500 até PH-520...")
        try:
            response = await client.post(f"{API_URL}/cache/popular?inicio=500&fim=520")
            if response.status_code == 200:
                result = response.json()
                detalhes = result.get('detalhes', {})
                print(f"✅ Cache populado: {detalhes.get('produtos_encontrados')} produtos encontrados")
            else:
                print(f"❌ Erro ao popular cache: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        # 2. Listar produtos cacheados
        print("\n2. Listando produtos no cache...")
        try:
            response = await client.get(f"{API_URL}/cache/produtos")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Total no cache: {result['total']} produtos")
                for p in result['produtos'][:5]:
                    print(f"   - {p['codigo']}: {p['nome']}")
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        # 3. Testar entrada de estoque
        print("\n3. Testando entrada de estoque para PH-510...")
        entrada_data = {
            "codigo_produto": "PH-510",
            "quantidade": 10,
            "tipo": "E",
            "descricao": "Produção - 22/07 - Segunda - Teste API",
            "data": datetime.now().isoformat(),
            "deposito": "FUNDIÇÃO"
        }
        
        try:
            response = await client.post(f"{API_URL}/entrada", json=entrada_data)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {result['message']}")
                print(f"   Saldo atual: {result.get('saldo_atual')} unidades")
            else:
                print(f"❌ Erro: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        # 4. Testar saída de estoque
        print("\n4. Testando saída de estoque para PH-510...")
        saida_data = {
            "codigo_produto": "PH-510",
            "quantidade": 5,
            "tipo": "S",
            "descricao": "Envio para cliente - Teste API",
            "data": datetime.now().isoformat(),
            "deposito": "FUNDIÇÃO"
        }
        
        try:
            response = await client.post(f"{API_URL}/saida", json=saida_data)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {result['message']}")
                print(f"   Saldo atual: {result.get('saldo_atual')} unidades")
            else:
                print(f"❌ Erro: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        # 5. Buscar produto
        print("\n5. Buscando informações do PH-510...")
        try:
            response = await client.get(f"{API_URL}/produto/PH-510")
            if response.status_code == 200:
                produto = response.json()
                print(f"✅ Produto: {produto['nome']}")
                print(f"   Código: {produto['codigo']}")
                print(f"   Saldo: {produto['saldo']} unidades")
        except Exception as e:
            print(f"❌ Erro: {e}")

async def main():
    """Função principal"""
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
    
    await testar_sistema()
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    asyncio.run(main())