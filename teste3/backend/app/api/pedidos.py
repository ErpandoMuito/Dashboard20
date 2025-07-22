from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime
import PyPDF2
import io
import re
from ..core.redis_client import redis_manager
from ..core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload")
async def upload_pedido(
    file: UploadFile = File(...),
    cliente: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """Upload e processamento de pedido PDF"""
    try:
        # Valida tamanho
        contents = await file.read()
        if len(contents) > settings.max_upload_size:
            raise HTTPException(
                status_code=413,
                detail=f"Arquivo muito grande. Máximo: {settings.max_upload_size / 1024 / 1024}MB"
            )
        
        # Valida tipo
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Apenas arquivos PDF são aceitos"
            )
        
        # Processa PDF
        pdf_data = io.BytesIO(contents)
        pdf_reader = PyPDF2.PdfReader(pdf_data)
        
        # Extrai texto
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        # Parse básico (adaptar conforme formato do cliente)
        pedido_info = _parse_pedido_pdf(text, cliente)
        
        # Gera ID único
        pedido_id = f"ped_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        pedido_info["id"] = pedido_id
        pedido_info["upload_date"] = datetime.now().isoformat()
        pedido_info["filename"] = file.filename
        
        # Salva no Redis
        key = f"pedido:{pedido_id}"
        await redis_manager.set(key, pedido_info, ex=2592000)  # 30 dias
        
        # Indexa por cliente
        if cliente:
            cliente_key = f"pedidos:cliente:{cliente}"
            pedidos_cliente = await redis_manager.get(cliente_key) or []
            pedidos_cliente.append(pedido_id)
            await redis_manager.set(cliente_key, pedidos_cliente)
        
        logger.info(f"Pedido {pedido_id} processado com sucesso")
        
        return {
            "status": "success",
            "message": "Pedido processado com sucesso",
            "pedido_id": pedido_id,
            "dados": pedido_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar PDF: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar arquivo PDF")

def _parse_pedido_pdf(text: str, cliente: Optional[str]) -> Dict[str, Any]:
    """Parser genérico para PDFs de pedido"""
    pedido = {
        "cliente": cliente or "Desconhecido",
        "itens": [],
        "data_pedido": None,
        "numero": None
    }
    
    # Patterns comuns (adaptar por cliente)
    patterns = {
        "numero": [
            r"Pedido\s*[:＃]?\s*(\d+)",
            r"Order\s*[:＃]?\s*(\d+)",
            r"PO\s*[:＃]?\s*(\d+)"
        ],
        "data": [
            r"(\d{2}/\d{2}/\d{4})",
            r"(\d{4}-\d{2}-\d{2})"
        ],
        "item": [
            r"(\d+)\s+(.+?)\s+(\d+)\s+(\d{2}/\d{2}/\d{4})",  # Código Descrição Qtd Data
            r"(.+?)\s+Qtd:\s*(\d+)\s+Entrega:\s*(\d{2}/\d{2}/\d{4})"  # Descrição Qtd Data
        ]
    }
    
    # Busca número do pedido
    for pattern in patterns["numero"]:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            pedido["numero"] = match.group(1)
            break
    
    # Busca data
    for pattern in patterns["data"]:
        match = re.search(pattern, text)
        if match:
            pedido["data_pedido"] = match.group(1)
            break
    
    # Busca itens (exemplo básico)
    lines = text.split('\n')
    for line in lines:
        # Tenta extrair código de produto e quantidade
        match = re.search(r'(\d{6,})\s+.*?(\d+)\s*(?:pç|pc|un)', line, re.IGNORECASE)
        if match:
            pedido["itens"].append({
                "codigo": match.group(1),
                "quantidade": int(match.group(2)),
                "linha": line.strip()
            })
    
    return pedido

@router.get("/")
async def listar_pedidos(
    cliente: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """Lista pedidos cadastrados"""
    try:
        if cliente:
            # Busca pedidos do cliente
            pedidos_ids = await redis_manager.get(f"pedidos:cliente:{cliente}") or []
            pattern = None
        else:
            # Lista todos
            pattern = "pedido:*"
            keys = await redis_manager.scan_keys(pattern, count=limit)
            pedidos_ids = [k.replace("pedido:", "") for k in keys]
        
        # Busca dados
        pedidos = []
        for pedido_id in pedidos_ids[:limit]:
            pedido = await redis_manager.get(f"pedido:{pedido_id}")
            if pedido:
                pedidos.append(pedido)
        
        return {
            "status": "success",
            "total": len(pedidos),
            "pedidos": pedidos
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar pedidos: {e}")
        raise HTTPException(status_code=500, detail="Erro ao listar pedidos")

@router.get("/{pedido_id}")
async def obter_pedido(pedido_id: str) -> Dict[str, Any]:
    """Obtém detalhes de um pedido"""
    try:
        pedido = await redis_manager.get(f"pedido:{pedido_id}")
        
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido não encontrado")
        
        return {
            "status": "success",
            "data": pedido
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter pedido {pedido_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar pedido")