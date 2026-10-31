# transaction_normalizer/core/validators.py

from datetime import datetime, timezone
from dateutil import parser
from typing import Any, Dict, Tuple, Optional

def _get_raw_id(raw_tx: Dict[str, Any]) -> Any:
    """Función auxiliar para extraer el ID sin importar el formato de origen."""
    return raw_tx.get("id") or raw_tx.get("transaction_id") or raw_tx.get("ref")

def _get_raw_amount(raw_tx: Dict[str, Any]) -> Any:
    """Función auxiliar para extraer el monto sin importar el formato de origen."""
    return raw_tx.get("amount") or raw_tx.get("total")

def _get_raw_date(raw_tx: Dict[str, Any]) -> Any:
    """Función auxiliar para extraer la fecha sin importar el formato de origen."""
    return raw_tx.get("timestamp") or raw_tx.get("created_at") or raw_tx.get("date")

def is_valid_raw_transaction(raw_tx: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Evalúa las reglas de negocio para determinar si una transacción cruda debe ser descartada.
    Retorna: (es_valida: bool, motivo_error: str)
    """
    # 1. Validar la presencia del ID
    if not _get_raw_id(raw_tx):
        return False, "Falta el identificador de la transacción (id, transaction_id o ref)"

    # 2. Validar la presencia y el formato del monto
    raw_amount = _get_raw_amount(raw_tx)
    if raw_amount is None:
        return False, "Falta el campo del monto"

    try:
        # Eliminar símbolos de moneda comunes y manejar decimales con coma europea si es una cadena de texto
        if isinstance(raw_amount, str):
            cleaned_amount = raw_amount.replace("€", "").replace("$", "").replace(",", ".")
            float_val = float(cleaned_amount)
        else:
            float_val = float(raw_amount)

        if float_val < 0:
            return False, "El monto no puede ser negativo"
    except ValueError:
        return False, f"Monto numérico no analizable: {raw_amount}"

    # 3. Validar la presencia de la fecha, su formato y que no sea futura
    raw_date = _get_raw_date(raw_tx)
    if not raw_date:
        return False, "Falta el campo de fecha"

    try:
        # Convertir la cadena de texto en un objeto datetime
        parsed_date = parser.parse(str(raw_date))
        
        # Hacer que la fecha analizada tenga zona horaria si no la tiene, asumiendo UTC como base para la comparación
        if parsed_date.tzinfo is None:
            parsed_date = parsed_date.replace(tzinfo=timezone.utc)
            
        current_time = datetime.now(timezone.utc)
        
        if parsed_date > current_time:
            return False, "La fecha de la transacción no puede estar en el futuro"
            
    except (ValueError, OverflowError):
        return False, f"Formato de fecha inválido: {raw_date}"

    # Si pasa todas las comprobaciones, es válida para ser enviada al normalizador
    return True, None