from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class DesgloseIVALinea(BaseModel):
    base: Decimal
    tipo_iva: Decimal
    cuota: Decimal


class Factura(BaseModel):
    es_factura: bool
    proveedor: Optional[str] = None
    nif_proveedor: Optional[str] = None
    numero: Optional[str] = None
    fecha: Optional[str] = None
    desglose_iva: List[DesgloseIVALinea] = Field(default_factory=list)
    retencion_irpf: Decimal = Decimal("0")
    total: Optional[Decimal] = None
    moneda: str = "EUR"


class ProductoPedido(BaseModel):
    nombre: str
    cantidad: str


class Pedido(BaseModel):
    es_pedido: bool
    cliente: Optional[str] = None
    productos: List[ProductoPedido] = Field(default_factory=list)
    fecha_entrega: Optional[str] = None
    direccion_entrega: Optional[str] = None
    observaciones: Optional[str] = None
