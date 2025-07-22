#!/usr/bin/env python3
"""
Script de Teste Automatizado para Sistema DashboardNext v2 - Teste3
QA Tester 3 - Automatizado (Pragmático)
"""

import requests
import time
import json
import concurrent.futures
from datetime import datetime
from typing import Dict, List, Any
import statistics

# Configurações
BASE_URL = "https://dashboard-estoque-v2.fly.dev/teste3"
API_URL = f"{BASE_URL}/api"
TIMEOUT = 30

# Cores para output
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


class TestResult:
    """Armazena resultados de testes"""
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.response_times = []
        self.errors = []
        
    def add_success(self, response_time: float):
        self.total_tests += 1
        self.passed_tests += 1
        self.response_times.append(response_time)
        
    def add_failure(self, error: str, response_time: float = 0):
        self.total_tests += 1
        self.failed_tests += 1
        self.errors.append(error)
        if response_time > 0:
            self.response_times.append(response_time)
            
    def get_metrics(self) -> Dict[str, Any]:
        if self.response_times:
            return {
                "total_tests": self.total_tests,
                "passed": self.passed_tests,
                "failed": self.failed_tests,
                "avg_response_time": statistics.mean(self.response_times),
                "min_response_time": min(self.response_times),
                "max_response_time": max(self.response_times),
                "p95_response_time": statistics.quantiles(self.response_times, n=20)[18] if len(self.response_times) > 20 else max(self.response_times),
                "success_rate": (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
            }
        return {
            "total_tests": self.total_tests,
            "passed": self.passed_tests,
            "failed": self.failed_tests,
            "success_rate": 0
        }


def print_section(title: str):
    """Imprime seção formatada"""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{title}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")


def test_health_check() -> TestResult:
    """Testa endpoints de health check"""
    print_section("1. TESTE DE HEALTH CHECK")
    result = TestResult()
    
    # Teste 1: Health check básico
    print("1.1 Health check básico...")
    try:
        start = time.time()
        response = requests.get(f"{API_URL}/health", timeout=TIMEOUT)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") in ["healthy", "degraded"]:
                result.add_success(elapsed)
                print(f"{GREEN}✓ Health check OK - Status: {data['status']} ({elapsed:.2f}s){RESET}")
            else:
                result.add_failure(f"Status inesperado: {data.get('status')}", elapsed)
                print(f"{RED}✗ Status inesperado{RESET}")
        else:
            result.add_failure(f"HTTP {response.status_code}", elapsed)
            print(f"{RED}✗ Erro HTTP {response.status_code}{RESET}")
    except Exception as e:
        result.add_failure(str(e))
        print(f"{RED}✗ Erro: {e}{RESET}")
    
    # Teste 2: Health check detalhado
    print("\n1.2 Health check detalhado...")
    try:
        start = time.time()
        response = requests.get(f"{API_URL}/health/detailed", timeout=TIMEOUT)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            result.add_success(elapsed)
            print(f"{GREEN}✓ Health check detalhado OK ({elapsed:.2f}s){RESET}")
            
            # Verifica componentes
            checks = data.get("checks", {})
            for component, status in checks.items():
                status_color = GREEN if status.get("status") == "ok" else RED
                print(f"  - {component}: {status_color}{status.get('status', 'unknown')}{RESET}")
        else:
            result.add_failure(f"HTTP {response.status_code}", elapsed)
            print(f"{RED}✗ Erro HTTP {response.status_code}{RESET}")
    except Exception as e:
        result.add_failure(str(e))
        print(f"{RED}✗ Erro: {e}{RESET}")
    
    return result


def test_produtos_api() -> TestResult:
    """Testa API de produtos"""
    print_section("2. TESTE DE API DE PRODUTOS")
    result = TestResult()
    
    # Teste 1: Listar produtos
    print("2.1 Listando produtos...")
    try:
        start = time.time()
        response = requests.get(f"{API_URL}/produtos", timeout=TIMEOUT)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            result.add_success(elapsed)
            print(f"{GREEN}✓ Listagem OK - {data.get('total', 0)} produtos ({elapsed:.2f}s){RESET}")
            print(f"  - Source: {data.get('source', 'unknown')}")
        else:
            result.add_failure(f"HTTP {response.status_code}", elapsed)
            print(f"{RED}✗ Erro HTTP {response.status_code}{RESET}")
    except Exception as e:
        result.add_failure(str(e))
        print(f"{RED}✗ Erro: {e}{RESET}")
    
    # Teste 2: Buscar produto
    print("\n2.2 Buscando produto por nome...")
    try:
        start = time.time()
        response = requests.get(f"{API_URL}/produtos/buscar?nome=teste", timeout=TIMEOUT)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            result.add_success(elapsed)
            print(f"{GREEN}✓ Busca OK - {data.get('total', 0)} resultados ({elapsed:.2f}s){RESET}")
        else:
            result.add_failure(f"HTTP {response.status_code}", elapsed)
            print(f"{RED}✗ Erro HTTP {response.status_code}{RESET}")
    except Exception as e:
        result.add_failure(str(e))
        print(f"{RED}✗ Erro: {e}{RESET}")
    
    # Teste 3: Sincronizar produtos
    print("\n2.3 Sincronizando produtos...")
    try:
        start = time.time()
        response = requests.post(f"{API_URL}/produtos/sync", timeout=TIMEOUT)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            result.add_success(elapsed)
            print(f"{GREEN}✓ Sincronização OK - {data.get('produtos_salvos', 0)} salvos ({elapsed:.2f}s){RESET}")
        else:
            result.add_failure(f"HTTP {response.status_code}", elapsed)
            print(f"{RED}✗ Erro HTTP {response.status_code}{RESET}")
    except Exception as e:
        result.add_failure(str(e))
        print(f"{RED}✗ Erro: {e}{RESET}")
    
    return result


def test_concurrent_requests() -> TestResult:
    """Testa requisições simultâneas"""
    print_section("3. TESTE DE CARGA (10 REQUISIÇÕES SIMULTÂNEAS)")
    result = TestResult()
    
    def make_request(i: int) -> tuple:
        """Faz uma requisição e retorna resultado"""
        try:
            start = time.time()
            response = requests.get(f"{API_URL}/health", timeout=TIMEOUT)
            elapsed = time.time() - start
            
            if response.status_code == 200:
                return (True, elapsed, None)
            else:
                return (False, elapsed, f"HTTP {response.status_code}")
        except Exception as e:
            return (False, 0, str(e))
    
    # Executa 10 requisições simultâneas
    print("Executando 10 requisições simultâneas...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request, i) for i in range(10)]
        
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            success, elapsed, error = future.result()
            
            if success:
                result.add_success(elapsed)
                print(f"{GREEN}✓ Requisição {i+1}/10 OK ({elapsed:.2f}s){RESET}")
            else:
                result.add_failure(error or "Unknown error", elapsed)
                print(f"{RED}✗ Requisição {i+1}/10 falhou: {error}{RESET}")
    
    return result


def test_rate_limiting() -> TestResult:
    """Testa rate limiting"""
    print_section("4. TESTE DE RATE LIMITING")
    result = TestResult()
    
    print("Enviando 30 requisições rápidas para testar rate limiting...")
    rate_limited = False
    
    for i in range(30):
        try:
            start = time.time()
            response = requests.get(f"{API_URL}/health", timeout=5)
            elapsed = time.time() - start
            
            if response.status_code == 429:  # Too Many Requests
                rate_limited = True
                result.add_success(elapsed)
                print(f"{YELLOW}! Rate limit ativado na requisição {i+1} (esperado){RESET}")
                break
            elif response.status_code == 200:
                result.add_success(elapsed)
                if i % 5 == 0:
                    print(f"  Requisição {i+1}/30 OK...")
            else:
                result.add_failure(f"HTTP {response.status_code}", elapsed)
                
        except Exception as e:
            result.add_failure(str(e))
    
    if not rate_limited:
        print(f"{YELLOW}⚠ Rate limiting não detectado (pode estar desabilitado){RESET}")
    
    return result


def test_error_recovery() -> TestResult:
    """Testa recuperação de erros"""
    print_section("5. TESTE DE CONFIABILIDADE E RECUPERAÇÃO")
    result = TestResult()
    
    # Teste 1: Endpoint inválido (404)
    print("5.1 Testando tratamento de erro 404...")
    try:
        start = time.time()
        response = requests.get(f"{API_URL}/endpoint-invalido", timeout=TIMEOUT)
        elapsed = time.time() - start
        
        if response.status_code == 404:
            result.add_success(elapsed)
            print(f"{GREEN}✓ Erro 404 tratado corretamente ({elapsed:.2f}s){RESET}")
        else:
            result.add_failure(f"Esperado 404, recebido {response.status_code}", elapsed)
            print(f"{RED}✗ Status inesperado: {response.status_code}{RESET}")
    except Exception as e:
        result.add_failure(str(e))
        print(f"{RED}✗ Erro: {e}{RESET}")
    
    # Teste 2: Parâmetros inválidos
    print("\n5.2 Testando validação de parâmetros...")
    try:
        start = time.time()
        response = requests.get(f"{API_URL}/produtos/buscar", timeout=TIMEOUT)  # Sem parâmetros
        elapsed = time.time() - start
        
        if response.status_code == 400:
            result.add_success(elapsed)
            print(f"{GREEN}✓ Validação de parâmetros OK ({elapsed:.2f}s){RESET}")
        else:
            result.add_failure(f"Esperado 400, recebido {response.status_code}", elapsed)
            print(f"{RED}✗ Status inesperado: {response.status_code}{RESET}")
    except Exception as e:
        result.add_failure(str(e))
        print(f"{RED}✗ Erro: {e}{RESET}")
    
    # Teste 3: Retry automático
    print("\n5.3 Testando retry automático...")
    retry_count = 0
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            start = time.time()
            response = requests.get(f"{API_URL}/health", timeout=5)
            elapsed = time.time() - start
            
            if response.status_code == 200:
                result.add_success(elapsed)
                print(f"{GREEN}✓ Requisição bem-sucedida na tentativa {attempt + 1} ({elapsed:.2f}s){RESET}")
                break
            else:
                retry_count += 1
                print(f"{YELLOW}  Retry {retry_count}/{max_retries}...{RESET}")
                time.sleep(1)
        except Exception as e:
            retry_count += 1
            if retry_count < max_retries:
                print(f"{YELLOW}  Retry {retry_count}/{max_retries} após erro: {e}{RESET}")
                time.sleep(1)
            else:
                result.add_failure(f"Falha após {max_retries} tentativas: {e}")
                print(f"{RED}✗ Falha após {max_retries} tentativas{RESET}")
    
    return result


def test_cache_behavior() -> TestResult:
    """Testa comportamento do cache"""
    print_section("6. TESTE DE CACHE")
    result = TestResult()
    
    # Teste 1: Primeira requisição (sem cache)
    print("6.1 Primeira requisição (deve buscar da API)...")
    try:
        start = time.time()
        response = requests.get(f"{API_URL}/produtos?usar_cache=false", timeout=TIMEOUT)
        elapsed1 = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            source1 = data.get("source", "unknown")
            result.add_success(elapsed1)
            print(f"{GREEN}✓ Requisição OK - Source: {source1} ({elapsed1:.2f}s){RESET}")
        else:
            result.add_failure(f"HTTP {response.status_code}", elapsed1)
            print(f"{RED}✗ Erro HTTP {response.status_code}{RESET}")
            return result
    except Exception as e:
        result.add_failure(str(e))
        print(f"{RED}✗ Erro: {e}{RESET}")
        return result
    
    # Teste 2: Segunda requisição (deve vir do cache)
    print("\n6.2 Segunda requisição (deve vir do cache)...")
    time.sleep(1)  # Pequena pausa
    
    try:
        start = time.time()
        response = requests.get(f"{API_URL}/produtos?usar_cache=true", timeout=TIMEOUT)
        elapsed2 = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            source2 = data.get("source", "unknown")
            result.add_success(elapsed2)
            print(f"{GREEN}✓ Requisição OK - Source: {source2} ({elapsed2:.2f}s){RESET}")
            
            # Verifica se veio do cache e foi mais rápido
            if source2 == "cache" and elapsed2 < elapsed1:
                print(f"{GREEN}✓ Cache funcionando! Speedup: {elapsed1/elapsed2:.1f}x{RESET}")
            elif source2 != "cache":
                print(f"{YELLOW}⚠ Esperado source=cache, recebido {source2}{RESET}")
        else:
            result.add_failure(f"HTTP {response.status_code}", elapsed2)
            print(f"{RED}✗ Erro HTTP {response.status_code}{RESET}")
    except Exception as e:
        result.add_failure(str(e))
        print(f"{RED}✗ Erro: {e}{RESET}")
    
    return result


def generate_report(results: Dict[str, TestResult]) -> float:
    """Gera relatório final e calcula nota"""
    print_section("RELATÓRIO FINAL")
    
    total_tests = 0
    total_passed = 0
    all_response_times = []
    all_errors = []
    
    # Consolida resultados
    for test_name, result in results.items():
        metrics = result.get_metrics()
        total_tests += metrics["total_tests"]
        total_passed += metrics["passed"]
        all_response_times.extend(result.response_times)
        all_errors.extend(result.errors)
    
    # Calcula métricas globais
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total de testes executados: {total_tests}")
    print(f"Testes aprovados: {GREEN}{total_passed}{RESET}")
    print(f"Testes falhados: {RED}{total_tests - total_passed}{RESET}")
    print(f"Taxa de sucesso: {GREEN if success_rate >= 90 else YELLOW if success_rate >= 70 else RED}{success_rate:.1f}%{RESET}")
    
    if all_response_times:
        print(f"\nMétricas de Performance:")
        print(f"  - Tempo médio de resposta: {statistics.mean(all_response_times):.3f}s")
        print(f"  - Tempo mínimo: {min(all_response_times):.3f}s")
        print(f"  - Tempo máximo: {max(all_response_times):.3f}s")
        if len(all_response_times) > 20:
            p95 = statistics.quantiles(all_response_times, n=20)[18]
            print(f"  - P95: {p95:.3f}s")
    
    if all_errors:
        print(f"\nErros encontrados:")
        for error in all_errors[:5]:  # Mostra até 5 erros
            print(f"  - {RED}{error}{RESET}")
        if len(all_errors) > 5:
            print(f"  ... e mais {len(all_errors) - 5} erros")
    
    # Calcula nota
    nota = 10.0
    
    # Penalizações
    if success_rate < 100:
        nota -= (100 - success_rate) * 0.05  # -0.05 por cada 1% de falha
    
    if all_response_times:
        avg_time = statistics.mean(all_response_times)
        if avg_time > 2.0:
            nota -= 2.0  # -2 pontos se média > 2s
        elif avg_time > 1.0:
            nota -= 1.0  # -1 ponto se média > 1s
        elif avg_time > 0.5:
            nota -= 0.5  # -0.5 ponto se média > 0.5s
    
    # Bônus
    if success_rate == 100:
        nota += 0.5  # +0.5 se todos os testes passaram
    
    nota = max(0, min(10, nota))  # Limita entre 0 e 10
    
    print(f"\n{BLUE}{'=' * 30}{RESET}")
    print(f"{BLUE}NOTA FINAL: {nota:.1f}/10{RESET}")
    print(f"{BLUE}{'=' * 30}{RESET}")
    
    return nota


def main():
    """Função principal"""
    print(f"{BLUE}╔══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BLUE}║     TESTE AUTOMATIZADO - DASHBOARD NEXT v2 - TESTE3      ║{RESET}")
    print(f"{BLUE}║           QA Tester 3 - Automatizado (Pragmático)        ║{RESET}")
    print(f"{BLUE}╚══════════════════════════════════════════════════════════╝{RESET}")
    
    print(f"\nURL do sistema: {BASE_URL}")
    print(f"Iniciando testes em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Executa todos os testes
    results = {
        "health": test_health_check(),
        "produtos": test_produtos_api(),
        "concurrent": test_concurrent_requests(),
        "rate_limit": test_rate_limiting(),
        "recovery": test_error_recovery(),
        "cache": test_cache_behavior()
    }
    
    # Gera relatório
    nota = generate_report(results)
    
    print(f"\nTestes finalizados em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Salva resultados em arquivo JSON
    output = {
        "timestamp": datetime.now().isoformat(),
        "url": BASE_URL,
        "nota": nota,
        "resultados": {}
    }
    
    for test_name, result in results.items():
        output["resultados"][test_name] = result.get_metrics()
    
    with open("test_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResultados salvos em: test_results.json")


if __name__ == "__main__":
    main()