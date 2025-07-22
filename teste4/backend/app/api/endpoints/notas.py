"""
Notas Fiscais endpoints with full CRUD operations.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from app.models.nota import (
    NotaFiscal, 
    NotaFiscalCreate, 
    NotaFiscalUpdate,
    NotaFiscalFilter
)
from app.models.base import BaseResponse, PaginatedResponse, PaginationParams
from app.services.redis_service import redis_service
from app.api.middleware.rate_limit import limiter
from app.core.logging import get_logger
import uuid

router = APIRouter(prefix="/notas", tags=["Notas Fiscais"])
logger = get_logger(__name__)

CACHE_PREFIX = "nota:"
CACHE_TTL = 3600  # 1 hour


@router.post("/", response_model=NotaFiscal, status_code=201)
@limiter.limit("10/minute")
async def create_nota(
    nota: NotaFiscalCreate,
    background_tasks: BackgroundTasks
):
    """Create a new nota fiscal."""
    try:
        # Generate ID
        nota_id = f"nota_{uuid.uuid4().hex[:12]}"
        
        # Create nota object
        nota_obj = NotaFiscal(
            id=nota_id,
            **nota.model_dump()
        )
        
        # Save to Redis
        cache_key = f"{CACHE_PREFIX}{nota_id}"
        await redis_service.set(cache_key, nota_obj.model_dump(), expire=CACHE_TTL)
        
        # Add background task to sync with Tiny
        background_tasks.add_task(sync_nota_with_tiny, nota_id)
        
        logger.info("Nota fiscal created", nota_id=nota_id, numero=nota.numero)
        
        return nota_obj
        
    except Exception as e:
        logger.error("Error creating nota", error=str(e))
        raise HTTPException(status_code=500, detail="Error creating nota fiscal")


@router.get("/{nota_id}", response_model=NotaFiscal)
async def get_nota(nota_id: str):
    """Get a specific nota fiscal by ID."""
    cache_key = f"{CACHE_PREFIX}{nota_id}"
    
    # Try cache first
    cached = await redis_service.get(cache_key)
    if cached:
        return NotaFiscal(**cached)
    
    logger.warning("Nota not found", nota_id=nota_id)
    raise HTTPException(status_code=404, detail="Nota fiscal not found")


@router.get("/", response_model=PaginatedResponse)
async def list_notas(
    pagination: PaginationParams = Depends(),
    filters: NotaFiscalFilter = Depends(),
):
    """List notas fiscais with pagination and filters."""
    try:
        # Get all nota keys
        pattern = f"{CACHE_PREFIX}*"
        keys = await redis_service.scan_keys(pattern)
        
        if not keys:
            return PaginatedResponse.create([], 0, pagination.page, pagination.page_size)
        
        # Get all notas
        notas_data = await redis_service.mget(keys)
        notas = [NotaFiscal(**data) for data in notas_data.values()]
        
        # Apply filters
        filtered_notas = filter_notas(notas, filters)
        
        # Sort by date
        filtered_notas.sort(key=lambda x: x.data_emissao, reverse=True)
        
        # Paginate
        total = len(filtered_notas)
        start = pagination.offset
        end = start + pagination.page_size
        paginated = filtered_notas[start:end]
        
        return PaginatedResponse.create(
            [nota.model_dump() for nota in paginated],
            total,
            pagination.page,
            pagination.page_size
        )
        
    except Exception as e:
        logger.error("Error listing notas", error=str(e))
        raise HTTPException(status_code=500, detail="Error listing notas fiscais")


@router.patch("/{nota_id}", response_model=NotaFiscal)
async def update_nota(
    nota_id: str,
    update: NotaFiscalUpdate
):
    """Update a nota fiscal."""
    cache_key = f"{CACHE_PREFIX}{nota_id}"
    
    # Get existing nota
    cached = await redis_service.get(cache_key)
    if not cached:
        raise HTTPException(status_code=404, detail="Nota fiscal not found")
    
    # Update fields
    nota = NotaFiscal(**cached)
    update_data = update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(nota, field, value)
    
    # Update timestamp
    nota.updated_at = datetime.utcnow()
    
    # Save back to Redis
    await redis_service.set(cache_key, nota.model_dump(), expire=CACHE_TTL)
    
    logger.info("Nota fiscal updated", nota_id=nota_id, fields=list(update_data.keys()))
    
    return nota


@router.delete("/{nota_id}", response_model=BaseResponse)
async def delete_nota(nota_id: str):
    """Delete a nota fiscal."""
    cache_key = f"{CACHE_PREFIX}{nota_id}"
    
    # Check if exists
    if not await redis_service.exists(cache_key):
        raise HTTPException(status_code=404, detail="Nota fiscal not found")
    
    # Delete from Redis
    await redis_service.delete(cache_key)
    
    logger.info("Nota fiscal deleted", nota_id=nota_id)
    
    return BaseResponse(
        success=True,
        message="Nota fiscal deleted successfully",
        data={"nota_id": nota_id}
    )


@router.post("/sync", response_model=BaseResponse)
@limiter.limit("1/minute")
async def sync_notas_from_tiny(background_tasks: BackgroundTasks):
    """Trigger sync with Tiny ERP."""
    try:
        # Add background task
        task_id = f"sync_{uuid.uuid4().hex[:8]}"
        background_tasks.add_task(sync_all_notas_from_tiny, task_id)
        
        return BaseResponse(
            success=True,
            message="Sync started in background",
            data={"task_id": task_id}
        )
        
    except Exception as e:
        logger.error("Error starting sync", error=str(e))
        raise HTTPException(status_code=500, detail="Error starting sync")


# Helper functions
def filter_notas(notas: List[NotaFiscal], filters: NotaFiscalFilter) -> List[NotaFiscal]:
    """Apply filters to notas list."""
    filtered = notas
    
    if filters.data_inicio:
        filtered = [n for n in filtered if n.data_emissao >= filters.data_inicio]
    
    if filters.data_fim:
        filtered = [n for n in filtered if n.data_emissao <= filters.data_fim]
    
    if filters.cliente_nome:
        search = filters.cliente_nome.lower()
        filtered = [n for n in filtered if search in n.cliente_nome.lower()]
    
    if filters.cliente_cnpj:
        filtered = [n for n in filtered if n.cliente_cnpj == filters.cliente_cnpj]
    
    if filters.numero:
        filtered = [n for n in filtered if filters.numero in n.numero]
    
    if filters.status:
        filtered = [n for n in filtered if n.status == filters.status]
    
    if filters.valor_min:
        filtered = [n for n in filtered if n.valor_total >= filters.valor_min]
    
    if filters.valor_max:
        filtered = [n for n in filtered if n.valor_total <= filters.valor_max]
    
    return filtered


# Background tasks
async def sync_nota_with_tiny(nota_id: str):
    """Background task to sync nota with Tiny ERP."""
    logger.info("Starting sync with Tiny", nota_id=nota_id)
    # TODO: Implement Tiny API sync
    await asyncio.sleep(1)  # Simulate API call
    logger.info("Sync completed", nota_id=nota_id)


async def sync_all_notas_from_tiny(task_id: str):
    """Background task to sync all notas from Tiny ERP."""
    logger.info("Starting full sync from Tiny", task_id=task_id)
    # TODO: Implement Tiny API full sync
    await asyncio.sleep(5)  # Simulate API calls
    logger.info("Full sync completed", task_id=task_id)


import asyncio  # Add at top with other imports