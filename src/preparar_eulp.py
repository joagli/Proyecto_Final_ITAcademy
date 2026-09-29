"""
preparar_eulp.py
----------------
Limpia las tablas de la Encuesta de usos lingüísticos de la población (EULP)
descargadas del Idescat (https://www.idescat.cat/pub/?id=eulp) y las deja en
formato largo, listo para la app.

Uso (desde la carpeta raíz del proyecto):
    python src/preparar_eulp.py

Entrada:  datos/originales/idescat_eulp/<carpeta por tabla>/*.csv
Salidas en datos/procesados/:
    eulp_lengua_segmento.csv       lengua inicial, de identificación y habitual
                                   por sexo, edad y lugar de nacimiento
    eulp_conocimiento_segmento.csv conocimiento del catalán por sexo, edad y
                                   lugar de nacimiento
    eulp_ambitos_segmento.csv      usos por ámbito y segmento
"""

import glob
import re
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
ENTRADA = RAIZ / "datos" / "originales" / "idescat_eulp"
SALIDA = RAIZ / "datos" / "procesados"

# Agrupación de las categorías de lengua para que los gráficos sean legibles
GRUPOS = {
    "catalán": "Catalán",
    "catalán y castellano": "Catalán y castellano",
    "castellano": "Castellano",
}
ORDEN_GRUPOS = ["Catalán", "Catalán y castellano", "Castellano", "Otras y no consta"]

USOS = {
    "solo catalán": "Solo catalán",
    "más catalán que castellano": "Más catalán que castellano",
    "catalán y castellano": "Igual catalán que castellano",
    "más castellano que catalán": "Más castellano que catalán",
    "solo castellano": "Solo castellano",
}
ORDEN_USOS = list(USOS.values()) + ["Otras y no consta"]


ETIQUETAS_SEGMENTO = {
    "Cataluña": ("Cataluña", 1), "resto de España": ("Resto de España", 2),
    "extranjero": ("Extranjero", 3), "hombres": ("Hombres", 1), "mujeres": ("Mujeres", 2),
    "total": ("total", 99),
}


def etiquetar(df):
    """Pone mayúscula inicial a los segmentos y añade un orden para los gráficos."""
    def nombre(v):
        return ETIQUETAS_SEGMENTO.get(v, (v[0].upper() + v[1:] if v else v, 50))[0]

    def orden(v):
        if v in ETIQUETAS_SEGMENTO:
            return ETIQUETAS_SEGMENTO[v][1]
        numeros = re.findall(r"\d+", str(v))
        return int(numeros[0]) if numeros else 50

    df["orden_segmento"] = df["segmento"].map(orden)
    df["segmento"] = df["segmento"].map(nombre)
    return df


def leer(patron: str) -> pd.DataFrame:
    """Lee y junta todos los CSV de una carpeta (el Idescat los separa por año)."""
    archivos = sorted(glob.glob(str(ENTRADA / patron / "*.csv")))
    if not archivos:
        raise SystemExit(f"No encuentro archivos en {ENTRADA / patron}")
    df = pd.concat([pd.read_csv(f, sep=";", encoding="utf-8-sig") for f in archivos],
                   ignore_index=True)
    df.columns = [c.strip() for c in df.columns]
    # El valor viene con coma decimal y "null" cuando el dato es confidencial.
    # Además, algunas filas usan 9999999 como código de dato no disponible.
    df["valor"] = pd.to_numeric(
        df["valor"].astype(str).str.replace(",", ".", regex=False).replace("null", None),
        errors="coerce")
    df.loc[df["valor"] >= 9_000_000, "valor"] = pd.NA
    df["año"] = df["año"].astype(int)
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
    return df


def porcentajes(df, col_segmento, col_categoria, mapa, orden, nombre_segmento):
    """Agrupa categorías menores y calcula el % sobre el total de cada segmento."""
    d = df[df[col_categoria] != "total"].copy()
    totales = (df[df[col_categoria] == "total"]
               .groupby(["año", col_segmento])["valor"].sum().rename("total"))
    d["categoria"] = d[col_categoria].map(mapa).fillna("Otras y no consta")
    d = (d.groupby(["año", col_segmento, "categoria"], as_index=False)["valor"].sum()
         .merge(totales, on=["año", col_segmento], how="left"))
    d["pct"] = d["valor"] / d["total"] * 100
    d = d.rename(columns={col_segmento: "segmento", "valor": "miles"})
    d["tipo_segmento"] = nombre_segmento
    d["orden_categoria"] = d["categoria"].map({c: i for i, c in enumerate(orden)})
    d = etiquetar(d)
    return d[["año", "tipo_segmento", "segmento", "orden_segmento", "categoria",
              "orden_categoria", "miles", "total", "pct"]]


