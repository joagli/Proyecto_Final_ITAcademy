# 02 · Datos

Datasets de la entrega:

- `procesados/`: datos limpios que usa la app (CPNL, EULP y mapa).
- `fuentes_oficiales/`: tablas oficiales pequeñas (censos lingüísticos, ECEPOV-2021 y serie de la EULP), cada fila con su fuente.
- `diccionario_datos.md`: qué es una fila y qué significa cada columna de cada archivo.

Se regeneran con `python src/preparar_entrega.py` (desde la raíz del proyecto). Los originales descargados de las fuentes están en `datos/originales/` y no se copian aquí.
