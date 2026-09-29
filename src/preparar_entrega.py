"""
preparar_entrega.py
-------------------
Prepara la carpeta de datos de la entrega: copia datos/procesados/ y
datos/fuentes_oficiales/ a entregables/02_datos/ y genera diccionario_datos.md
con una ficha por archivo (qué es una fila, número de filas y columnas, y qué
significa cada columna).

Uso (desde la carpeta raíz del proyecto, después de preparar los datos):
    python src/preparar_entrega.py
"""

import json
import shutil
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
ORIGENES = {"procesados": RAIZ / "datos" / "procesados",
            "fuentes_oficiales": RAIZ / "datos" / "fuentes_oficiales"}
DESTINO = RAIZ / "entregables" / "02_datos"

# Qué es cada archivo y qué es una fila
ARCHIVOS = {
    "cpnl_municipios.csv": "Inscripciones a los cursos del CPNL. Una fila por municipio y año (2011–2023). "
                           "El código 000000 agrupa las inscripciones sin municipio catalán asignado.",
    "cpnl_cataluna_anual.csv": "Inscripciones del CPNL, total por año (incluye las que no tienen municipio catalán).",
    "cpnl_validacion.csv": "Controles de coherencia del CPNL: filas que no cuadran, por año.",
    "cpnl_cambios.csv": "Correcciones aplicadas al CPNL en la limpieza.",
    "cpnl_ambito.csv": "Inscripciones del CPNL por ámbito territorial, para cada año y para el total 2011–2023 "
                       "(sin el código 000000).",
    "eulp_lengua_segmento.csv": "EULP: lengua inicial, de identificación y habitual por sexo, edad y lugar de "
                                "nacimiento. Una fila por año, indicador, segmento y categoría de lengua.",
    "eulp_conocimiento_segmento.csv": "EULP: % que conoce el catalán (entender, hablar, leer, escribir) por sexo, "
                                      "edad y lugar de nacimiento. Una fila por año, segmento y habilidad.",
    "eulp_ambitos_segmento.csv": "EULP: lengua usada en cada ámbito de uso (hogar, amigos, comercio...). Una fila "
                                 "por año, ámbito, segmento y categoría de uso.",
    "eulp_territorio.csv": "EULP 2023 por ámbito territorial (Plan territorial general de Cataluña): lengua habitual, lengua inicial "
                           "y sabe hablar. Una fila por ámbito territorial.",
    "mapa_centroides.csv": "Punto interior de cada ámbito territorial, donde el mapa escribe la etiqueta.",
    "mapa_ambitos.geojson": "Geometría simplificada de los 8 ámbitos territoriales (lon/lat), a partir de los "
                            "municipios del ICGC.",
    "metadatos.json": "Origen y fecha de proceso de los datos del CPNL.",
    "censo_conocimiento.csv": "Conocimiento del catalán (censos lingüísticos 1986–2011 y ECEPOV-2021). Una fila por año.",
    "conocimiento_edad_2021.csv": "Conocimiento del catalán por grupo de edad en 2021 (ECEPOV-2021). Una fila por grupo.",
    "eulp_cataluna.csv": "EULP, serie de Cataluña 2003–2023: población, lengua inicial y habitual. Una fila por edición "
                         "(2003: dato enlazado, solo como referencia).",
}

