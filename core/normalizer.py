# transaction_normalizer/core/normalizer.py

from typing import Dict, Any, Tuple, Optional
from dateutil import parser
from .models import NormalizedTransaction, TransactionStatus

# Tasas de cambio simuladas (En un entorno real, esto consultaría una API externa o base de datos)
EXCHANGE_RATES = {
    "EUR": 1.10, # 1 EUR = 1.10 USD
    "USD": 1.00
}

# Diccionario unificado para mapear todos los estados posibles hacia nuestro enum estándar
STATUS_MAPPING = {
    # Formato A
    "completed": TransactionStatus.SUCCESS,
    "failed": TransactionStatus.FAILED,
    "waiting": TransactionStatus.PENDING,
    # Formato B
    "ok": TransactionStatus.SUCCESS,
    "fail": TransactionStatus.FAILED,
    "wait": TransactionStatus.PENDING,
    # Formato C
    "success": TransactionStatus.SUCCESS,
    "pending": TransactionStatus.PENDING,
}

def _detect_source(raw_tx: Dict[str, Any]) -> str:
    """Determina la fuente de la transacción basándose en la clave primaria."""
    if "id" in raw_tx:
        return "FORMAT_A"
    elif "transaction_id" in raw_tx:
        return "FORMAT_B"
    elif "ref" in raw_tx:
        return "FORMAT_C"
    
    return "UNKNOWN"

def _normalize_status(raw_status: Optional[str]) -> Optional[TransactionStatus]:
    """Convierte el estado original a nuestro TransactionStatus estandarizado."""
    if not raw_status:
        return None
    
    # Limpiamos el string (espacios y mayúsculas) para buscarlo en el mapeo
    clean_status = str(raw_status).strip().lower()
    return STATUS_MAPPING.get(clean_status, None)

def _extract_financials(raw_tx: Dict[str, Any], source: str) -> Tuple[float, str]:
    """
    Extrae el monto y la moneda original dependiendo del formato.
    Retorna una tupla: (monto_original, codigo_moneda_original)
    """
    if source == "FORMAT_A":
        # Monto normal en string, moneda explícita
        amount = float(raw_tx.get("amount", 0.0))
        currency = str(raw_tx.get("currency", "USD")).upper()
        return amount, currency
        
    elif source == "FORMAT_B":
        # Monto en centavos, moneda explícita
        cents = float(raw_tx.get("total", 0.0))
        amount = cents / 100.0
        currency = str(raw_tx.get("currency_code", "USD")).upper()
        return amount, currency
        
    elif source == "FORMAT_C":
        # Monto con símbolo y comas, sin campo explícito de moneda
        raw_amount = str(raw_tx.get("amount", "0"))
        
        # Detección de moneda por símbolo
        currency = "USD"
        if "€" in raw_amount:
            currency = "EUR"
        elif "$" in raw_amount:
            currency = "USD"
            
        # Limpieza de caracteres para conversión numérica
        clean_amount = raw_amount.replace("€", "").replace("$", "").replace(",", ".")
        return float(clean_amount), currency
        
    return 0.0, "USD"

def normalize_transaction(raw_tx: Dict[str, Any]) -> NormalizedTransaction:
    """
    Toma un diccionario crudo, determina su fuente, aplica las reglas de negocio
    y retorna un modelo NormalizedTransaction validado por Pydantic.
    """
    source = _detect_source(raw_tx)
    
    # Extracción de campos dependiendo de la fuente
    if source == "FORMAT_A":
        tx_id = str(raw_tx.get("id"))
        raw_date = raw_tx.get("timestamp")
        raw_status = raw_tx.get("status")
    elif source == "FORMAT_B":
        tx_id = str(raw_tx.get("transaction_id"))
        raw_date = raw_tx.get("created_at")
        raw_status = raw_tx.get("state")
    elif source == "FORMAT_C":
        tx_id = str(raw_tx.get("ref"))
        raw_date = raw_tx.get("date")
        raw_status = raw_tx.get("result")
    else:
        raise ValueError(f"Formato de transacción desconocido para normalización: {raw_tx}")

    # Procesar finanzas
    original_amount, original_currency = _extract_financials(raw_tx, source)
    
    # Conversión a dólares (USD)
    conversion_rate = EXCHANGE_RATES.get(original_currency, 1.0)
    usd_amount = round(original_amount * conversion_rate, 2)
    
    # Parseo de fecha flexible utilizando dateutil
    parsed_timestamp = parser.parse(str(raw_date))
    
    # Construcción y validación automática del modelo Pydantic
    return NormalizedTransaction(
        id=tx_id,
        amount=usd_amount,
        original_amount=original_amount,
        currency="USD",
        original_currency=original_currency,
        timestamp=parsed_timestamp,
        status=_normalize_status(raw_status),
        source=source
    )