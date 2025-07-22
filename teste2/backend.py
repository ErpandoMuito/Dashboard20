from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import redis
import httpx
from datetime import datetime
import traceback
import sys
import json
from typing import Dict, Any
import logging
from pathlib import Path

# Configurar logging com rotação de arquivos
from logging.handlers import RotatingFileHandler

# Criar handler com rotação (máx 10MB, mantém 3 backups)
file_handler = RotatingFileHandler(
    'debug.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=3
)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        file_handler
    ]
)
logger = logging.getLogger(__name__)

# Log inicial do sistema
logger.info("=" * 80)
logger.info("INICIANDO SISTEMA DE DEBUG - LOGS SÃO VIDA!")
logger.info("=" * 80)

# Variáveis globais para debug
redis_client = None
startup_logs = []
api_call_history = []
MAX_STARTUP_LOGS = 1000  # Limite de logs de startup em memória
MAX_API_HISTORY = 500    # Limite de histórico de API em memória

def log_and_store(message: str, level: str = "INFO"):
    """Log e armazena mensagem para visualização posterior com limite"""
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "level": level,
        "message": message
    }
    startup_logs.append(log_entry)
    
    # Limitar tamanho da lista de logs
    if len(startup_logs) > MAX_STARTUP_LOGS:
        startup_logs.pop(0)  # Remove o mais antigo
    
    if level == "ERROR":
        logger.error(message)
    elif level == "WARNING":
        logger.warning(message)
    else:
        logger.info(message)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciador de ciclo de vida com MUITO logging"""
    global redis_client
    
    log_and_store("🚀 INICIANDO APLICAÇÃO...")
    
    # Carregar variáveis de ambiente do .env se existir
    env_file = Path(".env")
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv()
            log_and_store("✅ Arquivo .env carregado")
        except Exception as e:
            log_and_store(f"⚠️ Erro ao carregar .env: {str(e)}", "WARNING")
    else:
        log_and_store("ℹ️ Arquivo .env não encontrado, usando variáveis do sistema")
    
    # Log todas as variáveis de ambiente
    log_and_store("📋 VARIÁVEIS DE AMBIENTE:")
    for key, value in os.environ.items():
        if 'TOKEN' in key or 'SECRET' in key or 'PASSWORD' in key:
            masked_value = value[:4] + '*' * (len(value) - 4) if len(value) > 4 else '***'
            log_and_store(f"  {key} = {masked_value}")
        else:
            log_and_store(f"  {key} = {value}")
    
    # Tentar conectar ao Redis
    try:
        log_and_store("🔌 Tentando conectar ao Redis...")
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        log_and_store(f"  URL: {redis_url}")
        
        redis_client = redis.from_url(redis_url, decode_responses=True)
        
        # Testar conexão
        log_and_store("  Testando PING...")
        pong = redis_client.ping()
        log_and_store(f"  ✅ Redis respondeu: {pong}")
        
        # Informações do Redis
        info = redis_client.info()
        log_and_store(f"  📊 Redis versão: {info.get('redis_version', 'unknown')}")
        log_and_store(f"  💾 Memória usada: {info.get('used_memory_human', 'unknown')}")
        
    except Exception as e:
        log_and_store(f"❌ ERRO ao conectar ao Redis: {str(e)}", "ERROR")
        log_and_store(f"  Stack trace: {traceback.format_exc()}", "ERROR")
        redis_client = None
    
    # Verificar API Tiny
    tiny_token = os.getenv('TINY_API_TOKEN', '')
    if tiny_token:
        log_and_store(f"🔑 Token Tiny encontrado: {tiny_token[:10]}...")
    else:
        log_and_store("⚠️ Token Tiny NÃO encontrado!", "WARNING")
    
    log_and_store("✅ Aplicação iniciada com sucesso!")
    
    yield
    
    # Shutdown
    log_and_store("🛑 ENCERRANDO APLICAÇÃO...")
    if redis_client:
        redis_client.close()
        log_and_store("  Redis desconectado")
    log_and_store("👋 Aplicação encerrada")

# Criar app FastAPI
app = FastAPI(
    title="Dashboard Debug - Logs São Vida",
    version="1.0.0",
    lifespan=lifespan
)

# CORS com logging
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para logar TODAS as requisições
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.now()
    
    # Log da requisição
    log_entry = {
        "timestamp": start_time.isoformat(),
        "method": request.method,
        "path": request.url.path,
        "query": str(request.url.query),
        "headers": dict(request.headers)
    }
    
    logger.info(f"📥 REQUEST: {request.method} {request.url.path}")
    logger.debug(f"  Headers: {dict(request.headers)}")
    logger.debug(f"  Query: {request.url.query}")
    
    try:
        # Processar requisição
        response = await call_next(request)
        
        # Log da resposta
        duration = (datetime.now() - start_time).total_seconds()
        log_entry["duration_seconds"] = duration
        log_entry["status_code"] = response.status_code
        
        logger.info(f"📤 RESPONSE: {response.status_code} - {duration:.3f}s")
        
        # Salvar no histórico com limite maior
        api_call_history.append(log_entry)
        if len(api_call_history) > MAX_API_HISTORY:
            api_call_history.pop(0)
        
        return response
        
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        log_entry["duration_seconds"] = duration
        log_entry["error"] = str(e)
        log_entry["traceback"] = traceback.format_exc()
        
        logger.error(f"💥 ERRO na requisição: {str(e)}")
        logger.error(f"  Stack trace:\n{traceback.format_exc()}")
        
        api_call_history.append(log_entry)
        raise

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# ENDPOINTS DE DEBUG
@app.get("/debug/env")
async def debug_env():
    """Mostra todas as variáveis de ambiente (com máscaras para senhas)"""
    logger.info("🔍 Endpoint /debug/env chamado")
    
    env_vars = {}
    for key, value in os.environ.items():
        if any(sensitive in key.upper() for sensitive in ['TOKEN', 'SECRET', 'PASSWORD', 'KEY']):
            env_vars[key] = value[:4] + '*' * (len(value) - 4) if len(value) > 4 else '***'
        else:
            env_vars[key] = value
    
    return {
        "environment_variables": env_vars,
        "python_version": sys.version,
        "current_directory": os.getcwd(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/debug/redis")
async def debug_redis():
    """Testa conexão com Redis e mostra informações"""
    logger.info("🔍 Endpoint /debug/redis chamado")
    
    if not redis_client:
        logger.error("Redis client não está inicializado!")
        return {
            "status": "error",
            "message": "Redis client não inicializado",
            "connected": False
        }
    
    try:
        # Ping
        ping_result = redis_client.ping()
        logger.info(f"  Redis PING: {ping_result}")
        
        # Info
        info = redis_client.info()
        
        # Testar escrita/leitura
        test_key = "debug:test"
        test_value = f"teste_{datetime.now().isoformat()}"
        redis_client.set(test_key, test_value, ex=60)
        read_value = redis_client.get(test_key)
        
        logger.info(f"  Teste escrita/leitura: {read_value == test_value}")
        
        # Contar chaves
        keys_count = redis_client.dbsize()
        logger.info(f"  Total de chaves: {keys_count}")
        
        return {
            "status": "success",
            "connected": True,
            "ping": ping_result,
            "redis_version": info.get("redis_version"),
            "used_memory": info.get("used_memory_human"),
            "connected_clients": info.get("connected_clients"),
            "total_keys": keys_count,
            "write_read_test": read_value == test_value,
            "test_details": {
                "written": test_value,
                "read": read_value
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao testar Redis: {str(e)}")
        logger.error(f"Stack trace:\n{traceback.format_exc()}")
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc(),
            "connected": False
        }

@app.get("/debug/tiny")
async def debug_tiny():
    """Testa conexão com API Tiny"""
    logger.info("🔍 Endpoint /debug/tiny chamado")
    
    token = os.getenv('TINY_API_TOKEN', '')
    if not token:
        logger.error("Token Tiny não configurado!")
        return {
            "status": "error",
            "message": "TINY_API_TOKEN não configurado",
            "has_token": False
        }
    
    try:
        logger.info(f"  Testando com token: {token[:10]}...")
        
        async with httpx.AsyncClient() as client:
            # Testar endpoint de informações da conta
            response = await client.post(
                "https://api.tiny.com.br/api2/info.conta.php",
                data={
                    "token": token,
                    "formato": "JSON"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30.0  # Aumentar timeout para 30s
            )
            
            logger.info(f"  Status HTTP: {response.status_code}")
            logger.debug(f"  Headers resposta: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"  Resposta: {json.dumps(data, indent=2)}")
                
                return {
                    "status": "success",
                    "http_status": response.status_code,
                    "has_token": True,
                    "response": data,
                    "headers": dict(response.headers)
                }
            else:
                logger.error(f"  Erro HTTP: {response.status_code}")
                logger.error(f"  Body: {response.text}")
                
                return {
                    "status": "error",
                    "http_status": response.status_code,
                    "message": response.text,
                    "has_token": True
                }
                
    except Exception as e:
        logger.error(f"Erro ao testar Tiny: {str(e)}")
        logger.error(f"Stack trace:\n{traceback.format_exc()}")
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc(),
            "has_token": True
        }

@app.get("/debug/static")
async def debug_static():
    """Lista arquivos estáticos disponíveis"""
    logger.info("🔍 Endpoint /debug/static chamado")
    
    static_dir = "static"
    files = []
    
    try:
        for root, dirs, filenames in os.walk(static_dir):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, static_dir)
                size = os.path.getsize(filepath)
                modified = datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                
                files.append({
                    "path": rel_path,
                    "size_bytes": size,
                    "modified": modified
                })
                
        logger.info(f"  Encontrados {len(files)} arquivos estáticos")
        
        return {
            "static_directory": os.path.abspath(static_dir),
            "files_count": len(files),
            "files": files
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar arquivos: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

@app.get("/debug/logs")
async def debug_logs():
    """Retorna logs de startup e histórico de chamadas com limites"""
    logger.info("🔍 Endpoint /debug/logs chamado")
    
    # Retornar apenas os últimos logs para evitar sobrecarga
    recent_startup = startup_logs[-200:] if len(startup_logs) > 200 else startup_logs
    recent_api = api_call_history[-100:] if len(api_call_history) > 100 else api_call_history
    
    return {
        "startup_logs": recent_startup,
        "api_call_history": recent_api,
        "total_startup_logs": len(startup_logs),
        "total_api_calls": len(api_call_history),
        "logs_truncated": len(startup_logs) > 200 or len(api_call_history) > 100,
        "current_time": datetime.now().isoformat(),
        "memory_limits": {
            "max_startup_logs": MAX_STARTUP_LOGS,
            "max_api_history": MAX_API_HISTORY
        }
    }

@app.get("/debug/test-error")
async def debug_test_error():
    """Endpoint para testar tratamento de erros"""
    logger.info("🔍 Endpoint /debug/test-error chamado")
    logger.warning("⚠️ Este endpoint vai gerar um erro proposital!")
    
    try:
        # Forçar erro
        x = 1 / 0
    except Exception as e:
        logger.error(f"💥 ERRO CAPTURADO: {str(e)}")
        logger.error(f"Stack trace:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc()
            }
        )

# ENDPOINTS PRINCIPAIS
@app.get("/")
async def root():
    """Endpoint raiz com informações do sistema"""
    logger.info("🏠 Endpoint / chamado")
    
    return {
        "message": "Dashboard Debug - Logs São Vida! 🔍",
        "endpoints": {
            "debug": [
                "/debug/env - Variáveis de ambiente",
                "/debug/redis - Status do Redis",
                "/debug/tiny - Teste API Tiny",
                "/debug/static - Arquivos estáticos",
                "/debug/logs - Logs do sistema",
                "/debug/test-error - Testar erro"
            ],
            "api": [
                "/api/health - Status da API",
                "/api/notas - Listar notas",
                "/api/produtos - Listar produtos"
            ]
        },
        "timestamp": datetime.now().isoformat(),
        "uptime_logs": len(startup_logs),
        "api_calls": len(api_call_history)
    }

@app.get("/api/health")
async def health():
    """Health check com status detalhado"""
    logger.info("🏥 Health check chamado")
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "up",
            "redis": "unknown",
            "tiny": "unknown"
        }
    }
    
    # Verificar Redis
    try:
        if redis_client and redis_client.ping():
            health_status["services"]["redis"] = "up"
        else:
            health_status["services"]["redis"] = "down"
            health_status["status"] = "degraded"
    except:
        health_status["services"]["redis"] = "error"
        health_status["status"] = "degraded"
    
    # Verificar Tiny
    if os.getenv('TINY_API_TOKEN'):
        health_status["services"]["tiny"] = "configured"
    else:
        health_status["services"]["tiny"] = "not_configured"
        health_status["status"] = "degraded"
    
    logger.info(f"  Status: {health_status['status']}")
    logger.info(f"  Serviços: {health_status['services']}")
    
    return health_status

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Iniciando servidor Uvicorn...")
    logger.info(f"  Diretório atual: {os.getcwd()}")
    logger.info(f"  Python: {sys.version}")
    
    uvicorn.run(
        "backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug",
        access_log=True
    )