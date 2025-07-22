from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ItemNota(BaseModel):
    """Item de uma nota fiscal"""
    codigo: str
    descricao: str
    quantidade: float
    valor_unitario: float
    valor_total: float
    unidade: Optional[str] = None
    ncm: Optional[str] = None

class NotaFiscal(BaseModel):
    """Modelo de Nota Fiscal"""
    id: str
    numero: str
    serie: Optional[str] = None
    data_emissao: datetime
    data_saida: Optional[datetime] = None
    
    # Cliente
    cliente_nome: str
    cliente_cnpj: Optional[str] = None
    cliente_cpf: Optional[str] = None
    
    # Valores
    valor_produtos: float
    valor_total: float
    valor_frete: Optional[float] = 0
    valor_desconto: Optional[float] = 0
    
    # Itens
    itens: List[ItemNota]
    
    # Status
    situacao: int = Field(description="1=Autorizada, 2=Cancelada, etc")
    
    # Metadados
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }