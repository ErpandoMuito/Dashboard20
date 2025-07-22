#!/usr/bin/env python3
"""
Script de Teste Específico para API de Produtos
Testa funcionalidades CRUD e comportamento do cache
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://dashboard-estoque-v2.fly.dev/teste3/api"

def pretty_print(title, data):
    """Imprime dados formatados"""
    print(f"\n{'=' * 60}")
    print(f"{title}")
    print(f"{'=' * 60}")
    if isinstance(data, dict):
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(data)

def test_produtos_workflow():
    """Testa fluxo completo de produtos"""
    print("TESTE COMPLETO DA API DE PRODUTOS")
    print(f"Iniciado em: {datetime.now().strftime('%H:%M:%S')}")
    
    # 1. Listar produtos (com cache)
    print("\n1. Listando produtos (primeira vez - deve buscar da API)...")
    start = time.time()
    response = requests.get(f"{BASE_URL}/produtos")
    elapsed1 = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Status: {data.get('status')}")
        print(f"✓ Source: {data.get('source')}")
        print(f"✓ Total produtos: {data.get('total', 0)}")
        print(f"✓ Tempo de resposta: {elapsed1:.3f}s")
        
        # Mostra primeiro produto se existir
        produtos = data.get('data', [])
        if produtos and isinstance(produtos, list) and len(produtos) > 0:
            primeiro = produtos[0]
            if isinstance(primeiro, dict) and 'produto' in primeiro:
                prod = primeiro['produto']
                print(f"\nPrimeiro produto encontrado:")
                print(f"  - ID: {prod.get('id')}")
                print(f"  - Nome: {prod.get('nome')}")
                print(f"  - Código: {prod.get('codigo')}")
    else:
        print(f"✗ Erro HTTP {response.status_code}")
        print(f"✗ Resposta: {response.text}")
    
    # 2. Listar produtos novamente (deve vir do cache)
    print("\n2. Listando produtos novamente (deve vir do cache)...")
    time.sleep(1)
    start = time.time()
    response = requests.get(f"{BASE_URL}/produtos")
    elapsed2 = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Source: {data.get('source')}")
        print(f"✓ Tempo de resposta: {elapsed2:.3f}s")
        
        if data.get('source') == 'cache' and elapsed2 < elapsed1:
            speedup = elapsed1 / elapsed2
            print(f"✓ CACHE FUNCIONANDO! Speedup: {speedup:.1f}x mais rápido")
        else:
            print(f"⚠ Cache não detectado ou sem melhoria de performance")
    
    # 3. Buscar produto específico
    print("\n3. Buscando produto por nome...")
    response = requests.get(f"{BASE_URL}/produtos/buscar", params={"nome": "parafuso"})
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Produtos encontrados: {data.get('total', 0)}")
        print(f"✓ Source: {data.get('source')}")
    else:
        print(f"✗ Erro HTTP {response.status_code}")
    
    # 4. Teste de sincronização
    print("\n4. Testando sincronização de produtos...")
    response = requests.post(f"{BASE_URL}/produtos/sync")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Status: {data.get('status')}")
        print(f"✓ Produtos encontrados: {data.get('produtos_encontrados', 0)}")
        print(f"✓ Produtos salvos: {data.get('produtos_salvos', 0)}")
    else:
        print(f"✗ Erro HTTP {response.status_code}")
        print(f"✗ Resposta: {response.text}")
    
    # 5. Teste de validação
    print("\n5. Testando validação de parâmetros...")
    response = requests.get(f"{BASE_URL}/produtos/buscar")  # Sem parâmetros
    
    if response.status_code == 400:
        print(f"✓ Validação funcionando - erro 400 retornado corretamente")
    else:
        print(f"⚠ Esperado erro 400, recebido {response.status_code}")
    
    # 6. Teste de produto específico por ID
    print("\n6. Buscando produto por ID (teste com ID fictício)...")
    response = requests.get(f"{BASE_URL}/produtos/123456")
    
    if response.status_code in [200, 404]:
        print(f"✓ Endpoint funcionando - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Source: {data.get('source')}")
    else:
        print(f"✗ Erro inesperado: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("TESTE CONCLUÍDO")
    print("=" * 60)

if __name__ == "__main__":
    test_produtos_workflow()