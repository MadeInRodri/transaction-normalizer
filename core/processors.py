# transaction_normalizer/core/processor.py

from typing import List, Dict, Any, Tuple
from .validators import is_valid_raw_transaction
from .normalizer import normalize_transaction
from .models import NormalizedTransaction

def process_transaction_batch(
    raw_transactions: List[Dict[str, Any]]
) -> Tuple[List[NormalizedTransaction], List[Dict[str, Any]]]:
    """
    Procesa un lote de transacciones crudas, separando las válidas de las inválidas.
    Retorna una tupla: (lista_validas, lista_invalidas_con_motivo)
    """
    valid_transactions: List[NormalizedTransaction] = []
    invalid_transactions: List[Dict[str, Any]] = []

    for raw_tx in raw_transactions:
        # 1. Validar reglas de negocio
        is_valid, error_reason = is_valid_raw_transaction(raw_tx)
        
        if not is_valid:
            # Marcamos y separamos la transacción fallida
            raw_tx["_error_reason"] = error_reason
            invalid_transactions.append(raw_tx)
            continue
            
        # 2. Normalizar si es válida
        try:
            normalized_tx = normalize_transaction(raw_tx)
            valid_transactions.append(normalized_tx)
        except Exception as e:
            # Si ocurre un error inesperado durante la normalización, también se descarta
            raw_tx["_error_reason"] = f"Error de normalización: {str(e)}"
            invalid_transactions.append(raw_tx)

    return valid_transactions, invalid_transactions