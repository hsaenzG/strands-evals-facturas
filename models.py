"""Modelo de salida del agente: una factura electrónica de LATAM."""
import datetime

from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str = Field(description="Descripción del concepto, tal como aparece en la factura")
    quantity: int = Field(description="Cantidad de unidades")
    unit_price: float = Field(description="Precio unitario antes de impuestos, como número")


class Invoice(BaseModel):
    issuer_name: str = Field(description="Razón social de quien emite la factura")
    issuer_tax_id: str = Field(description="Identificación fiscal del emisor (RFC, RUC, RUT, NIT, CUIT, cédula jurídica)")
    invoice_uuid: str = Field(description="Folio fiscal, UUID, CUFE, serie-número o clave de acceso de la factura")
    issue_date: datetime.date = Field(description="Fecha de emisión de la factura")
    tax_amount: float = Field(description="Monto total del impuesto (IVA o IGV)")
    total: float = Field(description="Total a pagar, con impuestos")
    line_items: list[LineItem] = []
