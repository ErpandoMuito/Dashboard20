#!/usr/bin/env python3
"""
Script de teste para verificar o sistema de debug
LOGS SÃO VIDA!
"""

import requests
import json
import time
from datetime import datetime

# Configuração
BASE_URL = "http://localhost:8000"

# Cores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def log(message, color=None):
    """Log com timestamp e cor"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    if color:
        print(f"[{timestamp}] {color}{message}{Colors.END}")
    else:
        print(f"[{timestamp}] {message}")

def test_endpoint(endpoint, name):
    """Testa um endpoint e mostra resultado"""
    log(f"\n{'='*60}", Colors.BLUE)
    log(f"Testando: {name}", Colors.BOLD)
    log(f"Endpoint: {endpoint}", Colors.BLUE)
    
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        duration = time.time() - start
        
        log(f"Status: {response.status_code}", 
            Colors.GREEN if response.status_code == 200 else Colors.RED)
        log(f"Tempo: {duration:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            log("Resposta:", Colors.GREEN)
            print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
            if len(json.dumps(data)) > 500:
                log("... (resposta truncada)", Colors.YELLOW)
        else:
            log(f"Erro: {response.text}", Colors.RED)
            
        return response.status_code == 200
        
    except Exception as e:
        log(f"ERRO: {str(e)}", Colors.RED)
        return False

def check_server_running():
    """Verifica se o servidor está rodando"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    """Executa todos os testes"""
    log("🔍 SISTEMA DE TESTE DEBUG - LOGS SÃO VIDA! 🔍", Colors.BOLD)
    log(f"Testando API em: {BASE_URL}", Colors.BLUE)
    
    # Verificar se o servidor está rodando
    log("\nVerificando se o servidor está disponível...", Colors.YELLOW)
    if not check_server_running():
        log("❌ ERRO: Servidor não está rodando!", Colors.RED)
        log(f"Certifique-se de que o servidor está rodando em {BASE_URL}", Colors.YELLOW)
        log("Execute: ./run.sh ou python3 backend.py", Colors.YELLOW)
        return
    
    # Lista de endpoints para testar
    tests = [
        ("/", "API Root"),
        ("/api/health", "Health Check"),
        ("/debug/env", "Variáveis de Ambiente"),
        ("/debug/redis", "Conexão Redis"),
        ("/debug/tiny", "API Tiny"),
        ("/debug/static", "Arquivos Estáticos"),
        ("/debug/logs", "Logs do Sistema"),
    ]
    
    results = []
    
    # Executar testes
    for endpoint, name in tests:
        success = test_endpoint(endpoint, name)
        results.append((name, success))
        time.sleep(0.5)  # Pequena pausa entre testes
    
    # Teste de erro proposital
    log(f"\n{'='*60}", Colors.YELLOW)
    log("Testando tratamento de erro (deve falhar):", Colors.YELLOW)
    test_endpoint("/debug/test-error", "Erro Proposital")
    
    # Resumo
    log(f"\n{'='*60}", Colors.BOLD)
    log("RESUMO DOS TESTES:", Colors.BOLD)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        color = Colors.GREEN if success else Colors.RED
        log(f"  {name}: {status}", color)
    
    log(f"\nTotal: {passed}/{total} testes passaram", 
        Colors.GREEN if passed == total else Colors.YELLOW)
    
    # Dica final
    log(f"\n{'='*60}", Colors.BLUE)
    log("💡 DICAS:", Colors.BOLD)
    log("1. Acesse http://localhost:8000/static/index.html para interface visual")
    log("2. Veja os logs em tempo real com: tail -f debug.log")
    log("3. Todos os logs também aparecem no console do browser")
    log("4. Use o botão 'TESTAR TUDO' na interface para teste completo")
    
    log("\n🔍 LEMBRE-SE: LOGS SÃO VIDA! 🔍", Colors.BOLD)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\n\nTeste interrompido pelo usuário", Colors.YELLOW)
    except Exception as e:
        log(f"\n\nERRO FATAL: {str(e)}", Colors.RED)
        import traceback
        traceback.print_exc()