def lenguas():
    """Lengua inicial, de identificación y habitual por sexo, edad y nacimiento."""
    tablas = [
        ("Lengua inicial", "Por_lengua_inicial_y_edad", "edad", "Edad"),
        ("Lengua inicial", "Por_lengua_inicial_y_lugar_de_nacimiento", "lugar de nacimiento", "Lugar de nacimiento"),
        ("Lengua de identificación", "Por_lengua_de_identificacio_n_y_edad_en_grandes_grupos", "edad", "Edad"),
        ("Lengua de identificación", "Por_lengua_de_identificacio_n_y_lugar_de_nacimiento", "lugar de nacimiento", "Lugar de nacimiento"),
        ("Lengua de identificación", "Por_lengua_de_identificacio_n_y_sexo", "sexo", "Sexo"),
        ("Lengua habitual", "Por_lengua_habitual_y_lugar_de_nacimiento", "lugar de nacimiento", "Lugar de nacimiento"),
        ("Lengua habitual", "Por_lengua_habitual_y_sexo", "sexo", "Sexo"),
    ]
    salida = []
    for indicador, carpeta, col, nombre in tablas:
        df = leer(carpeta)
        d = porcentajes(df, col, "lengua", GRUPOS, ORDEN_GRUPOS, nombre)
        d.insert(1, "indicador", indicador)
        salida.append(d)
    return pd.concat(salida, ignore_index=True)


def conocimiento():
    """Conocimiento del catalán (%) por sexo, edad quinquenal y lugar de nacimiento."""
    tablas = [
        ("Por_conocimiento_de_lenguas_y_sexo", "sexo", "Sexo"),
        ("Por_conocimiento_de_lenguas_y_lugar_de_nacimiento", "lugar de nacimiento", "Lugar de nacimiento"),
        ("Por_conocimiento_del_catala_n_y_edad_quinquenal", "edad", "Edad"),
    ]
    salida = []
    for carpeta, col, nombre in tablas:
        df = leer(carpeta)
        d = df[(df["lengua"] == "catalán") & (df["concepto"].str.startswith("proporción"))].copy()
        d = d.rename(columns={col: "segmento", "habilidades lingüísticas": "habilidad", "valor": "pct"})
        d["tipo_segmento"] = nombre
        salida.append(etiquetar(d)[["año", "tipo_segmento", "segmento", "orden_segmento",
                                    "habilidad", "pct"]])
    return pd.concat(salida, ignore_index=True)


def ambitos():
    """Usos lingüísticos por ámbito de uso y segmento."""
    tablas = [
        ("Por_usos_lingu_isticos__a_mbitos_de_uso_y_sexo", "sexo", "Sexo"),
        ("Por_usos_lingu_isticos__a_mbitos_de_uso_y_grupos_de_edad", "edad", "Edad"),
        ("Por_usos_lingu_isticos__a_mbitos_de_uso_y_lugar_de_nacimiento", "lugar de nacimiento", "Lugar de nacimiento"),
    ]
    salida = []
    for carpeta, col, nombre in tablas:
        df = leer(carpeta).rename(columns={"ámbitos de uso de la lengua": "ambito",
                                           "usos lingüísticos": "uso"})
        d = df[df["uso"] != "total"].copy()
        totales = (df[df["uso"] == "total"]
                   .groupby(["año", "ambito", col])["valor"].sum().rename("total"))
        d["categoria"] = d["uso"].map(USOS).fillna("Otras y no consta")
        d = (d.groupby(["año", "ambito", col, "categoria"], as_index=False)["valor"].sum()
             .merge(totales, on=["año", "ambito", col], how="left"))
        d["pct"] = d["valor"] / d["total"] * 100
        d = d.rename(columns={col: "segmento", "valor": "miles"})
        d["tipo_segmento"] = nombre
        d["orden_categoria"] = d["categoria"].map({c: i for i, c in enumerate(ORDEN_USOS)})
        salida.append(etiquetar(d)[["año", "ambito", "tipo_segmento", "segmento", "orden_segmento",
                                    "categoria", "orden_categoria", "miles", "total", "pct"]])
    return pd.concat(salida, ignore_index=True)


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    for nombre, df in [("eulp_lengua_segmento", lenguas()),
                       ("eulp_conocimiento_segmento", conocimiento()),
                       ("eulp_ambitos_segmento", ambitos())]:
        df.to_csv(SALIDA / f"{nombre}.csv", index=False)
        print(f"{nombre}.csv: {len(df):,} filas, años {sorted(df['año'].unique())}")
        if "tipo_segmento" in df:
            print("   segmentos:", df["tipo_segmento"].unique().tolist())


if __name__ == "__main__":
    main()
