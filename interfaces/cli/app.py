# transaction_normalizer/interfaces/cli/app.py

import time
import os
from InquirerPy import inquirer
from rich.progress import Progress, SpinnerColumn, TextColumn
from . import views
from ...infrastructure.file_reader import load_transactions_from_json, export_invalid_transactions
from ...core.processor import process_transaction_batch
from ...core.metrics import generate_metrics, TransactionMetrics

class CLIApp:
    def __init__(self):
        self.valid_txs = []
        self.invalid_txs = []
        self.metrics = TransactionMetrics()
        self.data_loaded = False

    def run(self):
        views.console.clear()
        views.show_header()
        
        while True:
            # Construcción del menú interactivo
            choice = inquirer.select(
                message="Selecciona una acción:",
                choices=[
                    "1. Cargar y procesar archivo JSON",
                    "2. Ver Transacciones Válidas",
                    "3. Ver Transacciones Inválidas",
                    "4. Ver Métricas",
                    "5. Exportar transacciones inválidas",
                    "6. Salir"
                ],
                default="1. Cargar y procesar archivo JSON",
            ).execute()

            # Enrutamiento de la opción seleccionada
            if choice.startswith("1"):
                self._handle_load_file()
            elif choice.startswith("2"):
                views.show_valid_transactions_table(self.valid_txs)
            elif choice.startswith("3"):
                views.show_invalid_transactions_table(self.invalid_txs)
            elif choice.startswith("4"):
                views.show_metrics_panel(self.metrics)
            elif choice.startswith("5"):
                self._handle_export_errors()
            elif choice.startswith("6"):
                views.console.print("[bold cyan]¡Hasta luego![/bold cyan]")
                break
            
            # Pausa para que el usuario pueda leer los resultados antes de limpiar
            if not choice.startswith("6"):
                input("\nPresiona Enter para continuar...")
                views.console.clear()
                views.show_header()

    def _handle_load_file(self):
        file_path = inquirer.text(
            message="Ruta del archivo JSON (ej. data/input.json):",
            default="data/input.json"
        ).execute()

        try:
            # Simulación de carga visual con Rich Progress
            with Progress(
                SpinnerColumn(spinner_name="dots", style="bold cyan"),
                TextColumn("[bold cyan]{task.description}"),
                transient=True,
            ) as progress:
                
                task = progress.add_task("Leyendo archivo...", total=100)
                raw_data = load_transactions_from_json(file_path)
                
                # Simular un ligero retardo para apreciar la UI si el archivo es muy rápido
                time.sleep(0.5) 
                
                progress.update(task, description="Normalizando transacciones...")
                self.valid_txs, self.invalid_txs = process_transaction_batch(raw_data)
                
                progress.update(task, description="Calculando métricas...")
                self.metrics = generate_metrics(len(raw_data), self.valid_txs, len(self.invalid_txs))
                time.sleep(0.3)
                
            self.data_loaded = True
            views.show_success(f"Archivo procesado exitosamente. {len(self.valid_txs)} válidas, {len(self.invalid_txs)} inválidas.")
            
        except Exception as e:
            views.show_error(f"Error al procesar el archivo: {str(e)}")

    def _handle_export_errors(self):
        if not self.data_loaded:
            views.show_error("Debes cargar datos primero.")
            return
            
        if not self.invalid_txs:
            views.show_success("No hay errores para exportar.")
            return

        out_path = inquirer.text(
            message="Ruta para guardar errores:",
            default="data/invalid_transactions.json"
        ).execute()

        try:
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            export_invalid_transactions(out_path, self.invalid_txs)
            views.show_success(f"Errores exportados a {out_path}")
        except Exception as e:
            views.show_error(f"No se pudo guardar el archivo: {str(e)}")