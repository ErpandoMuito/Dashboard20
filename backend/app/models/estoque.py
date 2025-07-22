from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class EntradaEstoqueRequest(BaseModel):
    codigo_produto: str = Field(..., description="Código do produto (ex: PH-510)")
    quantidade: int = Field(..., gt=0, description="Quantidade a adicionar")
    descricao: Optional[str] = Field(None, description="Descrição/observações")
    data: datetime = Field(default_factory=datetime.now, description="Data da entrada")
    deposito: str = Field(default="Geral", description="Nome do depósito")
    tipo: str = Field(default="E", description="E=Entrada, S=Saída")
    
    class Config:
        json_schema_extra = {
            "example": {
                "codigo_produto": "PH-510",
                "quantidade": 100,
                "descricao": "Entrada de produção",
                "data": "2025-07-21T10:00:00",
                "deposito": "Fundição"
            }
        }

class EntradaEstoqueResponse(BaseModel):
    success: bool
    message: str
    produto_id: Optional[str] = None
    saldo_atual: Optional[int] = None
    tiny_response: Optional[dict] = None
    
class ProdutoInfo(BaseModel):
    id: str
    codigo: str
    nome: str
    unidade: str
    saldo: int