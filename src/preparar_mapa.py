"""
preparar_mapa.py
----------------
Prepara los datos de la pestaña "Mapa": la geometría de los 8 ámbitos territoriales
del Plan territorial general de Cataluña, la EULP 2023 por ámbito territorial y las inscripciones
del CPNL por ámbito territorial.

Fuentes oficiales (se descargan en datos/originales/ si no están):
    ICGC   Divisions administratives v2r2 (20/01/2026), municipios a escala 1:1.000.000
    Idescat Códigos territoriales: municipios con su comarca (id=50&n=9) y
            ámbitos territoriales de planificación con sus municipios (id=50&n=28)
    Idescat EULP 2023 por ámbito territorial: lengua habitual (n=3202), lengua inicial (n=3170)
            y conocimiento de lenguas (n=20833, una tabla por ámbito territorial)

Por qué municipios y no comarcas: según la tabla oficial del Idescat, dos comarcas
están repartidas entre dos ámbitos territoriales (Anoia: Comarques Centrals y Penedès; Moianès:
Metropolità y Comarques Centrals). Unir comarcas daría fronteras incorrectas, así que
cada ámbito territorial se construye uniendo sus municipios.

Uso (desde la carpeta raíz del proyecto; necesita requirements-dev.txt):
    python src/preparar_mapa.py
    python src/preparar_mapa.py --actualizar   # fuerza una nueva descarga

Salidas en datos/procesados/:
    mapa_ambitos.geojson     geometría simplificada de los 8 ámbitos territoriales (lon/lat)
    mapa_centroides.csv      punto interior de cada ámbito territorial para escribir las etiquetas
    eulp_territorio.csv      EULP 2023 por ámbito territorial: lengua habitual, lengua inicial y sabe hablar
    cpnl_ambito.csv          inscripciones del CPNL por ámbito territorial, año y total 2011-2023
"""

import argparse
import csv
import io
import json
import sys
import urllib.request
from pathlib import Path

import pandas as pd
from shapely import make_valid
from shapely.geometry import Point, mapping, shape
from shapely.ops import polylabel, unary_union

RAIZ = Path(__file__).resolve().parents[1]
ORIGINALES = RAIZ / "datos" / "originales"
PROCESADOS = RAIZ / "datos" / "procesados"

URL_ICGC = ("https://datacloud.icgc.cat/datacloud/divisions-administratives/json_unzip/"
            "divisions-administratives-v2r2-municipis-1000000-20260120.json")
ARCHIVO_ICGC = ORIGINALES / "icgc" / "divisions-administratives-v2r2-municipis-1000000-20260120.json"
URL_IDESCAT = "https://www.idescat.cat"
DESCARGAS_IDESCAT = {
    "idescat_codis/municipis_comarca.csv": "/codis/?id=50&n=9&f=ssv",
    "idescat_codis/ambits_municipis.csv": "/codis/?id=50&n=28&f=ssv",
    "idescat_eulp_territorio/llengua_habitual_ambits_2023.csv": "/pub/?id=eulp&n=3202&geo=at&f=ssv",
    "idescat_eulp_territorio/llengua_inicial_ambits_2023.csv": "/pub/?id=eulp&n=3170&geo=at&f=ssv",
    **{f"idescat_eulp_territorio/coneixement_AT0{i}_2023.csv": f"/pub/?id=eulp&n=20833&geo=at:AT0{i}&f=ssv"
       for i in range(1, 9)},
}

