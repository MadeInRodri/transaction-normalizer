# Sistema de normalización de transacciones

Proyecto educativo de un bootcamp de desarrollo con inteligencia artificial. La aplicación recibe transacciones JSON de distintos formatos, valida sus datos, las transforma a un esquema común y permite consultar resultados y métricas desde una CLI.

El proyecto sirve también como ejercicio de desarrollo asistido por IA: formular requisitos, dividir un problema, revisar propuestas de código y comprobar el resultado con datos de prueba. La IA puede apoyar el proceso, pero las decisiones, la revisión y la validación final corresponden al equipo de desarrollo.

## Objetivos de aprendizaje

- Separar reglas de negocio, interacción con archivos y presentación.
- Normalizar datos que llegan con estructuras distintas.
- Validar entradas y comunicar por qué se descartan.
- Usar Pydantic para modelar y validar datos.
- Construir una CLI interactiva con InquirerPy y Rich.
- Practicar un flujo responsable de desarrollo con IA: especificar, inspeccionar, probar e iterar.

## Requisitos

- Python 3.x. El proyecto se ejecutó en el entorno de desarrollo con Python 3.15.
- Dependencias listadas en [`requirements.txt`](requirements.txt):
  - `pydantic` (versión 2 o superior)
  - `python-dateutil`
  - `InquirerPy`
  - `rich`

## Instalación y ejecución

Desde la raíz del proyecto, en PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Después de instalar las dependencias, también puedes iniciar la CLI directamente con el intérprete del entorno virtual, sin activarlo:

```powershell
.\.venv\Scripts\python.exe main.py
```

Si el comando `py` no está disponible, crea el entorno con `python -m venv .venv`. En macOS o Linux, activa el entorno con `source .venv/bin/activate`.

Al iniciar, la CLI presenta un menú para:

1. Cargar y procesar un archivo JSON.
2. Ver transacciones válidas.
3. Ver transacciones inválidas y sus motivos.
4. Consultar métricas.
5. Exportar las transacciones inválidas.
6. Salir.

Al elegir la opción 1, introduce una ruta relativa desde la raíz, por ejemplo `data/valid_transactions.json` o `data/mixed_transactions.json`. Para la opción 5, la ruta predeterminada es `data/invalid_transactions.json`; la exportación se realiza cuando se solicita desde el menú y existen errores.

## Requerimientos funcionales

- Leer un archivo JSON cuyo contenido sea una lista de transacciones.
- Reconocer tres formatos de origen:

  | Formato | Identificador | Fecha | Monto | Estado |
  | --- | --- | --- | --- | --- |
  | A | `id` | `timestamp` | `amount` y `currency` | `status` |
  | B | `transaction_id` | `created_at` | `total` en centavos y `currency_code` | `state` |
  | C | `ref` | `date` | `amount` con símbolo de moneda | `result` |

- Normalizar los registros aceptados a un modelo común con ID, monto en USD, monto y moneda originales, fecha, estado y fuente.
- Estandarizar los estados reconocidos:
  - `completed`, `ok`, `success` → `SUCCESS`
  - `failed`, `fail` → `FAILED`
  - `waiting`, `wait`, `pending` → `PENDING`
  - Estado ausente o desconocido → sin estado (`NULL` en la interfaz)
- Descartar registros con identificador faltante, monto no procesable o negativo, fecha faltante, ilegible o futura.
- Continuar procesando el lote aunque haya registros inválidos y conservar el motivo de descarte.
- Mostrar transacciones, errores y métricas en la CLI.
- Permitir exportar las transacciones inválidas a otro archivo JSON.

## Normalización de montos

- La moneda normalizada es USD.
- En el formato B, el campo `total` se interpreta en centavos: `15000` se transforma en `150.00`.
- En el formato C, se eliminan los símbolos `€` y `$`; la coma se trata como separador decimal. La moneda se infiere del símbolo.
- Las tasas están definidas localmente en `core/normalizer.py`: EUR = 1.10 USD y USD = 1.00 USD.
- Para una moneda sin tasa definida, el código actual usa una tasa de 1.00. No consulta un servicio de cambio externo.

## Casos de uso con los archivos de prueba

