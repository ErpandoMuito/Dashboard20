#!/usr/bin/env python3
"""
Stress Test Suite para Sistema Notas/Pedidos
Testa condições extremas, falhas e recuperação
"""

import asyncio
import aiohttp
import time
import random
import json
import subprocess
import sys
from datetime import datetime
from typing import List, Dict, Any
import signal
import os

# Configurações
BASE_URL = "http://localhost:8000"
TOTAL_REQUESTS = 1000
CONCURRENT_USERS = 50
RAPID_TOGGLE_COUNT = 100

# Cores para output
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
RESET = '\033[0m'

class StressTestSuite:
    def __init__(self):
        self.session = None
        self.results = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "errors": [],
            "data_consistency_checks": [],
            "recovery_times": []
        }
        
    async def setup(self):
        """Inicializa sessão HTTP"""
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
    async def teardown(self):
        """Limpa recursos"""
        if self.session:
            await self.session.close()
            
    async def make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Faz uma requisição e mede o tempo de resposta"""
        start_time = time.time()
        try:
            async with self.session.request(method, f"{BASE_URL}{endpoint}", json=data) as resp:
                response_time = time.time() - start_time
                self.results["response_times"].append(response_time)
                self.results["total_requests"] += 1
                
                if resp.status == 200:
                    self.results["successful_requests"] += 1
                    return await resp.json()
                else:
                    self.results["failed_requests"] += 1
                    error = f"Status {resp.status}: {await resp.text()}"
                    self.results["errors"].append(error)
                    return None
                    
        except Exception as e:
            response_time = time.time() - start_time
            self.results["response_times"].append(response_time)
            self.results["total_requests"] += 1
            self.results["failed_requests"] += 1
            self.results["errors"].append(str(e))
            return None
            
    async def test_concurrent_searches(self, produto_codigo: str = "PH-510"):
        """Testa buscas simultâneas do mesmo produto"""
        print(f"\n{BLUE}=== TEST 1: Concurrent Searches ==={RESET}")
        print(f"Executando {CONCURRENT_USERS} buscas simultâneas de '{produto_codigo}'...")
        
        tasks = []
        for i in range(CONCURRENT_USERS):
            task = self.make_request("GET", f"/api/produtos/{produto_codigo}")
            tasks.append(task)
            
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        successful = sum(1 for r in results if r is not None)
        print(f"{GREEN}✓ Completo em {total_time:.2f}s{RESET}")
        print(f"  - Sucessos: {successful}/{CONCURRENT_USERS}")
        print(f"  - Tempo médio: {total_time/CONCURRENT_USERS:.3f}s")
        
        # Verifica consistência dos dados
        if successful > 0:
            first_result = next(r for r in results if r is not None)
            inconsistent = 0
            for result in results:
                if result and result != first_result:
                    inconsistent += 1
                    
            if inconsistent > 0:
                print(f"{RED}✗ ALERTA: {inconsistent} respostas inconsistentes!{RESET}")
                self.results["data_consistency_checks"].append({
                    "test": "concurrent_searches",
                    "status": "FAILED",
                    "inconsistent_count": inconsistent
                })
            else:
                print(f"{GREEN}✓ Dados consistentes em todas as respostas{RESET}")
                self.results["data_consistency_checks"].append({
                    "test": "concurrent_searches",
                    "status": "PASSED"
                })
                
    async def test_rapid_quantity_toggle(self, produto_codigo: str = "PH-510"):
        """Testa adição/remoção rápida de quantidades"""
        print(f"\n{BLUE}=== TEST 2: Rapid Quantity Toggle ==={RESET}")
        print(f"Executando {RAPID_TOGGLE_COUNT} operações de toggle...")
        
        # Primeiro, pega o estado inicial
        initial_state = await self.make_request("GET", f"/api/produtos/{produto_codigo}")
        if not initial_state:
            print(f"{RED}✗ Falha ao obter estado inicial{RESET}")
            return
            
        initial_quantity = initial_state.get("quantidade_total", 0)
        print(f"Quantidade inicial: {initial_quantity}")
        
        # Alterna entre adicionar e remover
        operations = []
        for i in range(RAPID_TOGGLE_COUNT):
            if i % 2 == 0:
                # Adiciona 1
                op = self.make_request("POST", "/api/produtos/atualizar", {
                    "codigo": produto_codigo,
                    "delta": 1
                })
            else:
                # Remove 1
                op = self.make_request("POST", "/api/produtos/atualizar", {
                    "codigo": produto_codigo,
                    "delta": -1
                })
            operations.append(op)
            
        start_time = time.time()
        results = await asyncio.gather(*operations)
        total_time = time.time() - start_time
        
        successful = sum(1 for r in results if r is not None)
        print(f"{GREEN}✓ Completo em {total_time:.2f}s{RESET}")
        print(f"  - Operações bem-sucedidas: {successful}/{RAPID_TOGGLE_COUNT}")
        print(f"  - Taxa: {RAPID_TOGGLE_COUNT/total_time:.1f} ops/s")
        
        # Verifica quantidade final
        final_state = await self.make_request("GET", f"/api/produtos/{produto_codigo}")
        if final_state:
            final_quantity = final_state.get("quantidade_total", 0)
            expected_quantity = initial_quantity  # Deve ser o mesmo após toggles pares
            
            if final_quantity == expected_quantity:
                print(f"{GREEN}✓ Quantidade final correta: {final_quantity}{RESET}")
                self.results["data_consistency_checks"].append({
                    "test": "rapid_quantity_toggle",
                    "status": "PASSED"
                })
            else:
                print(f"{RED}✗ ERRO: Quantidade esperada {expected_quantity}, obtida {final_quantity}{RESET}")
                self.results["data_consistency_checks"].append({
                    "test": "rapid_quantity_toggle",
                    "status": "FAILED",
                    "expected": expected_quantity,
                    "actual": final_quantity
                })
                
    async def test_spam_requests(self):
        """Testa spam de requisições variadas"""
        print(f"\n{BLUE}=== TEST 3: Request Spam ==={RESET}")
        print(f"Disparando {TOTAL_REQUESTS} requisições mistas...")
        
        endpoints = [
            ("GET", "/api/produtos/PH-510"),
            ("GET", "/api/notas"),
            ("GET", "/api/pedidos"),
            ("POST", "/api/produtos/atualizar"),
            ("GET", "/health"),
        ]
        
        tasks = []
        for i in range(TOTAL_REQUESTS):
            method, endpoint = random.choice(endpoints)
            
            if endpoint == "/api/produtos/atualizar":
                data = {
                    "codigo": f"TEST-{random.randint(1, 100)}",
                    "delta": random.randint(-10, 10)
                }
                task = self.make_request(method, endpoint, data)
            else:
                task = self.make_request(method, endpoint)
                
            tasks.append(task)
            
            # Adiciona um pequeno delay aleatório para simular tráfego real
            if i % 100 == 0:
                await asyncio.sleep(0.01)
                
        start_time = time.time()
        await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        print(f"{GREEN}✓ Completo em {total_time:.2f}s{RESET}")
        print(f"  - Taxa: {TOTAL_REQUESTS/total_time:.1f} req/s")
        print(f"  - Sucessos: {self.results['successful_requests']}")
        print(f"  - Falhas: {self.results['failed_requests']}")
        
    async def test_connection_failures(self):
        """Simula falhas de conexão e reconexão"""
        print(f"\n{BLUE}=== TEST 4: Connection Failures ==={RESET}")
        
        # Força timeout muito baixo
        old_timeout = self.session.timeout
        self.session.timeout = aiohttp.ClientTimeout(total=0.001)
        
        print("Simulando timeouts de rede...")
        timeout_requests = []
        for i in range(10):
            task = self.make_request("GET", "/api/produtos/PH-510")
            timeout_requests.append(task)
            
        await asyncio.gather(*timeout_requests)
        
        # Restaura timeout normal
        self.session.timeout = old_timeout
        
        print(f"  - Timeouts simulados: {len([e for e in self.results['errors'] if 'timeout' in str(e).lower()])}")
        
        # Testa reconexão
        print("Testando reconexão após falhas...")
        reconnect_start = time.time()
        reconnect_result = await self.make_request("GET", "/health")
        reconnect_time = time.time() - reconnect_start
        
        if reconnect_result:
            print(f"{GREEN}✓ Reconexão bem-sucedida em {reconnect_time:.2f}s{RESET}")
            self.results["recovery_times"].append(reconnect_time)
        else:
            print(f"{RED}✗ Falha na reconexão{RESET}")
            
    def kill_process(self, process_name: str):
        """Mata um processo específico"""
        try:
            subprocess.run(["pkill", "-f", process_name], check=False)
            return True
        except:
            return False
            
    def start_process(self, command: List[str]):
        """Inicia um processo"""
        try:
            subprocess.Popen(command)
            return True
        except:
            return False
            
    async def test_component_failover(self):
        """Testa failover de componentes"""
        print(f"\n{BLUE}=== TEST 5: Component Failover ==={RESET}")
        print(f"{YELLOW}⚠️  Este teste requer que o sistema esteja rodando via docker-compose{RESET}")
        
        components = [
            {
                "name": "Backend",
                "container": "teste5-backend-1",
                "health_endpoint": "/health"
            },
            {
                "name": "Redis",
                "container": "teste5-redis-1", 
                "health_endpoint": "/health"
            },
            {
                "name": "Nginx",
                "container": "teste5-nginx-1",
                "health_endpoint": "/"
            }
        ]
        
        for component in components:
            print(f"\nTestando failover de {component['name']}...")
            
            # Para o container
            print(f"  - Parando {component['container']}...")
            stop_result = subprocess.run(
                ["docker", "stop", component['container']], 
                capture_output=True
            )
            
            if stop_result.returncode != 0:
                print(f"{YELLOW}  - Não foi possível parar {component['container']}{RESET}")
                continue
                
            # Aguarda um momento
            await asyncio.sleep(2)
            
            # Testa se o sistema ainda responde
            failed_request = await self.make_request("GET", component['health_endpoint'])
            
            # Reinicia o container
            print(f"  - Reiniciando {component['container']}...")
            start_time = time.time()
            subprocess.run(
                ["docker", "start", component['container']],
                capture_output=True
            )
            
            # Aguarda recuperação
            recovery_attempts = 0
            while recovery_attempts < 30:  # 30 segundos máximo
                await asyncio.sleep(1)
                health_check = await self.make_request("GET", component['health_endpoint'])
                if health_check:
                    recovery_time = time.time() - start_time
                    print(f"{GREEN}  ✓ {component['name']} recuperado em {recovery_time:.1f}s{RESET}")
                    self.results["recovery_times"].append(recovery_time)
                    break
                recovery_attempts += 1
            else:
                print(f"{RED}  ✗ {component['name']} não se recuperou em 30s{RESET}")
                
    def generate_report(self):
        """Gera relatório detalhado dos testes"""
        print(f"\n{MAGENTA}{'='*60}{RESET}")
        print(f"{MAGENTA}=== STRESS TEST REPORT ==={RESET}")
        print(f"{MAGENTA}{'='*60}{RESET}")
        
        # Estatísticas gerais
        print(f"\n{CYAN}Estatísticas Gerais:{RESET}")
        print(f"  - Total de requisições: {self.results['total_requests']}")
        print(f"  - Requisições bem-sucedidas: {self.results['successful_requests']}")
        print(f"  - Requisições falhadas: {self.results['failed_requests']}")
        
        if self.results['total_requests'] > 0:
            success_rate = (self.results['successful_requests'] / self.results['total_requests']) * 100
            print(f"  - Taxa de sucesso: {success_rate:.1f}%")
            
        # Tempos de resposta
        if self.results['response_times']:
            avg_response = sum(self.results['response_times']) / len(self.results['response_times'])
            min_response = min(self.results['response_times'])
            max_response = max(self.results['response_times'])
            
            print(f"\n{CYAN}Tempos de Resposta:{RESET}")
            print(f"  - Médio: {avg_response:.3f}s")
            print(f"  - Mínimo: {min_response:.3f}s")
            print(f"  - Máximo: {max_response:.3f}s")
            
        # Consistência de dados
        if self.results['data_consistency_checks']:
            print(f"\n{CYAN}Consistência de Dados:{RESET}")
            passed = sum(1 for c in self.results['data_consistency_checks'] if c['status'] == 'PASSED')
            failed = sum(1 for c in self.results['data_consistency_checks'] if c['status'] == 'FAILED')
            print(f"  - Testes passados: {passed}")
            print(f"  - Testes falhados: {failed}")
            
            for check in self.results['data_consistency_checks']:
                if check['status'] == 'FAILED':
                    print(f"    {RED}✗ {check['test']}: {check}{RESET}")
                    
        # Tempos de recuperação
        if self.results['recovery_times']:
            avg_recovery = sum(self.results['recovery_times']) / len(self.results['recovery_times'])
            print(f"\n{CYAN}Recuperação de Falhas:{RESET}")
            print(f"  - Tempo médio de recuperação: {avg_recovery:.1f}s")
            
        # Top erros
        if self.results['errors']:
            print(f"\n{CYAN}Top 5 Erros:{RESET}")
            error_counts = {}
            for error in self.results['errors']:
                error_type = error.split(':')[0]
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
                
            sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            for error_type, count in sorted_errors:
                print(f"  - {error_type}: {count} ocorrências")
                
        # Recomendações
        print(f"\n{CYAN}Recomendações:{RESET}")
        
        if success_rate < 99:
            print(f"  {YELLOW}⚠️  Taxa de sucesso abaixo de 99% - investigar falhas{RESET}")
            
        if avg_response > 1.0:
            print(f"  {YELLOW}⚠️  Tempo médio de resposta alto - otimizar performance{RESET}")
            
        if failed > 0:
            print(f"  {RED}⚠️  Falhas de consistência detectadas - revisar lógica de concorrência{RESET}")
            
        if not self.results['recovery_times']:
            print(f"  {YELLOW}⚠️  Testes de recuperação não executados - rodar com docker-compose{RESET}")
        elif avg_recovery > 10:
            print(f"  {YELLOW}⚠️  Tempo de recuperação alto - melhorar resiliência{RESET}")
            
        print(f"\n{MAGENTA}{'='*60}{RESET}")
        
        # Salva relatório em arquivo
        report_file = f"stress_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n{GREEN}Relatório completo salvo em: {report_file}{RESET}")
        
async def main():
    """Executa suite completa de testes"""
    tester = StressTestSuite()
    
    print(f"{CYAN}{'='*60}{RESET}")
    print(f"{CYAN}STRESS TEST SUITE - Sistema Notas/Pedidos{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")
    print(f"\nIniciando testes de stress em {BASE_URL}...")
    print(f"{YELLOW}Pressione Ctrl+C para interromper{RESET}\n")
    
    try:
        await tester.setup()
        
        # Executa todos os testes
        await tester.test_concurrent_searches()
        await asyncio.sleep(1)
        
        await tester.test_rapid_quantity_toggle()
        await asyncio.sleep(1)
        
        await tester.test_spam_requests()
        await asyncio.sleep(1)
        
        await tester.test_connection_failures()
        await asyncio.sleep(1)
        
        # Teste de failover apenas se solicitado
        if "--with-failover" in sys.argv:
            await tester.test_component_failover()
            
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Testes interrompidos pelo usuário{RESET}")
    except Exception as e:
        print(f"\n{RED}Erro durante os testes: {e}{RESET}")
    finally:
        await tester.teardown()
        
    # Gera relatório final
    tester.generate_report()
    
if __name__ == "__main__":
    # Configura tratamento de sinais
    def signal_handler(sig, frame):
        print(f"\n{YELLOW}Encerrando testes...{RESET}")
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    
    # Roda os testes
    asyncio.run(main())