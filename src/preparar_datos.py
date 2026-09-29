"""
preparar_datos.py
-----------------
Descarga, limpia y valida las inscripciones a los cursos de catalán del
Consorci per a la Normalització Lingüística (CPNL).

Fuente oficial: Generalitat de Catalunya, portal de datos abiertos.
Dataset q9ct-fkjt: https://analisi.transparenciacatalunya.cat/d/q9ct-fkjt

Uso (desde la carpeta raíz del proyecto):
    python src/preparar_datos.py              # descarga el CSV oficial completo
    python src/preparar_datos.py --actualizar # fuerza una nueva descarga
    python src/preparar_datos.py --muestra    # usa la muestra incluida (sin internet)

Salidas en datos/procesados/:
    cpnl_municipios.csv      una fila por municipio y año (datos limpios)
    cpnl_cataluna_anual.csv  totales de Cataluña por año
    cpnl_validacion.csv      controles de coherencia por año
    cpnl_cambios.csv         correcciones aplicadas a la fuente
    metadatos.json           origen de los datos y fecha de proceso
"""

import argparse
import json
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
URL_CPNL = ("https://analisi.transparenciacatalunya.cat/api/v3/views/"
            "q9ct-fkjt/export.csv?accessType=DOWNLOAD")
ARCHIVO_ORIGINAL = RAIZ / "datos" / "originales" / "cpnl_inscripciones_raw.csv"
ARCHIVO_MUESTRA = RAIZ / "datos" / "muestra" / "cpnl_muestra_raw.csv"
CARPETA_SALIDA = RAIZ / "datos" / "procesados"

# Nombres en español, en el mismo orden que las 18 columnas de la fuente
COLUMNAS = [
    "municipio", "codigo_municipio", "anio", "total",
    "nivel_inicial_basico1",          # "Inicials i B1"      -> Inicial (A1) + Bàsic 1
    "nivel_basico23_elemental",       # "B2, B3 i elementals" -> Bàsic 2-3 (A2) + Elemental (B1)
    "nivel_intermedio_suficiencia",   # "Intermedis i suficiència" -> B2 + C1
    "nacidos_cataluna", "nacidos_resto_espana",
    "nacidos_extranjero_fuente", "sin_datos_origen",
    "ue", "resto_europa", "norte_africa", "resto_africa",
    "america_sur_central", "asia", "resto_mundo",
]
NUMERICAS = COLUMNAS[3:]
SUBREGIONES = ["ue", "resto_europa", "norte_africa", "resto_africa",
               "america_sur_central", "asia", "resto_mundo"]
PROVINCIAS = {"08": "Barcelona", "17": "Girona", "25": "Lleida", "43": "Tarragona"}


