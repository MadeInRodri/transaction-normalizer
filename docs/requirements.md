# Decisiones de Diseño y Especificación Técnica
**Proyecto:** Sistema de Normalización de Transacciones

## 1. Stack Tecnológico Elegido
*   **Lenguaje:** Python 3.x
*   **Validación y Modelado:** `Pydantic` (Garantiza tipado estricto y facilita la integración futura con APIs).
*   **CLI e Interfaz de Usuario:** `InquirerPy` (Menús interactivos) y `Rich` (Renderizado de tablas y formateo en consola).
*   **Manejo de Fechas:** `python-dateutil` (Parsing flexible de múltiples formatos de fecha).

## 2. Modelo de Datos Final
Para cumplir con el requerimiento de mantener el monto original y normalizar a una moneda base, el esquema unificado (Pydantic) tendrá la siguiente estructura:

*   `id` (str): Identificador único de la transacción.
*   `amount` (float): Monto convertido a dólares (USD).
*   `original_amount` (float/str): Monto exacto tal como vino en la fuente.
*   `original_currency` (str): Moneda original (ej. USD, EUR).
*   `timestamp` (str): Fecha y hora en formato ISO-8601.
*   `status` (str | None): Estado normalizado (`SUCCESS`, `FAILED`, `PENDING`). Permitirá `null` (None) si no viene especificado.
*   `source` (str): Nombre o identificador de la fuente origen.

## 3. Reglas de Normalización

### Detección de Fuente
La fuente de los datos se inferirá analizando la clave primaria (el campo del ID) del objeto JSON entrante:
*   **Fuente A:** Se detecta si existe la clave `"id"`.
*   **Fuente B:** Se detecta si existe la clave `"transaction_id"`.
*   **Fuente C:** Se detecta si existe la clave `"ref"`.

### Normalización de Montos y Moneda
*   **Moneda Base:** USD (Dólares estadounidenses).
*   **Conversión:** Toda transacción que no esté en USD deberá ser convertida a USD para el campo `amount`.
*   **Formato de Centavos:** Si un monto es un número entero (ej. `10050` en Fuente B), se asumirá que los dos últimos dígitos representan los decimales (resultado: `100.50`).
*   **Símbolos:** Se limpiarán los caracteres de moneda (como `€`) antes de procesar numéricamente.

### Mapeo de Estados
Todos los estados se estandarizarán a tres valores posibles:
*   `SUCCESS`: Mapea desde `completed`, `OK`, `success`.
*   `FAILED`: Mapea desde `failed`, `FAIL`.
*   `PENDING`: Mapea desde `waiting`, `WAIT`, `pending`.
*   *Nota:* Si el estado no está presente, se asignará como `null` y se mantendrá en el listado de transacciones válidas (a menos que incumpla otras reglas).

## 4. Criterios de Validación y Descarte (Reglas de Negocio)
Una transacción se considerará **inválida** y será descartada si cumple *al menos una* de las siguientes condiciones:
1.  **ID Faltante:** No tiene el campo de identificación correspondiente a su fuente (`id`, `transaction_id`, o `ref`).
2.  **Monto Inválido:** El monto no puede ser procesado numéricamente, es nulo, o es un valor inconsistente.
3.  **Fecha Inválida:** El formato de fecha es irreconocible por `dateutil` o la fecha representa un momento en el futuro (mayor al año y fecha de ejecución).

### Manejo de Errores (Dead Letters)
*   Las transacciones que caigan en los criterios de descarte no detendrán la ejecución.
*   Se guardarán en memoria para poder ser visualizadas en la CLI bajo una opción de "Ver Errores".
*   Al finalizar el procesamiento, se exportarán automáticamente a un archivo secundario (ej. `invalid_transactions.json`).