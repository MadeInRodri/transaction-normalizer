# transaction_normalizer/core/models.py

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class TransactionStatus(str, Enum):
    """Enumeración de los estados permitidos para una transacción normalizada."""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"

class NormalizedTransaction(BaseModel):
    """
    Modelo de datos principal que representa una transacción completamente normalizada.
    Pydantic maneja la conversión de tipos y la validación automáticamente.
    """
    id: str = Field(..., description="Identificador único de la transacción")
    
    # Montos
    amount: float = Field(..., ge=0.0, description="Monto normalizado en USD")
    original_amount: float = Field(..., description="Monto en su moneda original")
    
    # Monedas
    currency: str = Field(default="USD", description="Código de la moneda base (Siempre USD)")
    original_currency: str = Field(..., description="Código de la moneda original (ej. EUR, USD)")
    
    # Temporal y Estado
    timestamp: datetime = Field(..., description="Marca de tiempo en formato ISO-8601")
    status: Optional[TransactionStatus] = Field(None, description="Estado mapeado. None si no está presente.")
    
    # Trazabilidad
    source: str = Field(..., description="Identificador del formato de origen (ej. Format_A, Format_B)")

    # Configuración de Pydantic V2 para serializar enums por su valor de texto nativamente
    model_config = ConfigDict(use_enum_values=True)