#!/usr/bin/env python3
"""
🧪 TESTE RÁPIDO - Valida se tudo funciona!
"""

import asyncio
import httpx
import json
from datetime import datetime

# ANSI colors para output bonito
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

async def test_api():
    """Testa todos endpoints principais"""
    
    base_url = "http://localhost:8000"
    client = httpx.AsyncClient()
    
    tests = {
        "1. Health Check": {
            "method": "GET",
            "url": f"{base_url}/api/health",
            "expected": lambda r: r.status_code == 200
        },
        "2. Dashboard Data": {
            "method": "GET", 
            "url": f"{base_url}/api/dashboard",
            "expected": lambda r: r.status_code == 200 and "metricas" in r.json()
        },
        "3. Listar Notas": {
            "method": "GET",
            "url": f"{base_url}/api/notas",
            "expected": lambda r: r.status_code == 200
        },
        "4. Proxy Tiny": {
            "method": "POST",
            "url": f"{base_url}/api/tiny-proxy",
            "json": {"endpoint": "notas.pesquisa", "params": {}},
            "expected": lambda r: r.status_code == 200
        },
        "5. Frontend": {
            "method": "GET",
            "url": f"{base_url}/",
            "expected": lambda r: r.status_code == 200
        }
    }
    
    print(f"\n{BLUE}🧪 EXECUTANDO TESTES RÁPIDOS{RESET}\n")
    
    passed = 0
    failed = 0
    
    for name, test in tests.items():
        try:
            if test["method"] == "GET":
                response = await client.get(test["url"])
            else:
                response = await client.post(
                    test["url"], 
                    json=test.get("json", {})
                )
            
            if test["expected"](response):
                print(f"{GREEN}✅ {name}{RESET}")
                passed += 1
                
                # Mostra preview dos dados
                if response.headers.get("content-type", "").startswith("application/json"):
                    data = response.json()
                    preview = json.dumps(data, indent=2)[:200] + "..."
                    print(f"   {preview}\n")
            else:
                print(f"{RED}❌ {name}{RESET}")
                failed += 1
                
        except Exception as e:
            print(f"{RED}❌ {name} - Erro: {str(e)}{RESET}")
            failed += 1
    
    await client.aclose()
    
    # Resumo
    print(f"\n{BLUE}📊 RESUMO DOS TESTES{RESET}")
    print(f"{GREEN}✅ Passou: {passed}{RESET}")
    print(f"{RED}❌ Falhou: {failed}{RESET}")
    
    if failed == 0:
        print(f"\n{GREEN}🎉 TODOS OS TESTES PASSARAM! O SISTEMA ESTÁ 100% FUNCIONAL!{RESET}\n")
    else:
        print(f"\n{YELLOW}⚠️  Alguns testes falharam. Verifique se o servidor está rodando.{RESET}\n")

async def test_websocket():
    """Testa conexão WebSocket"""
    
    print(f"{BLUE}🔌 TESTANDO WEBSOCKET...{RESET}")
    
    try:
        import websockets
        
        async with websockets.connect("ws://localhost:8000/ws") as ws:
            # Espera uma mensagem
            message = await asyncio.wait_for(ws.recv(), timeout=5.0)
            data = json.loads(message)
            
            if data.get("type") == "update":
                print(f"{GREEN}✅ WebSocket funcionando! Recebeu update: {data}{RESET}")
            else:
                print(f"{YELLOW}⚠️  WebSocket conectou mas dados inesperados{RESET}")
                
    except asyncio.TimeoutError:
        print(f"{YELLOW}⚠️  WebSocket conectou mas não recebeu dados em 5s{RESET}")
    except Exception as e:
        print(f"{RED}❌ WebSocket erro: {str(e)}{RESET}")

async def main():
    """Executa todos os testes"""
    
    print(f"""
{BLUE}╔═══════════════════════════════════════╗
║       🚀 TESTE RÁPIDO DO SISTEMA      ║
║          Dashboard Hacker v1.0        ║
╚═══════════════════════════════════════╝{RESET}
    """)
    
    # Testa API
    await test_api()
    
    # Testa WebSocket
    await test_websocket()
    
    print(f"""
{GREEN}💡 DICAS:{RESET}
- Se os testes falharam, execute: ./start.sh
- Acesse o dashboard em: http://localhost:8000
- Veja a documentação em: http://localhost:8000/docs
    """)

if __name__ == "__main__":
    asyncio.run(main())