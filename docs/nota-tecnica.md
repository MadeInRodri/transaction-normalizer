# Nota técnica

## Decisiones de diseño

Para este programa decidí utilizar una arquitectura basada en el concepto de "Clean Architecture" y la "Arquitectura Hexagonal" para que el proyecto fuera no sólo independiente de la interfaz que lo va a consumir, la CLI en este caso, sino también que este sea escalable por si se quisiera adaptar a un entorno web o de escritorio en un futuro.

## Uso de IA

Sobre el uso de IA, este proyecto fue hecho pensando en el AI-First, por lo que la IA eligió la distribución de archivos, funciones a implementar y restricciones impuestas por mí.

Antes de empezar a desarrollar me hice las siguientes preguntas sobre los requerimientos:

1. **Sobre el esquema de datos y monedas:**
   - ¿Existe una moneda base oficial para los montos?
   - Si entra una transacción en Euros (€99,99), ¿se debe convertir el valor matemático a USD usando una tasa de cambio fija/dinámica, o solo se estandariza el código de moneda y se mantiene el valor nominal?
   - Para los montos expresados en centavos (ej. 10050), ¿se asume siempre que los dos últimos dígitos son decimales al normalizarlos a float (es decir, 100.50)?

2. **Sobre las reglas de normalización:**
   - El estado objetivo solo permite SUCCESS, FAILED, PENDING.
   - ¿Qué otros estados de origen existen además de completed, OK y success que debamos mapear?
   - ¿Cómo determinamos exactamente la fuente (source) de la transacción?
   - ¿Se infiere por la estructura del objeto (ej. si tiene ref es Fuente A, si tiene transaction_id es Fuente B) o vendrá definido por el nombre del archivo?

3. **Sobre los criterios de validez e incompletitud:**
   - ¿Qué hace que una transacción sea catalogada como inválida? (¿Falta de ID, formato de fecha irreconocible, monto negativo o nulo?).
   - ¿Qué se debe hacer con los registros descartados?
   - ¿Se exportan a un archivo dead_letters.json, o simplemente se mantienen en memoria para mostrarlos en una tabla de la CLI bajo la opción de "Ver errores"?

Las respuestas a estas preguntas fueron respondidas a profundidad en [requirements.md](requirements.md).

## Lo que aprendí

Desarrollando este proyecto aprendí sobre el ciclo de desarrollo enfocado en AI-First, siendo mi rol el de un orquestador el cual decide el esquema de los datos, las reglas y requerimientos del sistema como en la normalización y los criterios de validez o descarte, delegando las tareas que podrían tardar más tiempo como la lógica dentro de las funciones o el proceso de solución de errores y conflictos de librerías para poder enfocarme mucho más en el flujo final de la aplicación y cumplir los requisitos presentados.
