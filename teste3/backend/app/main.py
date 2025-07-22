from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from prometheus_fastapi_instrumentator import Instrumentator
from .core.config import settings
from .core.redis_client import redis_manager
from .core.logging import setup_logging
from .api import notas, pedidos, produtos, health
import time

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação"""
    try:
        # Startup
        logger.info("Iniciando aplicação...")
        await redis_manager.connect()
        logger.info("Conectado ao Redis")
        yield
    finally:
        # Shutdown
        logger.info("Encerrando aplicação...")
        await redis_manager.disconnect()
        logger.info("Desconectado do Redis")

# Create FastAPI app
app = FastAPI(
    title="Dashboard API",
    version="2.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        logger.error(f"Erro no middleware: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Erro interno do servidor"}
        )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro não tratado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"}
    )

# Instrumentação Prometheus
Instrumentator().instrument(app).expose(app)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(notas.router, prefix="/api/v2/notas", tags=["notas"])
app.include_router(pedidos.router, prefix="/api/v2/pedidos", tags=["pedidos"])
app.include_router(produtos.router, prefix="/api/v2/produtos", tags=["produtos"])

@app.get("/")
async def root():
    return {
        "message": "Dashboard API v2.0",
        "status": "online",
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs",
            "notas": "/api/v2/notas",
            "pedidos": "/api/v2/pedidos",
            "produtos": "/api/v2/produtos"
        }
    }