# Qué significa cada columna (las mismas en todos los archivos, salvo las de CONTEXTO)
COLUMNAS = {
    "anio": "Año", "año": "Año (edición de la EULP)", "periodo": "Año o periodo acumulado (2011–2023)",
    "codigo_municipio": "Código INE del municipio (6 dígitos); 000000 = sin municipio catalán asignado",
    "municipio": "Nombre del municipio", "provincia": "Provincia (de los dos primeros dígitos del código)",
    "codigo_ambito": "Código del ámbito territorial (AT01–AT08, Idescat)",
    "total": "Inscripciones totales (no personas)",
    "nivel_inicial_basico1": "Inscripciones de nivel Inicial y Básico 1",
    "nivel_basico23_elemental": "Inscripciones de nivel Básico 2-3 y Elemental",
    "nivel_intermedio_suficiencia": "Inscripciones de nivel Intermedio y Suficiencia",
    "nacidos_cataluna": "Inscripciones de personas nacidas en Cataluña",
    "nacidos_resto_espana": "Inscripciones de personas nacidas en el resto de España",
    "nacidos_extranjero": "Inscripciones de personas nacidas en el extranjero (corregido desde 2022)",
    "sin_datos_origen": "Inscripciones sin dato de lugar de nacimiento",
    "origen_conocido": "Suma de los tres orígenes (base de los porcentajes por origen)",
    "ue": "Nacidos en la Unión Europea", "resto_europa": "Nacidos en el resto de Europa",
    "norte_africa": "Nacidos en el norte de África", "resto_africa": "Nacidos en el resto de África",
    "america_sur_central": "Nacidos en América del Sur y Central", "asia": "Nacidos en Asia",
    "resto_mundo": "Nacidos en el resto del mundo",
    "dif_niveles": "Control: total − suma de niveles (0 = cuadra)",
    "dif_origen": "Control: total − (origen conocido + sin datos) (0 = cuadra)",
    "dif_subregiones": "Control: nacidos en el extranjero − suma de regiones (0 = cuadra)",
    "filas": "Número de filas del año", "falla_niveles": "Filas con descuadre por nivel",
    "falla_origen": "Filas con descuadre por origen", "falla_subregiones": "Filas con descuadre por región",
    "tipo": "Tipo de corrección", "antes": "Código de municipio antes de la corrección",
    "despues": "Código de municipio después de la corrección",
    "pct_cataluna": "% nacidos en Cataluña sobre el origen conocido",
    "pct_resto_espana": "% nacidos en el resto de España sobre el origen conocido",
    "pct_extranjero": "% nacidos en el extranjero sobre el origen conocido",
    "indicador": "Lengua inicial, de identificación o habitual",
    "tipo_segmento": "Variable de corte: sexo, edad o lugar de nacimiento",
    "segmento": "Grupo dentro del corte ('total' = todos)", "orden_segmento": "Orden para los gráficos",
    "categoria": "Categoría de lengua o de uso (las menores se agrupan en 'Otras y no consta')",
    "orden_categoria": "Orden para los gráficos",
    "miles": "Miles de personas", "pct": "% sobre el total del grupo",
    "habilidad": "Entender, saber hablar, leer, escribir o las cuatro",
    "poblacion_15mas_miles": "Población de 15 años o más (miles)",
    "habitual_catalan_miles": "Catalán como lengua habitual (miles)",
    "habitual_catalan_pct": "Catalán como lengua habitual (%)",
    "inicial_catalan_miles": "Catalán como lengua inicial (miles)",
    "inicial_catalan_pct": "Catalán como lengua inicial (%)",
    "sabe_hablar_miles": "Sabe hablar catalán (miles)", "sabe_hablar_pct": "Sabe hablar catalán (%)",
    "lon": "Longitud (grados)", "lat": "Latitud (grados)",
    "poblacion_2mas": "Población de 2 años o más", "personas_sabe_hablar": "Personas que saben hablar catalán",
    "pct_entiende": "% que entiende el catalán", "pct_sabe_hablar": "% que sabe hablar catalán",
    "pct_sabe_leer": "% que sabe leer catalán", "pct_sabe_escribir": "% que sabe escribir catalán",
    "comparable_con_serie": "'si' si es comparable con la serie 1986–2011",
    "grupo_edad": "Grupo de edad", "poblacion_miles": "Población del grupo (miles)",
    "lengua_inicial_catalan_miles": "Catalán como lengua inicial (miles)",
    "lengua_inicial_catalan_pct": "Catalán como lengua inicial (%)",
    "lengua_habitual_catalan_pct": "Catalán como lengua habitual (%)",
    "lengua_habitual_castellano_pct": "Castellano como lengua habitual (%)",
    "fuente": "Fuente oficial de la fila",
}
# Columnas con el mismo nombre y distinto significado según el archivo
CONTEXTO = {
    ("eulp_ambitos_segmento.csv", "ambito"): "Ámbito de uso de la lengua (con los amigos, en el comercio...)",
    ("eulp_ambitos_segmento.csv", "total"): "Población de referencia del ámbito (miles)",
    ("eulp_lengua_segmento.csv", "total"): "Población del grupo (miles)",
    ("cpnl_ambito.csv", "ambito"): "Ámbito territorial del Plan territorial general de Cataluña",
    ("eulp_territorio.csv", "ambito"): "Ámbito territorial del Plan territorial general de Cataluña",
    ("mapa_centroides.csv", "ambito"): "Ámbito territorial del Plan territorial general de Cataluña",
    ("cpnl_cambios.csv", "municipio"): "Municipio afectado por la corrección",
}


def ficha(nombre: str, ruta: Path) -> list[str]:
    lineas = [f"### `{nombre}`", "", ARCHIVOS.get(nombre, "")]
    if ruta.suffix == ".csv":
        # Los códigos se leen como texto para no perder los ceros a la izquierda
        df = pd.read_csv(ruta, dtype={"codigo_municipio": str, "antes": str, "despues": str})
        lineas += ["", f"{len(df):,} filas y {df.shape[1]} columnas.".replace(",", "."), "",
                   "| Columna | Tipo | Descripción |", "|---|---|---|"]
        for col in df.columns:
            tipo = "número" if pd.api.types.is_numeric_dtype(df[col]) else "texto"
            descripcion = CONTEXTO.get((nombre, col), COLUMNAS.get(col, ""))
            lineas.append(f"| `{col}` | {tipo} | {descripcion} |")
    elif ruta.suffix == ".geojson":
        geo = json.loads(ruta.read_text(encoding="utf-8"))
        lineas += ["", f"{len(geo['features'])} elementos. Propiedades: `codigo_ambito` y `ambito`."]
    return lineas + [""]


def main():
    if DESTINO.exists():
        for carpeta in ORIGENES:
            shutil.rmtree(DESTINO / carpeta, ignore_errors=True)
    DESTINO.mkdir(parents=True, exist_ok=True)
    texto = ["# Diccionario de datos", "",
             "Datos de la entrega, copiados de `datos/procesados/` y `datos/fuentes_oficiales/` con "
             "`src/preparar_entrega.py`. Las fuentes y la limpieza están en `docs/fuentes_resumen.md`, "
             "`docs/calidad_datos.md` y `docs/calculos.md`.", ""]
    for carpeta, origen in ORIGENES.items():
        shutil.copytree(origen, DESTINO / carpeta)
        texto += [f"## {carpeta}/", ""]
        for ruta in sorted(origen.iterdir()):
            if ruta.suffix in (".csv", ".geojson", ".json"):
                texto += ficha(ruta.name, ruta)
    (DESTINO / "diccionario_datos.md").write_text("\n".join(texto), encoding="utf-8")
    copiados = sum(1 for _ in DESTINO.rglob("*") if _.is_file())
    print(f"Entrega de datos: {copiados} archivos en {DESTINO.relative_to(RAIZ)} (incluido diccionario_datos.md)")


if __name__ == "__main__":
    main()