# Catalán como lengua habitual en 2023 según la nota del Idescat del 27/11/2025.
# Si los datos descargados no dan estas cifras, el script se detiene.
CONTROL_HABITUAL_2023 = {
    "Terres de l'Ebre": 66.8, "Comarques Centrals": 59.6, "Ponent": 51.1, "Alt Pirineu i Aran": 50.5,
    "Comarques Gironines": 45.0, "Camp de Tarragona": 37.9, "Penedès": 34.6, "Metropolità": 24.7,
}
TOLERANCIA_SIMPLIFICACION = 0.002   # grados (unos 200 m): suficiente para un mapa de 8 territorios
# Posición manual de algunas etiquetas (lon, lat): Metropolità, Penedès y Camp de Tarragona son
# vecinos y sus puntos interiores automáticos quedan tan cerca que las etiquetas se solapan.
# El script comprueba que cada punto cae dentro de su ámbito territorial; si no, usa el automático.
AJUSTE_ETIQUETA = {"AT01": (2.20, 41.58), "AT08": (1.65, 41.36), "AT03": (1.12, 41.33)}


def descargar(forzar: bool) -> None:
    """Descarga los archivos originales que falten (o todos, si se pide actualizar)."""
    pendientes = {ARCHIVO_ICGC: URL_ICGC}
    pendientes.update({ORIGINALES / ruta: URL_IDESCAT + url for ruta, url in DESCARGAS_IDESCAT.items()})
    for ruta, url in pendientes.items():
        if ruta.exists() and not forzar:
            continue
        ruta.parent.mkdir(parents=True, exist_ok=True)
        peticion = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(peticion, timeout=120) as respuesta:
            ruta.write_bytes(respuesta.read())
        print(f"Descargado: {ruta.relative_to(RAIZ)}")


def leer_ssv(ruta: Path) -> list[list[str]]:
    """Lee un archivo del Idescat separado por punto y coma (con líneas de cabecera)."""
    texto = ruta.read_text(encoding="utf-8-sig")
    return [fila for fila in csv.reader(io.StringIO(texto), delimiter=";") if fila]


def numero(texto: str) -> float | None:
    """Convierte un número del Idescat: "1062,5" -> 1062.5; ".." (dato confidencial) -> None."""
    texto = texto.strip()
    if texto in ("..", ""):
        return None
    if "," in texto:                 # "1.062,5": el punto es de miles y la coma, decimal
        texto = texto.replace(".", "").replace(",", ".")
    return float(texto)


def correspondencias() -> tuple[pd.DataFrame, dict[str, str]]:
    """Municipio -> comarca (n=9) y municipio -> ámbito territorial (n=28), ambas oficiales del Idescat."""
    municipios = pd.DataFrame(
        [f[:4] for f in leer_ssv(ORIGINALES / "idescat_codis" / "municipis_comarca.csv") if f[0][:1].isdigit()],
        columns=["codigo_municipio", "municipio", "codigo_comarca", "comarca"])
    ambitos, actual = {}, None
    for fila in leer_ssv(ORIGINALES / "idescat_codis" / "ambits_municipis.csv"):
        if fila[0] == "Àmbit territorial":
            actual = fila[1]
            ambitos[actual] = fila[2]
        elif fila[0] == "Municipi":
            municipios.loc[municipios["codigo_municipio"] == fila[1], "codigo_ambito"] = actual
    if municipios["codigo_ambito"].isna().any():
        sys.exit("Hay municipios sin ámbito territorial en la tabla del Idescat. Revisa las descargas.")
    partidas = municipios.groupby("comarca")["codigo_ambito"].nunique()
    print("Comarcas repartidas entre dos ámbitos territoriales:", ", ".join(partidas[partidas > 1].index) or "ninguna")
    return municipios, ambitos


