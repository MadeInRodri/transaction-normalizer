# transaction_normalizer/interfaces/cli/views.py

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from typing import List, Dict, Any
from ...core.models import NormalizedTransaction
from ...core.metrics import TransactionMetrics

# Inicializamos la consola para renderizar los elementos
console = Console()

def show_header():
    """Muestra el título principal de la aplicación."""
    title = Text("=== SISTEMA DE NORMALIZACIÓN DE TRANSACCIONES ===", style="bold cyan", justify="center")
    console.print(Panel(title, border_style="cyan"))
    console.print()

def show_success(message: str):
    """Muestra un mensaje de éxito."""
    console.print(f"[bold green]✔ {message}[/bold green]")

def show_error(message: str):
    """Muestra un mensaje de error."""
    console.print(f"[bold red]✖ {message}[/bold red]")

def show_metrics_panel(metrics: TransactionMetrics):
    """Renderiza las métricas en un panel estilizado."""
    if metrics.total_processed == 0:
        show_error("No hay métricas disponibles. Por favor, procesa un archivo primero.")
        return

    # Tabla resumen principal
    table = Table(show_header=False, box=None)
    table.add_column("Métrica", style="bold cyan")
    table.add_column("Valor", style="bold white")
    
    table.add_row("Total Procesadas", str(metrics.total_processed))
    table.add_row("Transacciones Válidas", f"[green]{metrics.total_valid}[/green]")
    table.add_row("Transacciones Inválidas", f"[red]{metrics.total_invalid}[/red]")
    table.add_row("Total General (USD)", f"[bold green]${metrics.grand_total_usd:,.2f}[/bold green]")

    # Detalles por moneda
    currency_text = "\n[bold purple]Totales por Moneda Original:[/bold purple]\n"
    for curr, total in metrics.totals_by_original_currency.items():
        currency_text += f" • {curr}: {total:,.2f}\n"

    # Detalles por estado
    status_text = "\n[bold purple]Conteo por Estado:[/bold purple]\n"
    for status, count in metrics.status_counts.items():
        color = "green" if status == "SUCCESS" else "red" if status == "FAILED" else "yellow"
        status_text += f" • {status}: [{color}]{count}[/{color}]\n"

    content = table
    console.print(Panel.fit(content, title="[bold]Resumen de Métricas[/bold]", border_style="cyan"))
    console.print(currency_text)
    console.print(status_text)

def show_valid_transactions_table(transactions: List[NormalizedTransaction]):
    """Dibuja una tabla con las transacciones procesadas correctamente."""
    if not transactions:
        show_error("No hay transacciones válidas para mostrar.")
        return

    table = Table(title="Transacciones Normalizadas", border_style="green", header_style="bold green")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Monto (USD)", justify="right", style="bold white")
    table.add_column("Monto Orig.", justify="right")
    table.add_column("Moneda")
    table.add_column("Fecha (UTC)", style="magenta")
    table.add_column("Estado")
    table.add_column("Fuente", style="dim")

    for tx in transactions:
        status_color = "green" if tx.status == "SUCCESS" else "red" if tx.status == "FAILED" else "yellow"
        status_str = f"[{status_color}]{tx.status}[/{status_color}]" if tx.status else "[dim]NULL[/dim]"
        
        table.add_row(
            tx.id,
            f"${tx.amount:,.2f}",
            f"{tx.original_amount:,.2f}",
            tx.original_currency,
            tx.timestamp.strftime("%Y-%m-%d %H:%M"),
            status_str,
            tx.source
        )
    
    console.print(table)

def show_invalid_transactions_table(invalid_txs: List[Dict[str, Any]]):
    """Dibuja una tabla mostrando los registros fallidos y su motivo."""
    if not invalid_txs:
        show_success("¡Excelente! No hay transacciones inválidas.")
        return

    table = Table(title="Transacciones Descartadas", border_style="red", header_style="bold red")
    table.add_column("ID Crudo / Ref", style="cyan")
    table.add_column("Monto Crudo", justify="right")
    table.add_column("Motivo de Error", style="bold yellow")

    for tx in invalid_txs:
        raw_id = str(tx.get("id") or tx.get("transaction_id") or tx.get("ref") or "N/A")
        raw_amount = str(tx.get("amount") or tx.get("total") or "N/A")
        error = tx.get("_error_reason", "Error desconocido")
        
        table.add_row(raw_id, raw_amount, error)
        
    console.print(table)