Los archivos de [`data/`](data/) contienen 15 registros cada uno y se pueden cargar desde la opción 1 del menú.

### `data/valid_transactions.json`

Incluye cinco registros de cada formato (A, B y C), con datos válidos.

Resultado observado al procesarlo:

- 15 transacciones procesadas.
- 15 válidas y 0 inválidas.
- Las métricas agrupan estados reconocidos y calculan el total normalizado en USD.

Este caso permite comprobar la detección de formatos, la conversión de centavos, el reconocimiento de monedas y el renderizado de la tabla de resultados.

### `data/mixed_transactions.json`

Intercala registros válidos con casos diseñados para activar validaciones, entre ellos montos negativos, identificadores o montos ausentes, fechas futuras y fechas ilegibles. También incluye estados desconocidos o ausentes.

Resultado observado al procesarlo:

- 15 transacciones procesadas.
- 8 válidas y 7 inválidas.
- Las métricas incluyen dos transacciones válidas sin estado reconocido.
- La vista de inválidas muestra el motivo asociado a cada registro.

Este caso permite comprobar que los registros inválidos no detienen el lote y que los registros con estado desconocido o ausente no se descartan por ese motivo.

Los resultados anteriores se verificaron con los archivos de prueba disponibles en el proyecto; no representan una suite automatizada de pruebas.

## Arquitectura: enfoque hexagonal

El proyecto está organizado por responsabilidades y sigue una separación inspirada en arquitectura hexagonal (puertos y adaptadores):

```text
main.py
  └── interfaces/cli/       Adaptador de entrada: menú, flujo y presentación
        ├── app.py
        └── views.py
              │
              ▼
        core/                Reglas y modelo de negocio
        ├── models.py
        ├── validators.py
        ├── normalizer.py
        ├── processor.py
        └── metrics.py
              ▲
              │
        infrastructure/      Adaptador de salida: lectura y escritura JSON
        └── file_reader.py

data/                        Archivos JSON de prueba y de entrada/salida
```

- **Dominio y aplicación (`core/`)**: define el modelo de transacción, valida registros, normaliza valores, procesa lotes y calcula métricas.
- **Adaptador de entrada (`interfaces/cli/`)**: recoge las decisiones del usuario, invoca el procesamiento y presenta resultados con Rich.
- **Adaptador de salida (`infrastructure/`)**: encapsula la carga y exportación de archivos JSON.
- **Punto de composición (`main.py`)**: inicia la CLI.

En el estado actual, las dependencias entre componentes se expresan mediante imports y funciones Python; todavía no hay interfaces de puerto explícitas (por ejemplo, `Protocol` o clases abstractas). Por ello, es más preciso describirlo como una arquitectura por capas inspirada en hexagonal que como una implementación estricta de puertos y adaptadores. La organización permite, como evolución didáctica, sustituir la CLI o el almacenamiento JSON sin trasladar las reglas de negocio a esas capas.

## Estructura del proyecto

```text
.
├── core/
│   ├── metrics.py
│   ├── models.py
│   ├── normalizer.py
│   ├── processor.py
│   └── validators.py
├── data/
│   ├── mixed_transactions.json
│   └── valid_transactions.json
├── docs/
│   ├── requirements.md
│   └── test-results.md
├── infrastructure/
│   └── file_reader.py
├── interfaces/
│   └── cli/
│       ├── app.py
│       └── views.py
├── main.py
├── README.md
└── requirements.txt
```

## Alcance actual y posibles mejoras

- La exportación de inválidas es una acción manual del menú; no se ejecuta automáticamente al terminar de procesar un archivo.
- Los errores se conservan en memoria durante la sesión y se exportan como JSON cuando el usuario elige la opción correspondiente.
- Las tasas de conversión son simuladas y locales.
- La carpeta `docs/` contiene la especificación y los resultados esperados de los casos de prueba.
- Los JSON de `data/` son fixtures para validación manual. Actualmente no hay una suite de pruebas automatizadas configurada.
- La estructura `interfaces/web/` puede alojar una futura interfaz web sin mezclarla con la CLI ni con las reglas de negocio.

## Archivos de referencia

- [Especificación técnica](docs/requirements.md)
- [Resultados esperados de las pruebas](docs/test-results.md)