def geometria(municipios: pd.DataFrame, ambitos: dict[str, str]) -> None:
    """Une los municipios del ICGC por ámbito territorial, simplifica y guarda el GeoJSON y los centroides."""
    icgc = json.loads(ARCHIVO_ICGC.read_text(encoding="utf-8"))
    municipio_ambito = municipios.set_index("codigo_municipio")["codigo_ambito"]
    grupos: dict[str, list] = {codigo: [] for codigo in ambitos}
    sin_ambito = []
    for elemento in icgc["features"]:
        codigo = elemento["properties"]["CODIMUNI"]
        if codigo in municipio_ambito:
            # Algunos polígonos de la fuente no son válidos (autointersecciones): se reparan
            grupos[municipio_ambito[codigo]].append(make_valid(shape(elemento["geometry"])))
        else:
            sin_ambito.append(codigo)
    if sin_ambito:
        sys.exit(f"Municipios del ICGC sin ámbito territorial en la tabla del Idescat: {sin_ambito}")

    elementos, centroides = [], []
    for codigo, piezas in grupos.items():
        union = unary_union(piezas)
        simple = union.simplify(TOLERANCIA_SIMPLIFICACION, preserve_topology=True)
        elementos.append({"type": "Feature",
                          "properties": {"codigo_ambito": codigo, "ambito": ambitos[codigo]},
                          "geometry": mapping(simple)})
        # Punto interior más alejado del borde: la etiqueta cae siempre dentro del ámbito territorial
        mayor = max(getattr(union, "geoms", [union]), key=lambda p: p.area)
        punto = polylabel(mayor, tolerance=0.001)
        if codigo in AJUSTE_ETIQUETA and union.contains(Point(AJUSTE_ETIQUETA[codigo])):
            punto = Point(AJUSTE_ETIQUETA[codigo])
        centroides.append({"codigo_ambito": codigo, "ambito": ambitos[codigo],
                           "lon": round(punto.x, 5), "lat": round(punto.y, 5)})

    salida = {"type": "FeatureCollection",
              "fuente": "ICGC, Divisions administratives v2r2 (20/01/2026), municipios 1:1.000.000; "
                        "ámbitos territoriales según Idescat (codis id=50&n=28)",
              "features": elementos}
    ruta = PROCESADOS / "mapa_ambitos.geojson"
    ruta.write_text(json.dumps(salida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    pd.DataFrame(centroides).to_csv(PROCESADOS / "mapa_centroides.csv", index=False)
    print(f"Geometría: {len(elementos)} ámbitos territoriales, {ruta.stat().st_size / 1024:.0f} KB")


def tabla_ambitos(ruta: Path) -> pd.DataFrame:
    """Tabla del Idescat por ámbitos territoriales (miles de personas): columnas Codi, Nom, lenguas..., Total."""
    filas = leer_ssv(ruta)
    cabecera = next(f for f in filas if f[0] == "Codi")
    datos = [f[:len(cabecera)] for f in filas if f[0].startswith("AT")]
    df = pd.DataFrame(datos, columns=cabecera)
    for col in cabecera[2:]:
        df[col] = df[col].map(numero)
    return df


def sabe_hablar() -> pd.DataFrame:
    """% de la población de 15 años o más que sabe hablar catalán en cada ámbito territorial."""
    filas = []
    for i in range(1, 9):
        tabla = leer_ssv(ORIGINALES / "idescat_eulp_territorio" / f"coneixement_AT0{i}_2023.csv")
        cabecera = next(f for f in tabla if f[0] == "" and "Saber parlar" in ";".join(f))
        catala = next(f for f in tabla if f[0] == "Català")
        col_pct = next(j for j, c in enumerate(cabecera) if "(%)" in c and "Saber parlar" in c)
        col_miles = next(j for j, c in enumerate(cabecera) if "(milers)" in c and "Saber parlar" in c)
        filas.append({"codigo_ambito": f"AT0{i}", "sabe_hablar_miles": numero(catala[col_miles]),
                      "sabe_hablar_pct": numero(catala[col_pct])})
    return pd.DataFrame(filas)


def eulp_territorio() -> None:
    habitual = tabla_ambitos(ORIGINALES / "idescat_eulp_territorio" / "llengua_habitual_ambits_2023.csv")
    inicial = tabla_ambitos(ORIGINALES / "idescat_eulp_territorio" / "llengua_inicial_ambits_2023.csv")
    df = pd.DataFrame({
        "codigo_ambito": habitual["Codi"], "ambito": habitual["Nom"], "año": 2023,
        "poblacion_15mas_miles": habitual["Total"],
        "habitual_catalan_miles": habitual["Català"],
        "habitual_catalan_pct": (habitual["Català"] / habitual["Total"] * 100).round(1),
        "inicial_catalan_miles": inicial["Català"].values,
        "inicial_catalan_pct": (inicial["Català"] / inicial["Total"] * 100).round(1).values,
    }).merge(sabe_hablar(), on="codigo_ambito")

    # Control obligatorio con la nota del Idescat
    obtenido = df.set_index("ambito")["habitual_catalan_pct"]
    distintos = {a: (v, obtenido.get(a)) for a, v in CONTROL_HABITUAL_2023.items() if obtenido.get(a) != v}
    if distintos:
        sys.exit(f"El catalán como lengua habitual no coincide con la nota del Idescat: {distintos}")
    print("Control superado: lengua habitual 2023 por ámbito territorial = nota del Idescat (27/11/2025).")

    df["fuente"] = ("Idescat, EULP 2023 por ámbitos territoriales del Plan territorial general de Cataluña (n=3202, n=3170 y n=20833); "
                    "% de lengua habitual e inicial calculados sobre la población de 15 años o más")
    df.to_csv(PROCESADOS / "eulp_territorio.csv", index=False)
    print(df[["ambito", "habitual_catalan_pct", "inicial_catalan_pct", "sabe_hablar_pct"]].to_string(index=False))


def cpnl_ambito(municipios: pd.DataFrame, ambitos: dict[str, str]) -> None:
    """Inscripciones del CPNL por ámbito territorial, por año y en total 2011-2023 (sin el código 000000)."""
    cpnl = pd.read_csv(PROCESADOS / "cpnl_municipios.csv", dtype={"codigo_municipio": str})
    cpnl = cpnl[cpnl["codigo_municipio"] != "000000"]
    cpnl = cpnl.merge(municipios[["codigo_municipio", "codigo_comarca", "codigo_ambito"]],
                      on="codigo_municipio", how="left")
    sin_ambito = cpnl[cpnl["codigo_ambito"].isna()]
    if not sin_ambito.empty:
        print("Códigos del CPNL sin ámbito territorial (no se usan en el mapa):",
              sorted(sin_ambito["codigo_municipio"].unique()),
              f"({int(sin_ambito['total'].sum())} inscripciones)")
    cpnl = cpnl.dropna(subset=["codigo_ambito"])
    columnas = ["total", "nacidos_cataluna", "nacidos_resto_espana", "nacidos_extranjero",
                "sin_datos_origen", "origen_conocido"]
    por_anio = cpnl.groupby(["codigo_ambito", "anio"], as_index=False)[columnas].sum()
    por_anio["periodo"] = por_anio["anio"].astype(str)
    total = cpnl.groupby("codigo_ambito", as_index=False)[columnas].sum()
    total["periodo"] = f"{cpnl['anio'].min()}–{cpnl['anio'].max()}"
    df = pd.concat([por_anio.drop(columns="anio"), total], ignore_index=True)
    df.insert(1, "ambito", df["codigo_ambito"].map(ambitos))
    for origen in ["cataluna", "resto_espana", "extranjero"]:
        df[f"pct_{origen}"] = (df[f"nacidos_{origen}"] / df["origen_conocido"] * 100).round(1)
    df.to_csv(PROCESADOS / "cpnl_ambito.csv", index=False)
    print(f"CPNL por ámbito territorial: {len(df)} filas ({df['periodo'].nunique()} periodos)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--actualizar", action="store_true", help="forzar nueva descarga")
    args = parser.parse_args()
    descargar(args.actualizar)
    PROCESADOS.mkdir(parents=True, exist_ok=True)
    municipios, ambitos = correspondencias()
    eulp_territorio()          # primero, para detenerse si el control falla
    geometria(municipios, ambitos)
    cpnl_ambito(municipios, ambitos)


if __name__ == "__main__":
    main()
