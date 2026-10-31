# transaction_normalizer/core/metrics.py

from typing import List, Dict
from pydantic import BaseModel, Field
from .models import NormalizedTransaction, TransactionStatus

class TransactionMetrics(BaseModel):
    """Esquema de datos para almacenar los resultados de las métricas."""
    total_processed: int = 0
    total_valid: int = 0
    total_invalid: int = 0
    status_counts: Dict[str, int] = Field(default_factory=dict)
    totals_by_original_currency: Dict[str, float] = Field(default_factory=dict)
    grand_total_usd: float = 0.0

def generate_metrics(
    total_raw: int, 
    valid_txs: List[NormalizedTransaction], 
    invalid_count: int
) -> TransactionMetrics:
    """
    Calcula las métricas solicitadas a partir de las listas de transacciones procesadas.
    """
    metrics = TransactionMetrics(
        total_processed=total_raw,
        total_valid=len(valid_txs),
        total_invalid=invalid_count,
        status_counts={"SUCCESS": 0, "FAILED": 0, "PENDING": 0, "NULL": 0}
    )

    for tx in valid_txs:
        # Conteo por estado
        if tx.status:
            status_key = tx.status.value if isinstance(tx.status, TransactionStatus) else tx.status
            metrics.status_counts[status_key] = metrics.status_counts.get(status_key, 0) + 1
        else:
            metrics.status_counts["NULL"] += 1

        # Totales por moneda original
        currency = tx.original_currency
        current_currency_total = metrics.totals_by_original_currency.get(currency, 0.0)
        metrics.totals_by_original_currency[currency] = current_currency_total + tx.original_amount

        # Total general normalizado en USD
        metrics.grand_total_usd += tx.amount

    # Redondear totales para evitar problemas de precisión de punto flotante
    for currency, total in metrics.totals_by_original_currency.items():
        metrics.totals_by_original_currency[currency] = round(total, 2)
    
    metrics.grand_total_usd = round(metrics.grand_total_usd, 2)

    return metrics