def descargar(forzar: bool) -> Path:
    """Descarga el CSV oficial si no existe (o si se pide actualizar)."""
    if ARCHIVO_ORIGINAL.exists() and not forzar:
        print(f"Uso el archivo ya descargado: {ARCHIVO_ORIGINAL.name}")
        return ARCHIVO_ORIGINAL
    print("Descargando datos oficiales del CPNL...")
    ARCHIVO_ORIGINAL.parent.mkdir(parents=True, exist_ok=True)
    peticion = urllib.request.Request(URL_CPNL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(peticion, timeout=120) as respuesta:
        ARCHIVO_ORIGINAL.write_bytes(respuesta.read())
    print(f"Descargado: {ARCHIVO_ORIGINAL.stat().st_size / 1024:.0f} KB")
    return ARCHIVO_ORIGINAL


def leer(ruta: Path) -> pd.DataFrame:
    """Lee todo como texto y renombra las columnas por posición."""
    df = pd.read_csv(ruta, dtype=str, keep_default_na=False)
    if df.shape[1] != len(COLUMNAS):
        sys.exit(f"La fuente tiene {df.shape[1]} columnas y se esperaban {len(COLUMNAS)}. "
                 "Revisa si el formato ha cambiado.")
    df.columns = COLUMNAS
    return df


def limpiar(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    cambios = []

    # 1. Números: la fuente usa coma de miles ("31,024") y celdas vacías
    for col in NUMERICAS:
        df[col] = (pd.to_numeric(df[col].str.replace(",", "", regex=False), errors="coerce")
                   .fillna(0).astype(int))
    df["anio"] = df["anio"].astype(int)
    df["codigo_municipio"] = df["codigo_municipio"].str.strip().str.zfill(6)
    df["municipio"] = df["municipio"].str.strip()

    # 2. Códigos erróneos: si un nombre aparece con varios códigos, uso el más frecuente
    #    (caso real: "Alfarràs" 2022 aparece con el código de Alfara de Carles)
    for nombre, grupo in df.groupby("municipio"):
        conteo = grupo["codigo_municipio"].value_counts()
        if len(conteo) > 1:
            correcto = conteo.index[0]
            filas = grupo[grupo["codigo_municipio"] != correcto]
            for _, fila in filas.iterrows():
                cambios.append({"tipo": "codigo corregido", "municipio": nombre,
                                "anio": fila["anio"], "antes": fila["codigo_municipio"],
                                "despues": correcto})
            df.loc[filas.index, "codigo_municipio"] = correcto

    # 3. Nombre único por código (el del año más reciente)
    nombre_actual = df.sort_values("anio").groupby("codigo_municipio")["municipio"].last()
    df["municipio"] = df["codigo_municipio"].map(nombre_actual)

    # 4. Duplicados código + año tras las correcciones: se suman
    #    (caso real: el código 000000 agrupa "sense dades" y cinco territorios de fuera de Cataluña)
    duplicados = df.duplicated(["codigo_municipio", "anio"], keep=False)
    if duplicados.any():
        for (codigo, anio), _ in df[duplicados].groupby(["codigo_municipio", "anio"]):
            cambios.append({"tipo": "duplicado sumado", "municipio": nombre_actual[codigo],
                            "anio": anio, "antes": codigo, "despues": codigo})
        df = (df.groupby(["codigo_municipio", "municipio", "anio"], as_index=False)[NUMERICAS]
              .sum())

    # 5. Ruptura de 2022: desde ese año "nacidos en el extranjero" incluye "sin datos"
    desde_2022 = df["anio"] >= 2022
    df["nacidos_extranjero"] = df["nacidos_extranjero_fuente"]
    df.loc[desde_2022, "nacidos_extranjero"] = (
        df.loc[desde_2022, "nacidos_extranjero_fuente"] - df.loc[desde_2022, "sin_datos_origen"])

    # 6. Columnas de apoyo
    df["provincia"] = df["codigo_municipio"].str[:2].map(PROVINCIAS)
    df["origen_conocido"] = df["nacidos_cataluna"] + df["nacidos_resto_espana"] + df["nacidos_extranjero"]

    # 7. Controles de coherencia (0 = cuadra)
    df["dif_niveles"] = df["total"] - df[["nivel_inicial_basico1", "nivel_basico23_elemental",
                                          "nivel_intermedio_suficiencia"]].sum(axis=1)
    df["dif_origen"] = df["total"] - (df["origen_conocido"] + df["sin_datos_origen"])
    df["dif_subregiones"] = df["nacidos_extranjero"] - df[SUBREGIONES].sum(axis=1)

    orden = ["codigo_municipio", "municipio", "provincia", "anio", "total",
             "nivel_inicial_basico1", "nivel_basico23_elemental", "nivel_intermedio_suficiencia",
             "nacidos_cataluna", "nacidos_resto_espana", "nacidos_extranjero", "sin_datos_origen",
             "origen_conocido"] + SUBREGIONES + ["dif_niveles", "dif_origen", "dif_subregiones"]
    return df[orden].sort_values(["codigo_municipio", "anio"]).reset_index(drop=True), cambios


def validar(df: pd.DataFrame) -> pd.DataFrame:
    """Resumen por año: cuántas filas no cuadran en cada control."""
    return (df.assign(filas=1,
                      falla_niveles=df["dif_niveles"] != 0,
                      falla_origen=df["dif_origen"] != 0,
                      falla_subregiones=df["dif_subregiones"] != 0)
            .groupby("anio")[["filas", "falla_niveles", "falla_origen", "falla_subregiones"]]
            .sum().reset_index())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--muestra", action="store_true", help="usar la muestra incluida")
    parser.add_argument("--actualizar", action="store_true", help="forzar nueva descarga")
    args = parser.parse_args()

    ruta = ARCHIVO_MUESTRA if args.muestra else descargar(args.actualizar)
    df, cambios = limpiar(leer(ruta))
    anual = df.groupby("anio", as_index=False).sum(numeric_only=True)
    validacion = validar(df)

    CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)
    df.to_csv(CARPETA_SALIDA / "cpnl_municipios.csv", index=False)
    anual.to_csv(CARPETA_SALIDA / "cpnl_cataluna_anual.csv", index=False)
    validacion.to_csv(CARPETA_SALIDA / "cpnl_validacion.csv", index=False)
    pd.DataFrame(cambios, columns=["tipo", "municipio", "anio", "antes", "despues"]).to_csv(
        CARPETA_SALIDA / "cpnl_cambios.csv", index=False)
    (CARPETA_SALIDA / "metadatos.json").write_text(json.dumps({
        "origen": "muestra" if args.muestra else "completo",
        "fuente": URL_CPNL,
        "procesado": datetime.now().isoformat(timespec="seconds"),
        "municipios": int(df["codigo_municipio"].nunique()),
        "anios": [int(df["anio"].min()), int(df["anio"].max())],
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nListo: {len(df):,} filas, {df['codigo_municipio'].nunique()} municipios, "
          f"{df['anio'].min()}-{df['anio'].max()}")
    print(f"Correcciones aplicadas: {len(cambios)}")
    print("\nControles por año (número de filas que no cuadran):")
    print(validacion.to_string(index=False))


if __name__ == "__main__":
    main()
