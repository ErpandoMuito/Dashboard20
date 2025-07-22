#!/usr/bin/env python3
"""
Script para testar o sistema Flask de gestão de estoque
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Testa se o servidor está rodando"""
    print("1. Testando health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ERRO: {e}")
        return False

def test_buscar_produto():
    """Testa busca do produto PH-510"""
    print("\n2. Buscando produto PH-510...")
    try:
        response = requests.get(f"{BASE_URL}/api/v2/estoque/produto/PH-510")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Nome: {data.get('nome')}")
            print(f"   Código: {data.get('codigo')}")
            print(f"   Estoque Total: {data.get('saldo_estoque', {}).get('Total', 0)}")
            return True
        else:
            print(f"   Erro: {response.json()}")
            return False
    except Exception as e:
        print(f"   ERRO: {e}")
        return False

def test_adicionar_estoque():
    """Testa adicionar 1 unidade ao PH-510"""
    print("\n3. Adicionando 1 unidade ao PH-510...")
    try:
        response = requests.post(f"{BASE_URL}/api/v2/estoque/ph510/adicionar")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=2)}")
        return data.get('success', False)
    except Exception as e:
        print(f"   ERRO: {e}")
        return False

def test_remover_estoque():
    """Testa remover 1 unidade do PH-510"""
    print("\n4. Removendo 1 unidade do PH-510...")
    try:
        response = requests.post(f"{BASE_URL}/api/v2/estoque/ph510/remover")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=2)}")
        return data.get('success', False)
    except Exception as e:
        print(f"   ERRO: {e}")
        return False

def main():
    print("=== TESTE DO SISTEMA FLASK DE ESTOQUE ===\n")
    
    # Verifica se servidor está rodando
    if not test_health():
        print("\nERRO: Servidor não está rodando!")
        print("Execute primeiro: cd flask-backend && python app.py")
        return
    
    # Testa busca de produto
    if test_buscar_produto():
        print("   ✓ Busca funcionando!")
    
    # Aguarda um pouco
    time.sleep(1)
    
    # Testa adicionar estoque
    if test_adicionar_estoque():
        print("   ✓ Adição funcionando!")
    
    # Aguarda um pouco
    time.sleep(1)
    
    # Testa remover estoque
    if test_remover_estoque():
        print("   ✓ Remoção funcionando!")
    
    # Busca novamente para ver resultado final
    print("\n5. Verificando estoque final...")
    test_buscar_produto()
    
    print("\n=== TESTE CONCLUÍDO ===")

if __name__ == "__main__":
    main()