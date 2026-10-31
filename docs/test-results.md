# Casos de Prueba del Sistema de Normalización

Este documento describe el comportamiento esperado al procesar los archivos de prueba en la CLI interactiva.

## 1. Prueba con `valid_transactions.json`

Este archivo contiene 15 registros perfectos, divididos equitativamente entre los 3 formatos de origen.

**Comportamiento esperado en la CLI:**

- **Procesamiento (Opción 1):** La barra de carga avanzará y mostrará un mensaje verde indicando: `15 válidas, 0 inválidas`.
- **Transacciones Válidas (Opción 2):** Se mostrará una tabla con 15 filas. Verás que los montos en centavos del Formato B (ej. `15000`) se habrán convertido a decimales (`150.00`), los símbolos del Formato C (`€99,99`) habrán desaparecido y se habrán transformado en `99.99` de tipo numérico, y la moneda `EUR` habrá sido detectada.
- **Métricas (Opción 4):**
  - Total procesadas: 15
  - Transacciones Inválidas: 0
  - Se observará un conteo claro en los estados agrupados como `SUCCESS`, `PENDING` y `FAILED`.
- **Exportar (Opción 5):** El sistema debe impedir la exportación y mostrar un mensaje verde indicando que no hay errores para exportar.

## 2. Prueba con `mixed_transactions.json`

Este archivo contiene 15 registros intercalados: 8 transacciones válidas y 7 transacciones con datos corruptos diseñados para detonar las reglas de `validators.py`.

**Comportamiento esperado en la CLI:**

- **Procesamiento (Opción 1):** El sistema mostrará: `8 válidas, 7 inválidas`.
- **Transacciones Inválidas (Opción 3):** Al abrir la tabla de errores, deberás ver exactamente 7 filas detallando los motivos de descarte:
  1.  `tx_err_01`: "El monto no puede ser negativo".
  2.  `A-06`: "Falta el campo de fecha".
  3.  `N/A`: "Falta el identificador de la transacción" (El registro que no tiene `id`, `transaction_id` ni `ref`).
  4.  `tx_err_04`: "Monto numérico no analizable: cien dolares".
  5.  `A-08`: "La fecha de la transacción no puede estar en el futuro" (Tiene fecha del 2028).
  6.  `209`: "Falta el campo del monto".
  7.  `tx_err_07`: "Formato de fecha inválido: ayer por la tarde".
- **Validaciones Flexibles (Opción 2):** En la tabla de válidas notarás que los registros `tx_009` y `A-10` aparecen con estado `NULL` (en gris). Esto es porque uno tenía un estado que no existía en el diccionario de mapeo (`estado_desconocido`) y el otro simplemente omitió el campo de resultado, demostrando que el sistema normaliza estados faltantes sin descartar la información financiera.
- **Exportar (Opción 5):** Solicitará una ruta y generará un JSON exclusivamente con los 7 registros descartados, inyectando la llave `_error_reason` en cada uno.
