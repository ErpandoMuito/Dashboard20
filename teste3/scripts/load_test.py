#!/usr/bin/env python3
"""
Script de Teste de Carga Simples
Testa performance e confiabilidade do sistema
"""

import requests
import time
import concurrent.futures
from datetime import datetime

# Configuração
BASE_URL = "https://dashboard-estoque-v2.fly.dev/teste3"

def test_endpoint(url, timeout=5):
    """Testa um endpoint e retorna métricas"""
    try:
        start = time.time()
        response = requests.get(url, timeout=timeout)
        elapsed = time.time() - start
        
        return {
            "success": True,
            "status_code": response.status_code,
            "response_time": elapsed,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "status_code": None,
            "response_time": 0,
            "error": str(e)
        }

def run_load_test():
    """Executa teste de carga"""
    print("=" * 60)
    print("TESTE DE CARGA - Sistema DashboardNext v2")
    print("=" * 60)
    print(f"URL: {BASE_URL}")
    print(f"Hora: {datetime.now().strftime('%H:%M:%S')}\n")
    
    # Teste 1: Health Check Individual
    print("1. TESTE INDIVIDUAL - Health Check")
    result = test_endpoint(f"{BASE_URL}/api/health")
    print(f"   Status: {'OK' if result['success'] else 'FALHA'}")
    print(f"   HTTP: {result['status_code']}")
    print(f"   Tempo: {result['response_time']:.3f}s\n")
    
    # Teste 2: 10 requisições simultâneas
    print("2. TESTE DE CARGA - 10 requisições simultâneas")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(test_endpoint, f"{BASE_URL}/api/health") 
            for _ in range(10)
        ]
        
        results = []
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    
    # Análise dos resultados
    successful = sum(1 for r in results if r['success'])
    avg_time = sum(r['response_time'] for r in results) / len(results)
    
    print(f"   Requisições bem-sucedidas: {successful}/10")
    print(f"   Tempo médio de resposta: {avg_time:.3f}s\n")
    
    # Teste 3: Endpoints principais
    print("3. TESTE DE ENDPOINTS PRINCIPAIS")
    endpoints = [
        ("/", "Homepage"),
        ("/api/health", "Health Check"),
        ("/api/produtos", "Lista Produtos"),
        ("/api/notas", "Lista Notas")
    ]
    
    for endpoint, name in endpoints:
        result = test_endpoint(f"{BASE_URL}{endpoint}")
        status = "✓" if result['success'] and result['status_code'] == 200 else "✗"
        print(f"   {status} {name}: HTTP {result['status_code']} ({result['response_time']:.3f}s)")
    
    print("\n" + "=" * 60)
    
    # Nota final
    nota = 10.0
    if successful < 10:
        nota -= (10 - successful) * 0.5
    if avg_time > 1.0:
        nota -= 2.0
    elif avg_time > 0.5:
        nota -= 1.0
    
    nota = max(0, min(10, nota))
    print(f"NOTA FINAL: {nota:.1f}/10")
    print("=" * 60)

if __name__ == "__main__":
    run_load_test()