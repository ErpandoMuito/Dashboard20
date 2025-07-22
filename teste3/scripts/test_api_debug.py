#!/usr/bin/env python3
"""
Script de Debug da API - Verifica respostas
"""

import requests

BASE_URL = "https://dashboard-estoque-v2.fly.dev/teste3"

def test_endpoint(url, method="GET"):
    """Testa endpoint e mostra resposta completa"""
    print(f"\n{'=' * 60}")
    print(f"Testando: {method} {url}")
    print(f"{'=' * 60}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        else:
            response = requests.post(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Não especificado')}")
        print(f"Tamanho da resposta: {len(response.content)} bytes")
        
        # Verifica se é JSON
        try:
            data = response.json()
            print("\nResposta JSON:")
            print(data)
        except:
            # Se não for JSON, mostra os primeiros 500 caracteres
            print("\nResposta (primeiros 500 chars):")
            print(response.text[:500])
            if len(response.text) > 500:
                print("... (truncado)")
                
    except Exception as e:
        print(f"ERRO: {e}")

def main():
    print("DEBUG DA API - Sistema DashboardNext v2")
    
    # Testa endpoints principais
    endpoints = [
        (f"{BASE_URL}/", "GET"),
        (f"{BASE_URL}/api/health", "GET"),
        (f"{BASE_URL}/api/produtos", "GET"),
        (f"{BASE_URL}/api/notas", "GET"),
        (f"{BASE_URL}/api/produtos/buscar?nome=teste", "GET"),
        (f"{BASE_URL}/api/produtos/sync", "POST"),
    ]
    
    for url, method in endpoints:
        test_endpoint(url, method)
    
    print("\n" + "=" * 60)
    print("Debug concluído")

if __name__ == "__main__":
    main()