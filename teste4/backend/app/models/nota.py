"""
Nota Fiscal models with validation.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from .base import TimestampMixin


class NotaFiscalBase(BaseModel):
    """Base model for Nota Fiscal."""
    numero: str = Field(..., min_length=1, description="Número da nota fiscal")
    serie: str = Field(default="1", description="Série da nota fiscal")
    data_emissao: datetime = Field(..., description="Data de emissão")
    
    cliente_nome: str = Field(..., min_length=1, description="Nome do cliente")
    cliente_cnpj: Optional[str] = Field(None, regex=r"^\d{14}$", description="CNPJ do cliente")
    
    valor_total: Decimal = Field(..., gt=0, decimal_places=2, description="Valor total da nota")
    valor_produtos: Decimal = Field(..., ge=0, decimal_places=2, description="Valor dos produtos")
    valor_frete: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2, description="Valor do frete")
    valor_desconto: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2, description="Valor do desconto")
    
    @field_validator("valor_total")
    @classmethod
    def validate_valor_total(cls, v: Decimal, info) -> Decimal:
        """Validate that total value matches calculation."""
        if "valor_produtos" in info.data and "valor_frete" in info.data and "valor_desconto" in info.data:
            calculated = info.data["valor_produtos"] + info.data["valor_frete"] - info.data["valor_desconto"]
            if abs(v - calculated) > Decimal("0.01"):  # Allow 1 cent difference for rounding
                raise ValueError(f"Valor total ({v}) não corresponde ao cálculo ({calculated})")
        return v


class ItemNotaFiscal(BaseModel):
    """Item de uma nota fiscal."""
    codigo_produto: str = Field(..., min_length=1, description="Código do produto")
    descricao: str = Field(..., min_length=1, description="Descrição do produto")
    quantidade: Decimal = Field(..., gt=0, description="Quantidade")
    unidade: str = Field(default="UN", description="Unidade de medida")
    valor_unitario: Decimal = Field(..., gt=0, decimal_places=2, description="Valor unitário")
    valor_total: Decimal = Field(..., gt=0, decimal_places=2, description="Valor total do item")
    
    @field_validator("valor_total")
    @classmethod
    def validate_item_total(cls, v: Decimal, info) -> Decimal:
        """Validate item total calculation."""
        if "quantidade" in info.data and "valor_unitario" in info.data:
            calculated = info.data["quantidade"] * info.data["valor_unitario"]
            if abs(v - calculated) > Decimal("0.01"):
                raise ValueError(f"Valor total do item ({v}) não corresponde ao cálculo ({calculated})")
        return v


class NotaFiscalCreate(NotaFiscalBase):
    """Model for creating a Nota Fiscal."""
    itens: List[ItemNotaFiscal] = Field(..., min_length=1, description="Itens da nota fiscal")
    
    @field_validator("itens")
    @classmethod
    def validate_itens_total(cls, v: List[ItemNotaFiscal], info) -> List[ItemNotaFiscal]:
        """Validate that sum of items matches produtos value."""
        if v and "valor_produtos" in info.data:
            items_total = sum(item.valor_total for item in v)
            if abs(items_total - info.data["valor_produtos"]) > Decimal("0.01"):
                raise ValueError(f"Soma dos itens ({items_total}) não corresponde ao valor dos produtos ({info.data['valor_produtos']})")
        return v


class NotaFiscal(NotaFiscalBase, TimestampMixin):
    """Complete Nota Fiscal model."""
    id: str = Field(..., description="ID único da nota fiscal")
    status: str = Field(default="active", description="Status da nota fiscal")
    tiny_id: Optional[str] = Field(None, description="ID no Tiny ERP")
    itens: List[ItemNotaFiscal] = []
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "nota_12345",
                "numero": "001234",
                "serie": "1",
                "data_emissao": "2024-01-15T10:30:00",
                "cliente_nome": "Empresa ABC Ltda",
                "cliente_cnpj": "12345678000190",
                "valor_total": 1500.00,
                "valor_produtos": 1400.00,
                "valor_frete": 100.00,
                "valor_desconto": 0.00,
                "status": "active",
                "itens": [
                    {
                        "codigo_produto": "PROD001",
                        "descricao": "Produto Exemplo",
                        "quantidade": 10,
                        "unidade": "UN",
                        "valor_unitario": 140.00,
                        "valor_total": 1400.00
                    }
                ]
            }
        }
    }


class NotaFiscalUpdate(BaseModel):
    """Model for updating a Nota Fiscal."""
    status: Optional[str] = None
    valor_frete: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    valor_desconto: Optional[Decimal] = Field(None, ge=0, decimal_places=2)


class NotaFiscalFilter(BaseModel):
    """Filters for querying Notas Fiscais."""
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    cliente_nome: Optional[str] = None
    cliente_cnpj: Optional[str] = None
    numero: Optional[str] = None
    status: Optional[str] = None
    valor_min: Optional[Decimal] = None
    valor_max: Optional[Decimal] = None