# transaction_normalizer/infrastructure/file_reader.py

import json
from typing import List, Dict, Any
from pathlib import Path

def load_transactions_from_json(file_path: str) -> List[Dict[str, Any]]:
    """Lee un archivo JSON y retorna una lista de transacciones crudas."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"El archivo no existe: {file_path}")
        
    with open(path, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
            if not isinstance(data, list):
                raise ValueError("El JSON debe contener una lista de transacciones.")
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Error al decodificar el archivo JSON: {e}")

def export_invalid_transactions(file_path: str, invalid_transactions: List[Dict[str, Any]]) -> None:
    """Exporta las transacciones descartadas a un archivo JSON para auditoría."""
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(invalid_transactions, file, indent=4, ensure_ascii=False)