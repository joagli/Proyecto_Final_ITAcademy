"""
app.py - ¿Se está "apagando" el catalán?
App en Streamlit para el proyecto final (Sprint 13, IT Academy).

Ejecutar:  streamlit run app.py
Antes:     python src/preparar_datos.py   (descarga y limpia los datos del CPNL)
           python src/preparar_eulp.py    (limpia las tablas de la EULP)
"""

import json
import math
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

RAIZ = Path(__file__).parent
OFICIALES = RAIZ / "datos" / "fuentes_oficiales"
PROCESADOS = RAIZ / "datos" / "procesados"

TITULO = '¿Se está "apagando" el catalán?'

AZUL = "#1D4E89"      # catalán
OCRE = "#B8862B"      # castellano
GRIS = "#8A94A6"
TEXTO_OSCURO = "#1B1F24"

# Un color fijo por categoría en toda la app
COLOR_ORIGEN = {"Cataluña": "#2A7F62", "Resto de España": "#C8553D", "Extranjero": "#6D5BA8"}
COLOR_LENGUA = {"Catalán": AZUL, "Catalán y castellano": "#9DB9D9",
                "Castellano": OCRE, "Otras y no consta": GRIS}
COLOR_USOS = {"Solo catalán": AZUL, "Más catalán que castellano": "#4F7FB4",
              "Igual catalán que castellano": "#9DB9D9", "Más castellano que catalán": "#E0C48A",
              "Solo castellano": OCRE, "Otras y no consta": GRIS}
COLOR_USOS_SIMPLE = {"Solo o más catalán": AZUL, "Igual catalán que castellano": "#9DB9D9",
                     "Solo o más castellano": OCRE, "Otras y no consta": GRIS}
COLOR_HABILIDAD = {"Entiende": "#6F8FBA", "Sabe hablar": AZUL,
                   "Sabe leer": "#4F7FB4", "Sabe escribir": OCRE}
COLOR_NIVEL = {"Inicial y Básico 1": "#9DB9D9", "Básico 2-3 y Elemental": "#4F7FB4",
               "Intermedio y Suficiencia": AZUL}
# Sexo y edad no usan el azul del catalán ni el dorado del castellano
COLOR_SEXO = {"Hombres": "#37474F", "Mujeres": "#B5306B"}
COLOR_EDAD = {"De 15 a 29 años": "#D0588A", "De 30 a 44 años": "#A8386B",
              "De 45 a 64 años": "#6E1B47", "65 años o más": "#37474F"}

SIN_MUNICIPIO = "Sin municipio o fuera de Cataluña"

st.set_page_config(page_title=TITULO, page_icon="🗣️", layout="wide")


# ---------- Carga de datos ----------
@st.cache_data
def cargar():
    eulp = pd.read_csv(OFICIALES / "eulp_cataluna.csv")
    censo = pd.read_csv(OFICIALES / "censo_conocimiento.csv")
    edad = pd.read_csv(OFICIALES / "conocimiento_edad_2021.csv")
    lengua_seg = pd.read_csv(PROCESADOS / "eulp_lengua_segmento.csv")
    conoc_seg = pd.read_csv(PROCESADOS / "eulp_conocimiento_segmento.csv")
    ambitos_seg = pd.read_csv(PROCESADOS / "eulp_ambitos_segmento.csv")
    cpnl = pd.read_csv(PROCESADOS / "cpnl_municipios.csv", dtype={"codigo_municipio": str})
    # El código 000000 agrupa "sense dades" y territorios de fuera de Cataluña (ver Calidad de datos)
    cpnl.loc[cpnl["codigo_municipio"] == "000000", "municipio"] = SIN_MUNICIPIO
    validacion = pd.read_csv(PROCESADOS / "cpnl_validacion.csv")
    cambios = pd.read_csv(PROCESADOS / "cpnl_cambios.csv", dtype={"antes": str, "despues": str})
    meta = json.loads((PROCESADOS / "metadatos.json").read_text(encoding="utf-8"))
    return (eulp, censo, edad, lengua_seg, conoc_seg, ambitos_seg,
            cpnl, validacion, cambios, meta)


@st.cache_data
def cargar_mapa():
    """Datos de la pestaña "Mapa" (los genera src/preparar_mapa.py). None si faltan."""
    archivos = ["mapa_ambitos.geojson", "mapa_centroides.csv", "eulp_territorio.csv", "cpnl_ambito.csv"]
    if not all((PROCESADOS / a).exists() for a in archivos):
        return None
    geo = json.loads((PROCESADOS / "mapa_ambitos.geojson").read_text(encoding="utf-8"))
    return (geo, pd.read_csv(PROCESADOS / "mapa_centroides.csv"),
            pd.read_csv(PROCESADOS / "eulp_territorio.csv"), pd.read_csv(PROCESADOS / "cpnl_ambito.csv"))


(eulp, censo, edad, lengua_seg, conoc_seg, ambitos_seg,
 cpnl, validacion, cambios, meta) = cargar()
datos_mapa = cargar_mapa()

es_muestra = meta["origen"] == "muestra"


def sin_total(df):
    return df[df["segmento"] != "total"]


# ---------- Formato español (coma decimal, punto de miles) ----------
def num(valor, decimales=1, signo=False):
    if pd.isna(valor):
        return ""
    # Mitades hacia arriba (636,5 -> 637), como en la presentación; Python redondearía al par (636).
    # Antes se limpia el error de coma flotante (0,24999999999999997 es 0,25).
    redondeado = Decimal(f"{valor:.10f}").quantize(Decimal(1).scaleb(-decimales), rounding=ROUND_HALF_UP)
    texto = f"{redondeado:{'+' if signo else ''},.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(valor, decimales=1):
    return f"{num(valor, decimales)}%" if pd.notna(valor) else ""


def miles(valor):
    return num(valor, 0)


def millones(valor):
    return f"{num(valor / 1e6, 2)} M"


ETIQUETAS = {
    "anio": "Año", "total": "Inscripciones", "municipio": "Municipio", "provincia": "Provincia",
    "codigo_municipio": "Código", "nivel_inicial_basico1": "Inicial y Básico 1",
    "nivel_basico23_elemental": "Básico 2-3 y Elemental",
    "nivel_intermedio_suficiencia": "Intermedio y Suficiencia",
    "nacidos_cataluna": "Nacidos en Cataluña", "nacidos_resto_espana": "Nacidos en el resto de España",
    "nacidos_extranjero": "Nacidos en el extranjero", "sin_datos_origen": "Sin datos de origen",
    "origen_conocido": "Origen conocido", "ue": "Unión Europea", "resto_europa": "Resto de Europa",
    "norte_africa": "Norte de África", "resto_africa": "Resto de África",
    "america_sur_central": "América del Sur y Central", "asia": "Asia", "resto_mundo": "Resto del mundo",
    "pct_extranjero": "% nacidos en el extranjero", "filas": "Filas",
    "falla_niveles": "Descuadres por nivel", "falla_origen": "Descuadres por origen",
    "falla_subregiones": "Descuadres por región", "tipo": "Tipo", "antes": "Antes", "despues": "Después",
}


def en_espanol(df):
    """Renombra las columnas técnicas a etiquetas en español para mostrarlas."""
    return df.rename(columns=ETIQUETAS)


def tabla(df, numericas=()):
    """Tabla en Markdown: se ve entera (sin desplazamiento interno) y se imprime bien."""
    columnas = list(df.columns)
    alineacion = ["---:" if c in numericas else "---" for c in columnas]
    filas = ["| " + " | ".join(columnas) + " |", "| " + " | ".join(alineacion) + " |"]
    for _, fila in df.iterrows():
        filas.append("| " + " | ".join(str(v).replace("|", "/") for v in fila) + " |")
    st.markdown("\n".join(filas))


# ---------- Piezas comunes de los gráficos ----------
def escala(colores):
    return alt.Scale(domain=list(colores), range=list(colores.values()))


def leyenda(columnas=4):
    """Leyenda abajo y sin recortar."""
    return alt.Legend(orient="bottom", title=None, labelLimit=0, columns=columnas, symbolType="square")


def titulo(texto, subtitulo=None):
    if subtitulo:
        return alt.TitleParams(text=texto, subtitle=subtitulo, anchor="start", subtitleColor="#5B6573")
    return alt.TitleParams(text=texto, anchor="start")


def nota(fuente, anios, universo, aviso=None):
    """Una línea bajo el gráfico: "Fuente: organismo, fuente (años) · universo", y como mucho una
    advertencia breve. El resto va a las notas metodológicas de la pestaña."""
    texto = f"Fuente: {fuente}" + (f" ({anios})" if anios else "") + f" · {universo}"
    st.caption(texto + (f" · {aviso}" if aviso else ""))


def notas_metodologicas(notas):
    """Desplegable al final de cada pestaña con la información que no cabe en las notas."""
    with st.expander("Notas metodológicas", expanded=False):
        st.markdown("\n".join(f"- {n}" for n in notas) +
                    "\n\nMás detalle en la pestaña Calidad de datos y en la carpeta `docs/` del proyecto.")


def texto_sobre(color):
    """Blanco sobre colores oscuros, casi negro sobre colores claros."""
    r, g, b = (int(color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return TEXTO_OSCURO if 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.55 else "white"


def marcas(minimo, maximo, cuantas=5):
    """Valores redondos para las marcas de un eje: `cuantas` como máximo."""
    rango = max(maximo - minimo, 1e-9)
    pasos = sorted(b * 10 ** p for b in (1, 2, 2.5, 5) for p in range(-1, 8))
    paso = next(p for p in pasos if rango / p <= cuantas - 1)
    valor, valores = math.ceil(minimo / paso) * paso, []
    while valor <= maximo + 1e-9:
        valores.append(round(valor, 6))
        valor += paso
    return valores


# Etiquetas de los ejes con coma decimal y punto de miles
FORMATO_EJE = "replace(replace(replace(format(datum.value, ',.2~f'), /,/g, 'X'), /[.]/g, ','), /X/g, '.')"


def eje(valores, es_pct, titulo_eje=None, **extra):
    return alt.Axis(values=valores, title=titulo_eje, labelLimit=0,
                    labelExpr=FORMATO_EJE + (" + '%'" if es_pct else ""), **extra)


EJE_CAT = alt.Axis(labelLimit=0, labelAngle=0, title=None)


def posicion_etiquetas(df, x, y, serie):
    """En cada año: la etiqueta de la serie más alta va encima, la de la más baja debajo;
    las intermedias, en el lado con más espacio hasta la serie vecina."""
    df = df.copy()
    df["pos"] = "arriba"
    if serie is None:
        return df
    for _, grupo in df.groupby(x):
        orden = grupo.sort_values(y, ascending=False)
        indices, valores = list(orden.index), list(orden[y])
        if len(indices) < 2:
            continue
        df.at[indices[-1], "pos"] = "abajo"
        for k in range(1, len(indices) - 1):
            hueco_arriba = valores[k - 1] - valores[k]
            hueco_abajo = valores[k] - valores[k + 1]
            df.at[indices[k], "pos"] = "arriba" if hueco_arriba >= hueco_abajo else "abajo"
    return df


def grafico_lineas(df, x, y, *, serie=None, colores=None, color_fijo=AZUL, titulo_graf,
                   dominio=None, alto=460, tooltip=(), formato=pct, leyenda_cols=4, referencia_hasta=None,
                   anios_proporcionales=False):
    """Líneas con el valor escrito en cada punto.

    Con `referencia_hasta`, el tramo hasta ese valor de x se dibuja con línea discontinua
    (datos que solo sirven como referencia). Con `anios_proporcionales`, el eje de años es
    continuo: la distancia entre puntos es proporcional a los años que los separan.
    """
    df = posicion_etiquetas(df.dropna(subset=[y]), x, y, serie)
    df["etiqueta"] = df[y].map(formato)
    minimo, maximo = dominio if dominio else (df[y].min(), df[y].max())
    if not dominio:
        margen = (maximo - minimo) * 0.15 or 1
        minimo, maximo = max(0, minimo - margen), maximo + margen
    rango = maximo - minimo
    # Margen para que las etiquetas de arriba y de abajo quepan dentro del gráfico
    escala_y = alt.Scale(domain=[minimo - rango * 0.12, maximo + rango * 0.14], nice=False, zero=False)
    if anios_proporcionales:
        anios = sorted(df[x].unique())
        eje_x = alt.X(f"{x}:Q", scale=alt.Scale(domain=[anios[0] - 2, anios[-1] + 2], nice=False, zero=False),
                      axis=alt.Axis(values=anios, format="d", labelAngle=0, labelLimit=0, title=None))
    else:
        eje_x = alt.X(f"{x}:O", axis=EJE_CAT)
    base = alt.Chart(df).encode(
        x=eje_x,
        y=alt.Y(f"{y}:Q", scale=escala_y, axis=eje(marcas(minimo, maximo), formato is pct)),
    )
    consejo = [*tooltip, alt.Tooltip("etiqueta:N", title="Valor")]
    if serie:
        color = alt.Color(f"{serie}:N", scale=escala(colores), sort=list(colores), legend=leyenda(leyenda_cols))
        texto_color = alt.Color(f"{serie}:N", scale=escala(colores), legend=None)
        estilo_linea, estilo_punto = {}, {}
    else:
        color = texto_color = alt.value(color_fijo)
        estilo_linea, estilo_punto = {"color": color_fijo}, {"color": color_fijo}
    if referencia_hasta is None:
        lineas = [base.mark_line(**estilo_linea).encode(color=color)]
    else:
        lineas = [base.mark_line(**estilo_linea).encode(color=color)
                  .transform_filter(alt.datum[x] >= referencia_hasta),
                  base.mark_line(**estilo_linea, strokeDash=[5, 4]).encode(color=color)
                  .transform_filter(alt.datum[x] <= referencia_hasta)]
    puntos = base.mark_point(filled=True, size=60, opacity=1, **estilo_punto).encode(color=color, tooltip=consejo)
    arriba = base.mark_text(dy=-13, fontSize=12, fontWeight="bold").encode(
        text="etiqueta:N", color=texto_color).transform_filter(alt.datum.pos == "arriba")
    abajo = base.mark_text(dy=16, fontSize=12, fontWeight="bold").encode(
        text="etiqueta:N", color=texto_color).transform_filter(alt.datum.pos == "abajo")
    return alt.layer(*lineas, puntos, arriba, abajo).properties(height=alto, title=titulo_graf)


def grafico_apilado(df, categoria, serie, valor, colores, *, titulo_graf, eje_valor=None, horizontal=True,
                    orden_categoria=None, formato=pct, totales=None, dominio=None, alto=None,
                    tooltip=(), leyenda_cols=4, minimo_etiqueta=5):
    """Barras apiladas con el valor dentro de cada segmento que ocupa al menos
    `minimo_etiqueta` % de su barra (los menores, solo en el tooltip). En barras absolutas,
    además, el segmento debe medir al menos el 5% del eje para que el texto quepa.

    `totales` (opcional) es un dict categoría -> texto que se escribe al final de cada barra.
    """
    orden_serie = {s: i for i, s in enumerate(colores)}
    d = df.copy()
    d["_orden"] = d[serie].map(orden_serie)
    d = d.sort_values([categoria, "_orden"])
    d["fin"] = d.groupby(categoria)[valor].cumsum()
    d["inicio"] = d["fin"] - d[valor]
    d["medio"] = (d["inicio"] + d["fin"]) / 2
    cuota = d[valor] / d.groupby(categoria)[valor].transform("sum") * 100
    d["etiqueta"] = d[valor].map(formato)
    tope = d["fin"].max()
    visible = cuota >= minimo_etiqueta
    if formato is not pct:
        # En barras absolutas, un segmento pequeño en una barra baja tampoco tiene sitio
        visible &= d[valor] >= tope * 0.05
    d["etiqueta_dentro"] = d["etiqueta"].where(visible, "")
    d["color_texto"] = d[serie].map(lambda s: texto_sobre(colores[s]))
    if formato is pct:
        valores_eje = [0, 50, 100]
        dominio = dominio or [0, max(100, tope)]
    else:
        dominio = dominio or [0, tope * (1.1 if totales else 1.0)]
        valores_eje = marcas(0, tope)
    escala_v = alt.Scale(domain=dominio, nice=False)
    if horizontal:
        cat = alt.Y(f"{categoria}:O", sort=orden_categoria, axis=EJE_CAT)
        v1 = alt.X("inicio:Q", scale=escala_v, axis=eje(valores_eje, formato is pct, eje_valor))
        v2, vm, vf = alt.X2("fin:Q"), alt.X("medio:Q"), alt.X("fin:Q")
        canal_cat, canal_v = "y", "x"
    else:
        cat = alt.X(f"{categoria}:O", sort=orden_categoria, axis=EJE_CAT)
        v1 = alt.Y("inicio:Q", scale=escala_v, axis=eje(valores_eje, formato is pct))
        v2, vm, vf = alt.Y2("fin:Q"), alt.Y("medio:Q"), alt.Y("fin:Q")
        canal_cat, canal_v = "x", "y"
    barras = alt.Chart(d).mark_bar().encode(
        **{canal_cat: cat, canal_v: v1, f"{canal_v}2": v2},
        color=alt.Color(f"{serie}:N", scale=escala(colores), sort=list(colores), legend=leyenda(leyenda_cols)),
        tooltip=[*tooltip, alt.Tooltip(f"{serie}:N", title="Categoría"),
                 alt.Tooltip("etiqueta:N", title="Valor")],
    )
    dentro = alt.Chart(d).mark_text(fontSize=12).encode(
        **{canal_cat: cat, canal_v: vm},
        text="etiqueta_dentro:N", color=alt.Color("color_texto:N", scale=None),
    )
    capas = [barras, dentro]
    if totales:
        t = d.groupby(categoria, as_index=False)["fin"].max()
        t["texto"] = t[categoria].map(totales)
        marca = dict(align="left", dx=5) if horizontal else dict(baseline="bottom", dy=-5)
        capas.append(alt.Chart(t).mark_text(fontSize=12, fontWeight="bold", color=TEXTO_OSCURO, **marca).encode(
            **{canal_cat: cat, canal_v: vf}, text="texto:N"))
    if alto is None:
        alto = 150 + 38 * d[categoria].nunique() if horizontal else 460
    return alt.layer(*capas).properties(height=alto, title=titulo_graf)


def grafico_barras(df, categoria, valor, *, color, titulo_graf, eje_valor=None, formato=pct,
                   horizontal=True, orden=None, dominio=None, alto=None, tooltip=(), dentro=None):
    """Barras simples con el valor escrito al final de cada barra.

    `dentro` (opcional) es una columna de texto que se escribe en el centro de cada barra.
    """
    d = df.copy()
    d["etiqueta"] = d[valor].map(formato)
    tope = d[valor].max()
    if dominio is None:
        dominio = [0, tope * 1.15]
    valores_eje = marcas(0, min(dominio[1], 100) if formato is pct else tope)
    escala_v = alt.Scale(domain=dominio, nice=False)
    if horizontal:
        enc = dict(y=alt.Y(f"{categoria}:N", sort=orden or "-x", axis=EJE_CAT),
                   x=alt.X(f"{valor}:Q", scale=escala_v, axis=eje(valores_eje, formato is pct, eje_valor)))
        marca_texto = dict(align="left", dx=5)
    else:
        enc = dict(x=alt.X(f"{categoria}:N", sort=orden, axis=EJE_CAT),
                   y=alt.Y(f"{valor}:Q", scale=escala_v, axis=eje(valores_eje, formato is pct)))
        marca_texto = dict(baseline="bottom", dy=-5)
    base = alt.Chart(d).encode(**enc)
    barras = base.mark_bar(color=color).encode(
        tooltip=[*tooltip, alt.Tooltip("etiqueta:N", title="Valor")])
    texto = base.mark_text(fontSize=12, fontWeight="bold", color=TEXTO_OSCURO, **marca_texto).encode(
        text="etiqueta:N")
    capas = [barras, texto]
    if dentro:
        d["_medio"] = d[valor] / 2
        canal = "x" if horizontal else "y"
        capas.append(alt.Chart(d).mark_text(fontSize=12, color="white").encode(
            **{k: v for k, v in enc.items() if k != canal},
            **{canal: alt.X("_medio:Q") if horizontal else alt.Y("_medio:Q")}, text=f"{dentro}:N"))
    if alto is None:
        alto = 130 + 40 * d[categoria].nunique() if horizontal else 400
    return alt.layer(*capas).properties(height=alto, title=titulo_graf)


# Nombres de los ámbitos territoriales partidos en líneas para que la etiqueta quepa dentro del territorio
ROTULO_AMBITO = {"Comarques Gironines": "Comarques\nGironines", "Camp de Tarragona": "Camp de\nTarragona",
                 "Terres de l'Ebre": "Terres\nde l'Ebre", "Comarques Centrals": "Comarques\nCentrals",
                 "Alt Pirineu i Aran": "Alt Pirineu\ni Aran"}


def grafico_mapa(valores, campo, *, color, dominio, titulo_graf, titulo_leyenda, tooltip=(), alto=680,
                 tamano_texto=12, halo=False, formato=pct):
    """Coropleta de los 8 ámbitos territoriales con el nombre y el valor escritos en cada territorio.

    `valores` tiene una fila por ámbito territorial con codigo_ambito y la columna `campo`
    (en % por defecto; con `formato=miles`, un número absoluto).
    `tooltip` es una lista de (columna, título, decimales) que se muestran con formato español.
    """
    geo, centroides = datos_mapa[0], datos_mapa[1]
    v = valores.copy()
    v["etiqueta"] = v[campo].map(formato)
    extra = []
    for columna, titulo_tt, decimales in tooltip:
        v[f"{columna}_txt"] = v[columna].map(lambda x, d=decimales: num(x, d))
        extra.append(alt.Tooltip(f"{columna}_txt:N", title=titulo_tt))
    rotulos = centroides.merge(v, on=["codigo_ambito", "ambito"], how="left")
    rotulos["rotulo"] = rotulos["ambito"].map(lambda a: ROTULO_AMBITO.get(a, a)) + "\n" + rotulos["etiqueta"]
    # Texto blanco sobre los tonos más oscuros de la escala
    rotulos["color_texto"] = (rotulos[campo] > dominio[0] + (dominio[1] - dominio[0]) * 0.6).map(
        {True: "white", False: TEXTO_OSCURO})
    campos_extra = [c for c in v.columns if c not in ("codigo_ambito",)]
    formas = alt.Chart(alt.Data(values=geo["features"])).mark_geoshape(stroke="white", strokeWidth=1.5).encode(
        color=alt.Color(f"{campo}:Q", scale=alt.Scale(domain=dominio, range=["#F4F5F7", color], interpolate="rgb"),
                        legend=alt.Legend(orient="bottom", title=titulo_leyenda, gradientLength=240,
                                          titleLimit=0, labelLimit=0,
                                          values=[dominio[0], (dominio[0] + dominio[1]) / 2, dominio[1]],
                                          labelExpr=FORMATO_EJE + (" + '%'" if formato is pct else ""))),
        tooltip=[alt.Tooltip("ambito:N", title="Ámbito territorial"), alt.Tooltip("etiqueta:N", title="Valor"), *extra],
    ).transform_lookup(lookup="properties.codigo_ambito",
                       from_=alt.LookupData(v, "codigo_ambito", campos_extra))
    estilo = dict(lineBreak="\n", fontSize=tamano_texto, fontWeight="bold", lineHeight=tamano_texto + 2)
    posicion = dict(longitude="lon:Q", latitude="lat:Q", text="rotulo:N")
    if halo:
        # Mapas pequeños: texto oscuro con un halo blanco debajo, legible sobre cualquier tono y fuera del borde
        capas_texto = [alt.Chart(rotulos).mark_text(**estilo, stroke="white", strokeWidth=3, strokeJoin="round",
                                                    color="white").encode(**posicion),
                       alt.Chart(rotulos).mark_text(**estilo, color=TEXTO_OSCURO).encode(**posicion)]
    else:
        # Condición y no escala: la capa de formas ya usa una escala de color cuantitativa
        capas_texto = [alt.Chart(rotulos).mark_text(**estilo).encode(
            **posicion,
            color=alt.condition(alt.datum.color_texto == "white", alt.value("white"), alt.value(TEXTO_OSCURO)))]
    return (alt.layer(formas, *capas_texto).project(type="mercator")
            .properties(height=alto, title=titulo_graf))


def grafico_mapa_origenes(valores, columnas, *, formato, fondo, dominio_fondo, color_fondo, titulo_fondo,
                         titulo_graf, alto=720, tamano_texto=12):
    """Un solo mapa con los tres orígenes: en cada ámbito territorial, el nombre y debajo tres cifras
    (Cataluña, resto de España y extranjero), cada una con su color de COLOR_ORIGEN.

    `columnas` asigna a cada origen su columna de `valores`; `formato` escribe las cifras (pct o miles).
    El fondo de cada ámbito se colorea por la columna `fondo`.
    """
    geo, centroides = datos_mapa[0], datos_mapa[1]
    v = valores.copy()
    for origen_m, columna in columnas.items():
        v[f"{columna}_txt"] = v[columna].map(formato)
    v["total_txt"] = v["total"].map(miles)
    rotulos = centroides.merge(v, on=["codigo_ambito", "ambito"], how="left")
    # Nombre en una o dos líneas: la última va justo encima de las cifras
    lineas_nombre = rotulos["ambito"].map(lambda a: ROTULO_AMBITO.get(a, a).split("\n"))
    rotulos["nombre_1"] = lineas_nombre.map(lambda l: l[0] if len(l) > 1 else "")
    rotulos["nombre_2"] = lineas_nombre.map(lambda l: l[-1])
    formas = alt.Chart(alt.Data(values=geo["features"])).mark_geoshape(stroke="white", strokeWidth=1.5).encode(
        # fill y no color: el color de las cifras usa su propia escala (los tres orígenes)
        fill=alt.Fill(f"{fondo}:Q", scale=alt.Scale(domain=dominio_fondo, range=["#F4F5F7", color_fondo],
                                                    interpolate="rgb"),
                      legend=alt.Legend(orient="bottom", title=titulo_fondo, gradientLength=240, titleLimit=0,
                                        labelLimit=0, labelExpr=FORMATO_EJE + (" + '%'" if formato is pct else ""),
                                        values=[dominio_fondo[0], (dominio_fondo[0] + dominio_fondo[1]) / 2,
                                                dominio_fondo[1]])),
        tooltip=[alt.Tooltip("ambito:N", title="Ámbito territorial"),
                 *[alt.Tooltip(f"{c}_txt:N", title=f"Nacidos en {o.lower() if o != 'Cataluña' else o}")
                   for o, c in columnas.items()],
                 alt.Tooltip("total_txt:N", title="Inscripciones")],
    ).transform_lookup(lookup="properties.codigo_ambito",
                       from_=alt.LookupData(v, "codigo_ambito", [c for c in v.columns if c != "codigo_ambito"]))
    alto_linea = tamano_texto + 3
    estilo = dict(fontSize=tamano_texto, fontWeight="bold", baseline="middle")
    halo = dict(stroke="white", strokeWidth=3, strokeJoin="round", color="white")
    posicion = dict(longitude="lon:Q", latitude="lat:Q")
    # Cinco líneas centradas en el ámbito: dos para el nombre y, debajo, una cifra por origen
    capas = []
    for i, campo_nombre in enumerate(["nombre_1", "nombre_2"]):
        linea_nombre = dict(**estilo, dy=(i - 2) * alto_linea)
        capas += [alt.Chart(rotulos).mark_text(**linea_nombre, **halo).encode(**posicion, text=f"{campo_nombre}:N"),
                  alt.Chart(rotulos).mark_text(**linea_nombre, color=TEXTO_OSCURO).encode(
                      **posicion, text=f"{campo_nombre}:N")]
    escala_origen = alt.Scale(domain=list(COLOR_ORIGEN), range=list(COLOR_ORIGEN.values()))
    for i, (origen_m, columna) in enumerate(columnas.items()):
        linea = alt.Chart(rotulos.assign(origen=origen_m))
        cifra = dict(**estilo, dy=i * alto_linea)
        capas += [linea.mark_text(**cifra, **halo).encode(**posicion, text=f"{columna}_txt:N"),
                  linea.mark_text(**cifra).encode(
                      **posicion, text=f"{columna}_txt:N",
                      color=alt.Color("origen:N", scale=escala_origen,
                                      legend=alt.Legend(orient="bottom", title="Cifras: nacidos en…",
                                                        symbolType="square", labelLimit=0)))]
    return (alt.layer(formas, *capas).project(type="mercator")
            .properties(height=alto, title=titulo_graf))


def mostrar(grafico, donde=st):
    donde.altair_chart(grafico, width="stretch")


FUENTE_EULP = "Idescat y Generalitat, EULP"
FUENTE_CPNL = "CPNL, inscripciones a sus cursos"
EULP_15 = "población de 15 años o más"


# ---------- Encabezado ----------
st.title(TITULO)
st.markdown("#### Lo que se dice y lo que dicen los datos")
st.caption("Datos oficiales del Idescat, la Generalitat de Catalunya, el CPNL y el INE")

(tab_hip, tab_con, tab_uso, tab_quien, tab_amb, tab_mapa, tab_apr, tab_cal) = st.tabs(
    ["La hipótesis", "Conocimiento", "Uso", "¿Quién lo habla?", "¿Con quién se usa?", "Mapa",
     "Aprendizaje (CPNL)", "Calidad de datos"])


# ---------- 0. La hipótesis ----------
with tab_hip:
    st.markdown(
        '**Lo que se escucha en la calle:** *"el catalán se está muriendo"*.  \n'
        "Si fuera verdad, los datos tendrían que mostrar estas cuatro cosas. Las pongo a prueba una por una."
    )
    mostrar_resultados = st.toggle("Mostrar resultados", value=False,
                                   help="Desactivado, solo se ven las afirmaciones, sin datos ni veredictos.")
    serie_c = censo[censo["comparable_con_serie"] == "si"]
    c0, c1 = serie_c.iloc[0], serie_c.iloc[-1]
    jov = edad.loc[edad["grupo_edad"] == "15-29", "pct_sabe_hablar"].iloc[0]
    may = edad.loc[edad["grupo_edad"] == "75-84", "pct_sabe_hablar"].iloc[0]
    e0, e1 = eulp.iloc[0], eulp.iloc[-1]
    e08 = eulp[eulp["anio"] == 2008].iloc[0]
    e18 = eulp[eulp["anio"] == 2018].iloc[0]
    ambito_hip = "Barcelona" if es_muestra else "Total CPNL"
    datos_hip = cpnl[cpnl["municipio"] == "Barcelona"] if es_muestra else cpnl
    por_anio_hip = datos_hip.groupby("anio")["total"].sum().sort_index()
    anio_hip = int(por_anio_hip.index[-1])
    # Mínimo de la serie antes de la COVID-19 (2011–2019)
    sin_covid = por_anio_hip[por_anio_hip.index < 2020]
    anio_min, valor_min = int(sin_covid.idxmin()), sin_covid.min()
    fila_hip = datos_hip[datos_hip["anio"] == anio_hip]
    pct_ext_hip = fila_hip["nacidos_extranjero"].sum() / fila_hip["origen_conocido"].sum() * 100
    pct_sin_mun_hip = fila_hip.loc[fila_hip["municipio"] == SIN_MUNICIPIO, "total"].sum() / fila_hip["total"].sum() * 100
    # Personas de 15 años o más que saben hablar catalán según la EULP: población × % que sabe hablar
    habla_eulp = (conoc_seg[(conoc_seg["tipo_segmento"] == "Sexo") & (conoc_seg["segmento"] == "total") &
                            (conoc_seg["habilidad"] == "saber hablar")].set_index("año")["pct"])
    pob_eulp = eulp.set_index("anio")["poblacion_15mas_miles"]
    mas_hablantes = (pob_eulp[2023] * habla_eulp[2023] - pob_eulp[2008] * habla_eulp[2008]) / 100 * 1000

    pruebas = [
        ("1. Cada vez menos personas saben catalán",
         f"Las personas que saben hablarlo pasaron de {millones(c0.personas_sabe_hablar)} ({c0.anio}) "
         f"a {millones(c1.personas_sabe_hablar)} ({c1.anio}). Según la EULP, unas "
         f"{miles(round(mas_hablantes, -4))} personas más de 15 años o más saben hablarlo entre 2008 y 2023 "
         f"(del {pct(habla_eulp[2008])} al {pct(habla_eulp[2023])}).", "Mito"),
        ("2. Los jóvenes ya no lo saben",
         f"Lo sabe hablar el {pct(jov)} de las personas de 15 a 29 años, frente al {pct(may)} "
         "de las de 75 a 84 (2021).", "Mito"),
        ("3. Ya casi nadie lo aprende",
         f"{ambito_hip}: {miles(por_anio_hip.iloc[-1])} inscripciones al CPNL en {anio_hip}, un "
         f"{num((por_anio_hip.iloc[-1] / valor_min - 1) * 100, 0)}% más que en {anio_min} ({miles(valor_min)}), "
         f"el mínimo antes de la COVID-19. El {pct(pct_ext_hip)} de las inscripciones con origen conocido son "
         f"de personas nacidas en el extranjero."
         + ("" if es_muestra else f" Incluye un {pct(pct_sin_mun_hip)} de inscripciones sin municipio catalán "
                                  "asignado."), "Mito"),
        ("4. Cada vez menos gente lo usa en su día a día",
         f"Desde {e08.anio}, el catalán como lengua habitual pasa del {pct(e08.lengua_habitual_catalan_pct)} al "
         f"{pct(e1.lengua_habitual_catalan_pct)}. La caída se concentra entre {e18.anio} y {e1.anio} "
         f"({num(e1.lengua_habitual_catalan_pct - e18.lengua_habitual_catalan_pct, signo=True)} puntos; entre "
         f"{e08.anio} y {e18.anio} había subido {num(e18.lengua_habitual_catalan_pct - e08.lengua_habitual_catalan_pct)}). "
         f"En {e0.anio} era el {pct(e0.lengua_habitual_catalan_pct)} (dato enlazado, solo como referencia).",
         "Realidad (en %)"),
    ]
    filas = [st.columns(2), st.columns(2)]
    for i, (afirmacion, dato, veredicto) in enumerate(pruebas):
        with filas[i // 2][i % 2].container(border=True):
            st.markdown(f"**{afirmacion}**")
            if mostrar_resultados:
                st.markdown(dato)
                color = "blue" if veredicto == "Mito" else "orange"
                st.markdown(f":{color}-badge[{veredicto}]")

    if mostrar_resultados:
        st.subheader("Veredicto: no se apaga, se transforma")
        st.markdown(
            "Cada vez más personas saben catalán y, desde 2008, quienes lo tienen como lengua habitual se "
            "mantienen en unos 2,2 millones aunque la población crece. Su peso baja sobre todo porque cambia "
            "cómo se habla: desde 2013, más personas —también nacidas en Cataluña— combinan catalán y castellano."
        )
        if es_muestra:
            st.caption("La prueba 3 usa Barcelona hasta cargar el dataset completo del CPNL.")


# ---------- 1. Conocimiento ----------
with tab_con:
    notas_con = []
    serie = censo[censo["comparable_con_serie"] == "si"]
    ini, fin = serie.iloc[0], serie.iloc[-1]
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Saben hablar catalán ({ini.anio})", pct(ini.pct_sabe_hablar))
    c2.metric(f"Saben hablar catalán ({fin.anio})", pct(fin.pct_sabe_hablar),
              f"{num(fin.pct_sabe_hablar - ini.pct_sabe_hablar, signo=True)} pp", delta_color="off")
    c3.metric(f"Personas que saben hablarlo ({fin.anio})",
              f"{miles(fin.personas_sabe_hablar)}",
              f"{num((fin.personas_sabe_hablar / ini.personas_sabe_hablar - 1) * 100, signo=True)}% desde {ini.anio}",
              delta_color="off")

    # Un panel por habilidad (las cuatro líneas juntas solapaban sus etiquetas)
    largo = serie.melt(id_vars="anio",
                       value_vars=["pct_entiende", "pct_sabe_hablar", "pct_sabe_leer", "pct_sabe_escribir"],
                       var_name="habilidad", value_name="porcentaje")
    largo["habilidad"] = largo["habilidad"].map({
        "pct_entiende": "Entiende", "pct_sabe_hablar": "Sabe hablar",
        "pct_sabe_leer": "Sabe leer", "pct_sabe_escribir": "Sabe escribir"})
    st.markdown(f"#### Conocimiento del catalán, {ini.anio}–{fin.anio}")
    st.caption("Censos lingüísticos · % de la población de 2 años o más, un panel por habilidad")
    paneles = st.columns(2) + st.columns(2)
    for panel, (habilidad_c, color_c) in zip(paneles, COLOR_HABILIDAD.items()):
        mostrar(grafico_lineas(
            largo[largo["habilidad"] == habilidad_c], "anio", "porcentaje", color_fijo=color_c,
            dominio=[0, 100], alto=320, titulo_graf=titulo(habilidad_c), anios_proporcionales=True,
            tooltip=[alt.Tooltip("anio:Q", title="Año", format="d")]), panel)
    personas = serie[["anio", "personas_sabe_hablar", "pct_sabe_hablar"]].assign(
        millones=serie["personas_sabe_hablar"] / 1e6, pct_txt=serie["pct_sabe_hablar"].map(pct))
    mostrar(grafico_barras(
        personas, "anio", "millones", color=AZUL, horizontal=False, orden=list(personas["anio"]),
        formato=lambda v: num(v, 2), dentro="pct_txt",
        titulo_graf=titulo(f"Personas que saben hablar catalán (millones), {ini.anio}–{fin.anio}",
                           "Censos lingüísticos · encima, millones de personas; dentro, % de la población "
                           "de 2 años o más"),
        tooltip=[alt.Tooltip("anio:O", title="Año"), alt.Tooltip("pct_txt:N", title="% de la población")]))
    nuevo = censo[censo["comparable_con_serie"] == "no"].iloc[0]
    nota("Idescat, censos lingüísticos", f"{ini.anio}–{fin.anio}", "población de 2 años o más",
         f"{nuevo.anio}, pregunta distinta: fuera de la serie")
    notas_con.append(f'Censos lingüísticos: en {nuevo.anio} la pregunta cambió (respuestas "bien" y "con '
                     f'dificultad"), por eso no se une a la serie {ini.anio}–{fin.anio}: en {nuevo.anio}, el '
                     f"{pct(nuevo.pct_sabe_hablar)} sabe hablar catalán y el {pct(nuevo.pct_sabe_escribir)} sabe "
                     "escribirlo. El censo de 2011 ya combinó registros administrativos con una gran encuesta "
                     "por muestreo (cerca del 9% de la población, según el INE).")

    habilidades = {"saber hablar": "Sabe hablar", "entender": "Entiende", "saber leer": "Sabe leer",
                   "saber escribir": "Sabe escribir",
                   "conocimiento en todas las habilidades": "Las cuatro habilidades"}
    frase_habilidad = {"saber hablar": "Sabe hablar catalán", "entender": "Entiende el catalán",
                       "saber leer": "Sabe leer en catalán", "saber escribir": "Sabe escribir en catalán",
                       "conocimiento en todas las habilidades": "Entiende, habla, lee y escribe catalán"}
    habilidad = st.selectbox("Habilidad (EULP, por lugar de nacimiento)", list(habilidades),
                             index=0, format_func=habilidades.get)
    origen = sin_total(conoc_seg[(conoc_seg["tipo_segmento"] == "Lugar de nacimiento") &
                                 (conoc_seg["habilidad"] == habilidad)])
    mostrar(grafico_lineas(
        origen, "año", "pct", serie="segmento", colores=COLOR_ORIGEN, dominio=[0, 100],
        titulo_graf=titulo(f"{frase_habilidad[habilidad]}, según lugar de nacimiento, 2008–2023",
                           "EULP · % de la población de 15 años o más de cada origen"),
        tooltip=[alt.Tooltip("año:O", title="Año"), alt.Tooltip("segmento:N", title="Nacidos en")]))
    nota(FUENTE_EULP, "2008–2023", EULP_15)

    habilidades_calor = {"saber hablar": ("Saber hablar", "Sabe hablar catalán", "% que sabe hablar catalán"),
                         "saber escribir": ("Saber escribir", "Sabe escribir en catalán",
                                            "% que sabe escribir en catalán")}
    habilidad_calor = st.selectbox("Habilidad (mapa de calor por edad)", list(habilidades_calor), index=0,
                                   format_func=lambda h: habilidades_calor[h][0])
    _, frase_calor, leyenda_calor = habilidades_calor[habilidad_calor]
    calor = sin_total(conoc_seg[(conoc_seg["tipo_segmento"] == "Edad") &
                                (conoc_seg["habilidad"] == habilidad_calor)]).copy()
    # Escala desde la decena inferior al mínimo, para que se vean las diferencias en las dos habilidades
    inicio_calor = int(calor["pct"].min() // 10 * 10)
    # "65 años o más" (solo existe en 2008) va justo antes de "De 65 a 69 años"
    calor["orden"] = calor["orden_segmento"] - (calor["segmento"] == "65 años o más") * 0.5
    orden_edad = list(calor.sort_values("orden")["segmento"].drop_duplicates())
    calor["etiqueta"] = calor["pct"].map(lambda v: num(v))
    base_calor = alt.Chart(calor).encode(
        x=alt.X("año:O", axis=alt.Axis(labelAngle=0, orient="top", title=None)),
        y=alt.Y("segmento:N", sort=orden_edad, axis=EJE_CAT),
    )
    celdas = base_calor.mark_rect(stroke="white").encode(
        color=alt.Color("pct:Q", scale=alt.Scale(scheme="blues", domain=[inicio_calor, 100]),
                        legend=alt.Legend(orient="bottom", title=leyenda_calor, gradientLength=260,
                                          values=[inicio_calor, (inicio_calor + 100) / 2, 100])),
        tooltip=[alt.Tooltip("año:O", title="Año"), alt.Tooltip("segmento:N", title="Edad"),
                 alt.Tooltip("etiqueta:N", title=leyenda_calor)])
    texto_celdas = base_calor.mark_text(fontSize=12).encode(
        text="etiqueta:N",
        color=alt.condition(alt.datum.pct > inicio_calor + (100 - inicio_calor) * 0.6,
                            alt.value("white"), alt.value(TEXTO_OSCURO)))
    mostrar(alt.layer(celdas, texto_celdas).properties(
        height=36 * len(orden_edad) + 150,
        title=titulo(f"{frase_calor}, por edad y año, 2008–2023",
                     "EULP · % de cada grupo de edad (población de 15 años o más)")))
    nota(FUENTE_EULP, "2008–2023", EULP_15, "2008: mayores de 65 años en un solo grupo")
    notas_con.append('Mapa de calor por edad: en 2008 los mayores de 65 años se publican en un solo grupo ("65 '
                     'años o más"); desde 2013, en grupos de 5 años. Las celdas vacías no existen en esa edición.')

    mostrar(grafico_barras(
        edad, "grupo_edad", "pct_sabe_hablar", color=AZUL, horizontal=False,
        orden=list(edad["grupo_edad"]), dominio=[0, 112],
        titulo_graf=titulo("Sabe hablar catalán, por edad, 2021 (incluye de 2 a 14 años)",
                           "Idescat a partir de la ECEPOV-2021 (INE) · % de cada grupo de edad"),
        tooltip=[alt.Tooltip("grupo_edad:N", title="Edad")]))
    nota("Idescat a partir del INE, ECEPOV-2021", "2021", "población de 2 años o más",
         "pregunta distinta: no comparable con los censos ni la EULP")
    notas_con.append("Gráfico de 2021: ECEPOV-2021 (Encuesta de Características Esenciales de la Población y las "
                     "Viviendas, INE), explotada por el Idescat. Es la única fuente que incluye a los niños de 2 a "
                     '14 años, y por eso muestra el efecto de la escuela. La pregunta tiene grados ("bien", "con '
                     'dificultad") y no es comparable con los censos anteriores ni con la EULP.')
    notas_con.append("EULP: encuesta por muestreo a la población de 15 años o más; en 2023, 8.682 entrevistas y "
                     "un error de alrededor del 1% para el conjunto de Cataluña.")
    notas_metodologicas(notas_con)


# ---------- 2. Uso ----------
with tab_uso:
    # 2003 solo es referencia (cambió el cuestionario en 2008): los KPI se calculan desde 2008
    notas_uso = []
    ref2003 = eulp.iloc[0]
    a, b = eulp[eulp["anio"] == 2008].iloc[0], eulp.iloc[-1]
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Lengua habitual: catalán ({b.anio})", pct(b.lengua_habitual_catalan_pct),
              f"{num(b.lengua_habitual_catalan_pct - a.lengua_habitual_catalan_pct, signo=True)} pp desde {a.anio}",
              delta_color="off")
    c2.metric(f"Población de 15 años o más ({b.anio})", f"{num(b.poblacion_15mas_miles / 1000, 2)} M",
              f"{num((b.poblacion_15mas_miles / a.poblacion_15mas_miles - 1) * 100, signo=True)}% desde {a.anio}",
              delta_color="off")
    c3.metric(f"Catalán como lengua inicial ({b.anio})", f"{num(b.lengua_inicial_catalan_miles / 1000, 2)} M",
              f"{num((b.lengua_inicial_catalan_miles / a.lengua_inicial_catalan_miles - 1) * 100, signo=True)}% "
              f"desde {a.anio}", delta_color="off")

    uso = eulp.melt(id_vars="anio", value_vars=["lengua_habitual_catalan_pct", "lengua_inicial_catalan_pct"],
                    var_name="indicador", value_name="porcentaje")
    colores_uso = {"Catalán como lengua habitual": AZUL, "Catalán como lengua inicial (materna)": GRIS}
    uso["indicador"] = uso["indicador"].map({
        "lengua_habitual_catalan_pct": "Catalán como lengua habitual",
        "lengua_inicial_catalan_pct": "Catalán como lengua inicial (materna)"})
    mostrar(grafico_lineas(
        uso, "anio", "porcentaje", serie="indicador", colores=colores_uso, dominio=[0, 50], referencia_hasta=2008,
        titulo_graf=titulo(f"Uso del catalán, {ref2003.anio}–{b.anio}",
                           "EULP · % de la población de 15 años o más · 2003 en discontinua, solo como referencia"),
        tooltip=[alt.Tooltip("anio:O", title="Año"), alt.Tooltip("indicador:N", title="Indicador")]))
    nota(FUENTE_EULP, f"{ref2003.anio}–{b.anio}", EULP_15, f"{ref2003.anio}, solo como referencia")
    notas_uso.append(f'{ref2003.anio}: dato enlazado del Idescat ("Dades enllaçades 2003-2008-2013", tablas '
                     "n=7198 y n=7218), solo como referencia. En 2008 cambiaron el cuestionario, la selección de "
                     "la muestra y el modo de entrevista, y los datos enlazados solo recalculan pesos y calibración "
                     "con los criterios de 2008 (Idescat, EULP 2008, notas metodológicas). Por eso los indicadores "
                     "de arriba se calculan desde 2008. 2018 y 2023: tablas de lengua inicial y habitual del Idescat.")

    habitual = lengua_seg[(lengua_seg["indicador"] == "Lengua habitual") &
                          (lengua_seg["tipo_segmento"] == "Lugar de nacimiento")]
    habitual_total = habitual[habitual["segmento"] == "total"]
    poblacion = habitual_total.groupby("año")["total"].first()
    catalan_miles = habitual_total[habitual_total["categoria"] == "Catalán"].set_index("año")["miles"]
    mostrar(grafico_apilado(
        habitual_total, "año", "categoria", "miles", COLOR_LENGUA, horizontal=False,
        formato=miles, totales={a_: f"{num(p / 1000, 2)} M" for a_, p in poblacion.items()},
        titulo_graf=titulo("Personas por lengua habitual, 2008–2023",
                           "EULP · miles de personas de 15 años o más; encima, la población total"),
        tooltip=[alt.Tooltip("año:O", title="Año")]))
    nota(FUENTE_EULP, "2008–2023", EULP_15, 'salto de 2013 en "Catalán y castellano": posible efecto metodológico')
    notas_uso.append(f"Personas por lengua habitual: el catalán se mantiene en torno a los 2,2 millones de "
                     f"hablantes habituales "
         f"({num(catalan_miles.min() / 1000, 2)}–{num(catalan_miles.max() / 1000, 2)} M) mientras la "
         f"población crece. En 2003 (dato enlazado, solo como referencia), "
         f"{num(ref2003.lengua_habitual_catalan_pct / 100 * ref2003.poblacion_15mas_miles / 1000, 2)} millones "
         'tenían el catalán como lengua habitual. El salto de "Catalán y castellano" entre 2008 y 2013 '
         f"({miles(habitual_total.set_index(['año', 'categoria']).loc[(2008, 'Catalán y castellano'), 'miles'])} → "
         f"{miles(habitual_total.set_index(['año', 'categoria']).loc[(2013, 'Catalán y castellano'), 'miles'])} "
         "miles) puede deberse en parte a los cambios metodológicos de esas ediciones: según el Idescat, en "
         "2008 se reformularon algunas preguntas y categorías de respuesta y se añadió la entrevista "
         "presencial, y en 2013 se añadió la respuesta por internet y cambió la estimación de la población. "
         "El Idescat no cuantifica su efecto en este indicador.")

    st.subheader("¿Por qué baja el porcentaje?")
    por_origen = sin_total(habitual)
    pob_origen = por_origen.groupby(["año", "segmento"], as_index=False)["total"].first()
    mostrar(grafico_apilado(
        pob_origen, "año", "segmento", "total", COLOR_ORIGEN, horizontal=False, formato=miles,
        totales={a_: f"{num(p / 1000, 2)} M" for a_, p in poblacion.items()},
        titulo_graf=titulo("Población de 15 años o más, por lugar de nacimiento, 2008–2023",
                           "EULP · miles de personas; encima, la población total"),
        tooltip=[alt.Tooltip("año:O", title="Año")]))
    nota(FUENTE_EULP, "2008–2023", EULP_15)

    medida = st.radio("Lengua habitual", ["Catalán", "Catalán o catalán y castellano"], horizontal=True)
    categorias = ["Catalán"] if medida == "Catalán" else ["Catalán", "Catalán y castellano"]
    tasas = (por_origen[por_origen["categoria"].isin(categorias)]
             .groupby(["año", "segmento"], as_index=False)["pct"].sum())
    mostrar(grafico_lineas(
        tasas, "año", "pct", serie="segmento", colores=COLOR_ORIGEN, dominio=[0, 100],
        titulo_graf=titulo(f"Lengua habitual: {medida.lower()}, según lugar de nacimiento, 2008–2023",
                           "EULP · % de la población de 15 años o más de cada origen"),
        tooltip=[alt.Tooltip("año:O", title="Año"), alt.Tooltip("segmento:N", title="Nacidos en")]))
    nota(FUENTE_EULP, "2008–2023", EULP_15)

    # Descomposición shift-share del cambio del % entre la primera y la última edición.
    # Forma simétrica de Kitagawa (1955): cada efecto usa la media de los dos años del otro factor
    pesos = pob_origen.pivot(index="año", columns="segmento", values="total")
    pesos = pesos.div(pesos.sum(axis=1), axis=0)
    r = tasas.pivot(index="año", columns="segmento", values="pct")
    a0, a1 = int(r.index.min()), int(r.index.max())
    total_pct = (pesos * r).sum(axis=1)
    cambio = total_pct[a1] - total_pct[a0]
    efecto_composicion = ((pesos.loc[a1] - pesos.loc[a0]) * (r.loc[a0] + r.loc[a1]) / 2).sum()
    efecto_dentro = ((r.loc[a1] - r.loc[a0]) * (pesos.loc[a0] + pesos.loc[a1]) / 2).sum()
    nacidos_cat = por_origen[por_origen["segmento"] == "Cataluña"].set_index(["año", "categoria"])["pct"]
    # Personas (miles) con el catalán como única lengua habitual, y con el catalán solo o con el castellano
    miles_habitual = habitual_total.pivot_table(index="año", columns="categoria", values="miles")
    solo_cat = miles_habitual["Catalán"]
    con_cat = miles_habitual["Catalán"] + miles_habitual["Catalán y castellano"]
    inicial_cat = (lengua_seg[(lengua_seg["indicador"] == "Lengua inicial") &
                              (lengua_seg["tipo_segmento"] == "Lugar de nacimiento") &
                              (lengua_seg["segmento"] == "Cataluña")].set_index(["año", "categoria"])["pct"])
    if medida == "Catalán":
        publicado = (eulp.set_index("anio").loc[a1, "lengua_habitual_catalan_pct"]
                     - eulp.set_index("anio").loc[a0, "lengua_habitual_catalan_pct"])
        aclaracion = (f" Con los valores publicados, redondeados a un decimal, el cambio es de "
                      f"{num(publicado, signo=True)} puntos; la diferencia se debe al redondeo.")
    else:
        aclaracion = ""
    with st.container(border=True):
        st.markdown(
            f"**¿Cambia quién vive aquí o cambia cómo habla cada grupo?** Entre {a0} y {a1}, el % con "
            f'"{medida.lower()}" como lengua habitual pasó del {pct(total_pct[a0])} al {pct(total_pct[a1])}: '
            f"**{num(cambio, 2, signo=True)} puntos**, calculado con los valores sin redondear.{aclaracion} "
            f"Se descompone en:\n"
            f"- **Efecto composición: {num(efecto_composicion, 2, signo=True)} puntos.** Lo que habría cambiado "
            f"solo por el nuevo peso de cada origen (con las tasas medias de ambos años). Los nacidos en "
            f"Cataluña pasan del "
            f"{pct(pesos.loc[a0, 'Cataluña'] * 100)} al {pct(pesos.loc[a1, 'Cataluña'] * 100)} de la "
            f"población; los nacidos en el extranjero, del {pct(pesos.loc[a0, 'Extranjero'] * 100)} al "
            f"{pct(pesos.loc[a1, 'Extranjero'] * 100)}, sobre todo en lugar de los nacidos en el resto de "
            f"España ({pct(pesos.loc[a0, 'Resto de España'] * 100)} → "
            f"{pct(pesos.loc[a1, 'Resto de España'] * 100)}).\n"
            f"- **Efecto dentro de los grupos: {num(efecto_dentro, 2, signo=True)} puntos.** Lo que cambió el uso "
            f"dentro de cada origen (con los pesos medios de ambos años).\n\n"
            f'Entre los nacidos en Cataluña, de 2018 a 2023, la lengua habitual "Catalán" pasa del '
            f"{pct(nacidos_cat[(2018, 'Catalán')])} al {pct(nacidos_cat[(2023, 'Catalán')])} y \"Catalán y "
            f"castellano\", del {pct(nacidos_cat[(2018, 'Catalán y castellano')])} al "
            f"{pct(nacidos_cat[(2023, 'Catalán y castellano')])}.\n\n"
            f"Entre 2018 y 2023, quienes tienen solo el catalán como lengua habitual bajan unas "
            f"{miles(round(-(solo_cat[2023] - solo_cat[2018]) * 1000, -3))} personas, pero quienes usan el catalán "
            f"solo o combinado con el castellano pasan de {num(con_cat[2018] / 1000, 2)} a "
            f"{num(con_cat[2023] / 1000, 2)} millones.\n\n"
            f"En la lengua inicial de los nacidos en Cataluña, de {a0} a {a1}: catalán, del "
            f"{pct(inicial_cat[(a0, 'Catalán')])} al {pct(inicial_cat[(a1, 'Catalán')])}; catalán y castellano, "
            f"del {pct(inicial_cat[(a0, 'Catalán y castellano')])} al "
            f"{pct(inicial_cat[(a1, 'Catalán y castellano')])}."
        )
    nota("cálculo propio con la EULP", "2008–2023", EULP_15)
    notas_uso.append("Descomposición del cambio (shift-share, forma simétrica de Kitagawa, 1955, con los valores "
                     "medios de los dos años): composición = Σ (peso final − peso inicial) × (tasa inicial + tasa "
                     "final) / 2; dentro de los grupos = Σ (tasa final − tasa inicial) × (peso inicial + peso "
                     "final) / 2. Las dos partes suman exactamente el cambio total. Los pesos son la población de "
                     "15 años o más por lugar de nacimiento.")
    notas_metodologicas(notas_uso)


# ---------- 3. ¿Quién lo habla? ----------
with tab_quien:
    st.markdown("El catalán según quién sea la persona: por sexo, por edad y por lugar de nacimiento "
                "(EULP, 2008–2023).")
    c_seg, c_ind = st.columns(2)
    tipo = c_seg.radio("Segmentar por", ["Lugar de nacimiento", "Edad", "Sexo"], index=0, horizontal=True)
    disponibles = sorted(lengua_seg[lengua_seg["tipo_segmento"] == tipo]["indicador"].unique())
    indicador = c_ind.selectbox("Indicador", disponibles,
                                index=disponibles.index("Lengua habitual")
                                if "Lengua habitual" in disponibles else 0)
    colores_seg = {"Lugar de nacimiento": COLOR_ORIGEN, "Edad": COLOR_EDAD, "Sexo": COLOR_SEXO}[tipo]

    base = sin_total(lengua_seg[(lengua_seg["tipo_segmento"] == tipo) &
                                (lengua_seg["indicador"] == indicador)]).copy()
    # Una barra por segmento y edición
    base["fila"] = base["segmento"] + " · " + base["año"].astype(str)
    orden_filas = list(base.sort_values(["orden_segmento", "año"])["fila"].drop_duplicates())
    mostrar(grafico_apilado(
        base, "fila", "categoria", "pct", COLOR_LENGUA, orden_categoria=orden_filas,
        titulo_graf=titulo(f"{indicador}, por {tipo.lower()}, 2008–2023",
                           "EULP · % de cada grupo; una barra por edición"),
        eje_valor="% de cada grupo",
        tooltip=[alt.Tooltip("segmento:N", title="Grupo"), alt.Tooltip("año:O", title="Año")]))

    evol = base[base["categoria"] == "Catalán"]
    if tipo == "Edad":
        # Cuatro grupos de edad: un panel por grupo, con la misma escala (como en el censo)
        st.markdown(f"#### {indicador}: catalán, por edad, 2008–2023")
        st.caption("EULP · % de cada grupo de edad con el catalán, un panel por grupo")
        maximo_edad = math.ceil(evol["pct"].max() / 10) * 10
        paneles = st.columns(2) + st.columns(2)
        for panel, (grupo_edad, color_edad) in zip(paneles, COLOR_EDAD.items()):
            mostrar(grafico_lineas(
                evol[evol["segmento"] == grupo_edad], "año", "pct", color_fijo=color_edad,
                dominio=[0, maximo_edad], alto=320, titulo_graf=titulo(grupo_edad),
                tooltip=[alt.Tooltip("año:O", title="Año")]), panel)
    else:
        mostrar(grafico_lineas(
            evol, "año", "pct", serie="segmento", colores=colores_seg,
            titulo_graf=titulo(f"{indicador}: catalán, por {tipo.lower()}, 2008–2023",
                               "EULP · % de cada grupo con el catalán"),
            tooltip=[alt.Tooltip("año:O", title="Año"), alt.Tooltip("segmento:N", title="Grupo")]))
    nota(FUENTE_EULP, "2008–2023", EULP_15)
    notas_metodologicas([
        '"Otras y no consta" agrupa el resto de lenguas y combinaciones de lenguas, y las respuestas sin dato.',
        "Los cruces por sexo, edad y lugar de nacimiento se publican desde 2008. El Idescat no publica la lengua "
        "habitual por edad ni la lengua inicial por sexo, por eso esas combinaciones no aparecen.",
        "En 2008, las categorías de lengua habitual por sexo suman el 103,4% del total publicado (incoherencia de "
        'la fuente, solo en "Otras y no consta").'])


# ---------- 4. ¿Con quién se usa? ----------
with tab_amb:
    st.markdown(
        "Con quién y dónde se habla catalán, según la EULP. Los porcentajes tienen la misma base que en "
        "el Idescat: toda la población de 15 años o más o, en algunos ámbitos (hogar, estudios, trabajo, "
        "clientes, deporte, culto y redes sociales), la población a la que se refiere el ámbito."
    )
    c_ver, c_vista, c_anio = st.columns([2, 1, 1])
    tipo_amb = c_ver.radio("Ver", ["Total", "Por sexo", "Por edad", "Por lugar de nacimiento"],
                           horizontal=True)
    vista = c_vista.radio("Vista", ["Simplificada", "Detallada"], horizontal=True)
    anios_amb = sorted(ambitos_seg["año"].unique())
    anio_amb = c_anio.radio("Año", anios_amb, index=len(anios_amb) - 1, horizontal=True)
    if tipo_amb == "Total":
        datos_amb = ambitos_seg[(ambitos_seg["tipo_segmento"] == "Sexo") &
                                (ambitos_seg["segmento"] == "total")]
        grupo = "total"
    else:
        t = {"Por sexo": "Sexo", "Por edad": "Edad", "Por lugar de nacimiento": "Lugar de nacimiento"}[tipo_amb]
        opciones_seg = list(sin_total(ambitos_seg[ambitos_seg["tipo_segmento"] == t])
                            .sort_values("orden_segmento")["segmento"].unique())
        grupo = st.selectbox("Grupo", opciones_seg)
        datos_amb = ambitos_seg[(ambitos_seg["tipo_segmento"] == t) &
                                (ambitos_seg["segmento"] == grupo)]
    texto_grupo = "Total" if grupo == "total" else grupo

    def por_ambito(anio):
        """Ámbitos de un año con cobertura completa y su % de "solo o más catalán"."""
        u = datos_amb[datos_amb["año"] == anio].dropna(subset=["pct"]).copy()
        # Si faltan categorías por ser dato confidencial, el ámbito no se muestra:
        # las categorías restantes darían una imagen engañosa.
        cobertura = u.groupby("ambito")["pct"].sum()
        u = u[u["ambito"].isin(cobertura[cobertura >= 90].index)]
        catalan = (u[u["categoria"].isin(["Solo catalán", "Más catalán que castellano"])]
                   .groupby("ambito")["pct"].sum())
        return u, catalan

    u, catalan = por_ambito(anio_amb)
    if catalan.empty:
        st.info("No hay datos fiables para este grupo en este año.")
    else:
        mas, menos = catalan.idxmax(), catalan.idxmin()
        c1, c2 = st.columns(2)
        with c1.container(border=True):
            st.markdown(f"**Donde más se usa el catalán ({anio_amb})**  \n{mas}: **{pct(catalan.max())}** "
                        "habla solo o sobre todo en catalán")
        with c2.container(border=True):
            st.markdown(f"**Donde menos se usa ({anio_amb})**  \n{menos}: **{pct(catalan.min())}**")

        if vista == "Simplificada":
            simple = {"Solo catalán": "Solo o más catalán", "Más catalán que castellano": "Solo o más catalán",
                      "Solo castellano": "Solo o más castellano",
                      "Más castellano que catalán": "Solo o más castellano"}
            u["categoria"] = u["categoria"].map(simple).fillna(u["categoria"])
            u = u.groupby(["ambito", "categoria"], as_index=False)["pct"].sum()
            colores_amb = COLOR_USOS_SIMPLE
        else:
            colores_amb = COLOR_USOS
        orden_amb = list(catalan.sort_values(ascending=False).index)
        mostrar(grafico_apilado(
            u, "ambito", "categoria", "pct", colores_amb, orden_categoria=orden_amb,
            leyenda_cols=4 if vista == "Simplificada" else 3,
            titulo_graf=titulo(f"Usos lingüísticos, por ámbito, {anio_amb}",
                               f"EULP · % de la población del ámbito · {texto_grupo} · "
                               "ordenado por % solo o más catalán"),
            eje_valor="% de la población del ámbito",
            tooltip=[alt.Tooltip("ambito:N", title="Ámbito")]))
        nota(FUENTE_EULP, str(anio_amb), "población de 15 años o más o del ámbito",
             "sin los ámbitos con datos confidenciales")

    _, cat_ini = por_ambito(anios_amb[0])
    _, cat_fin = por_ambito(anios_amb[-1])
    comunes = cat_ini.index.intersection(cat_fin.index)
    if len(comunes) == 0:
        st.info("No hay ámbitos con datos fiables en los dos años para este grupo.")
    else:
        ancho = pd.DataFrame({"ambito": comunes, "inicio": cat_ini[comunes].values,
                              "fin": cat_fin[comunes].values})
        orden_pesas = list(ancho.sort_values("fin", ascending=False)["ambito"])
        pesas = ancho.melt(id_vars="ambito", value_vars=["inicio", "fin"], var_name="cual", value_name="pct")
        pesas["año"] = pesas["cual"].map({"inicio": str(anios_amb[0]), "fin": str(anios_amb[-1])})
        pesas["etiqueta"] = pesas["pct"].map(pct)
        menor = pesas.groupby("ambito")["pct"].transform("min")
        pesas["lado"] = "derecha"
        pesas.loc[(pesas["pct"] < pesas.groupby("ambito")["pct"].transform("max")) |
                  ((pesas["pct"] == menor) & (pesas["cual"] == "inicio")), "lado"] = "izquierda"
        colores_anio = {str(anios_amb[0]): GRIS, str(anios_amb[-1]): AZUL}
        eje_y = alt.Y("ambito:N", sort=orden_pesas, axis=EJE_CAT)
        desde = math.floor((pesas["pct"].min() - 6) / 5) * 5
        hasta = math.ceil((pesas["pct"].max() + 6) / 5) * 5
        escala_x = alt.Scale(domain=[max(0, desde), hasta], nice=False)
        eje_x = eje(list(range(max(0, desde), hasta + 1, 5)), True, "% que habla solo o más catalán")
        reglas = alt.Chart(ancho).mark_rule(color="#C9CED6", strokeWidth=3).encode(
            y=eje_y, x=alt.X("inicio:Q", scale=escala_x, axis=eje_x), x2="fin:Q")
        puntos = alt.Chart(pesas).mark_circle(size=140, opacity=1).encode(
            y=eje_y, x=alt.X("pct:Q", scale=escala_x),
            color=alt.Color("año:N", scale=escala(colores_anio), legend=leyenda()),
            tooltip=[alt.Tooltip("ambito:N", title="Ámbito"), alt.Tooltip("año:N", title="Año"),
                     alt.Tooltip("etiqueta:N", title="Valor")])
        izq = alt.Chart(pesas).mark_text(align="right", dx=-10, fontSize=12).encode(
            y=eje_y, x=alt.X("pct:Q", scale=escala_x), text="etiqueta:N",
            color=alt.Color("año:N", scale=escala(colores_anio), legend=None),
        ).transform_filter(alt.datum.lado == "izquierda")
        der = alt.Chart(pesas).mark_text(align="left", dx=10, fontSize=12).encode(
            y=eje_y, x=alt.X("pct:Q", scale=escala_x), text="etiqueta:N",
            color=alt.Color("año:N", scale=escala(colores_anio), legend=None),
        ).transform_filter(alt.datum.lado == "derecha")
        mostrar(alt.layer(reglas, puntos, izq, der).properties(
            height=150 + 38 * len(comunes),
            title=titulo(f"Solo o más catalán, por ámbito, {anios_amb[0]} frente a {anios_amb[-1]}",
                         f"EULP · % de la población del ámbito · {texto_grupo} · "
                         "solo ámbitos con datos en los dos años")))
        nota(FUENTE_EULP, f"{anios_amb[0]} y {anios_amb[-1]}", "población de 15 años o más o del ámbito")
    notas_metodologicas([
        "Base de los porcentajes: la misma que en el Idescat, toda la población de 15 años o más o, en algunos "
        "ámbitos (hogar, estudios, trabajo, clientes, deporte, culto y redes sociales), la población a la que se "
        "refiere el ámbito.",
        "Los ámbitos con datos confidenciales por baja fiabilidad (menos de 20 casos en la muestra) no aparecen: "
        "solo se muestran los que tienen datos para al menos el 90% de las respuestas.",
        '"Otras y no consta" es alto en algunos ámbitos, como las administraciones.',
        '"Solo o más catalán" suma "Solo catalán" y "Más catalán que castellano"; "Solo o más castellano", las '
        "dos categorías equivalentes en castellano.",
        "El gráfico 2008 frente a 2023 solo incluye los ámbitos que existen en las dos ediciones."])


# ---------- 5. Mapa ----------
with tab_mapa:
    if datos_mapa is None:
        st.warning("Faltan los datos del mapa. Ejecuta `python src/preparar_mapa.py` y vuelve a abrir la app.")
    else:
        _, _, eulp_terr, cpnl_amb = datos_mapa
        notas_mapa = []
        st.markdown("Los 8 ámbitos territoriales del Plan territorial general de Cataluña, el nivel en el que el "
                    "Idescat publica la EULP por territorios.")
        capas = ["Uso: lengua habitual, catalán", "Conocimiento: sabe hablar catalán",
                 "Aprendizaje: inscripciones del CPNL por origen", "Aprendizaje: inscripciones totales por ámbito"]
        capa = st.radio("Capa", capas, horizontal=True)
        fuente_mapa = ("Idescat y Departamento de Política Lingüística, EULP 2023 por ámbitos territoriales del Plan territorial general de Cataluña "
                       "(publicado el 27/11/2025); geometría: ICGC, Divisions administratives v2r2 (20/01/2026), "
                       "municipios unidos por ámbito territorial según el Idescat")
        margen = ("La EULP 2023 se diseñó con un error teórico máximo del 5% (95% de confianza) en cada uno de "
                  "sus 16 subámbitos territoriales, frente al 1% del conjunto de Cataluña: las diferencias "
                  "pequeñas entre territorios no son significativas. El Idescat solo publica estos 8 ámbitos territoriales "
                  "para 2023.")
        if capa == capas[0]:
            mostrar(grafico_mapa(
                eulp_terr, "habitual_catalan_pct", color=AZUL, dominio=[0, 80],
                titulo_graf=titulo("Catalán como lengua habitual, por ámbito territorial, 2023",
                                   f"EULP · % de la población de 15 años o más · Cataluña: "
                                   f"{pct(eulp.iloc[-1].lengua_habitual_catalan_pct)}"),
                titulo_leyenda="% con el catalán como lengua habitual",
                tooltip=[("habitual_catalan_miles", "Miles de personas", 1),
                         ("poblacion_15mas_miles", "Población de 15 años o más (miles)", 1)]))
            nota("Idescat y Generalitat, EULP por ámbitos territoriales (2023); geometría, ICGC", None, EULP_15,
                 "error de hasta el 5% por territorio")
            notas_mapa += [fuente_mapa + ".", margen]
        elif capa == capas[1]:
            mostrar(grafico_mapa(
                eulp_terr, "sabe_hablar_pct", color=AZUL, dominio=[50, 100],
                titulo_graf=titulo("Sabe hablar catalán, por ámbito territorial, 2023",
                                   "EULP · % de la población de 15 años o más · Cataluña: 80,4%"),
                titulo_leyenda="% que sabe hablar catalán",
                tooltip=[("sabe_hablar_miles", "Miles de personas", 1)]))
            nota("Idescat y Generalitat, EULP por ámbitos territoriales (2023); geometría, ICGC", None, EULP_15,
                 "error de hasta el 5% por territorio")
            notas_mapa += [fuente_mapa + ".", margen]
        else:
            periodos = list(cpnl_amb["periodo"].drop_duplicates())
            total_periodo = next(p_ for p_ in periodos if "–" in p_)
            periodo_mapa = st.selectbox("Periodo", [total_periodo] + sorted(
                [p_ for p_ in periodos if p_ != total_periodo], reverse=True), key="periodo_mapa")
            datos_p = cpnl_amb[cpnl_amb["periodo"] == periodo_mapa].copy()
            acumuladas = " · inscripciones acumuladas, no personas" if "–" in periodo_mapa else ""
            sin_mun_mapa = cpnl[(cpnl["municipio"] == SIN_MUNICIPIO) &
                                ((cpnl["anio"].astype(str) == periodo_mapa) | ("–" in periodo_mapa))]["total"].sum()
            if capa == capas[2]:
                columnas_origen = {"Cataluña": "pct_cataluna", "Resto de España": "pct_resto_espana",
                                   "Extranjero": "pct_extranjero"}
                titulos_origen = {"Cataluña": "Nacidos en Cataluña",
                                  "Resto de España": "Nacidos en el resto de España",
                                  "Extranjero": "Nacidos en el extranjero"}
                vistas_origen = ["Tres mapas", "Un solo mapa: los tres orígenes",
                                 "Un solo mapa: inscripciones por origen"]
                vista_origen = st.radio("Vista del mapa", vistas_origen, horizontal=True, key="vista_origen")
                if vista_origen == vistas_origen[0]:
                    tope = math.ceil(datos_p[list(columnas_origen.values())].max().max() / 10) * 10
                    st.markdown(f"#### Inscripciones al CPNL por lugar de nacimiento, por ámbito territorial, "
                                f"{periodo_mapa}")
                    st.caption("CPNL · % sobre las inscripciones con origen conocido de cada ámbito territorial · "
                               "misma escala en los tres mapas" + acumuladas)
                    paneles = st.columns(3)
                    for panel, (origen_m, columna) in zip(paneles, columnas_origen.items()):
                        mostrar(grafico_mapa(
                            datos_p, columna, color=COLOR_ORIGEN[origen_m], dominio=[0, tope], alto=460,
                            tamano_texto=10, halo=True, titulo_graf=titulo(titulos_origen[origen_m]),
                            titulo_leyenda="% de las inscripciones",
                            tooltip=[("origen_conocido", "Inscripciones con origen conocido", 0),
                                     ("total", "Inscripciones", 0)]), panel)
                    nota(f"{FUENTE_CPNL} ({periodo_mapa}); geometría, ICGC", None,
                         "inscripciones con origen conocido, no personas")
                elif vista_origen == vistas_origen[1]:
                    # Fondo con escala fija (40–100%) para comparar periodos: el mínimo de todos es 48,1%
                    mostrar(grafico_mapa_origenes(
                        datos_p, columnas_origen, formato=pct, fondo="pct_extranjero", dominio_fondo=[40, 100],
                        color_fondo="#A094C6", titulo_fondo="Fondo: % de nacidos en el extranjero",
                        titulo_graf=titulo(
                            f"Inscripciones al CPNL por lugar de nacimiento, por ámbito territorial, {periodo_mapa}",
                            "CPNL · % sobre las inscripciones con origen conocido · en cada ámbito, de arriba "
                            "abajo: Cataluña, resto de España y extranjero" + acumuladas)))
                    nota(f"{FUENTE_CPNL} ({periodo_mapa}); geometría, ICGC", None,
                         "inscripciones con origen conocido, no personas")
                else:
                    columnas_n = {"Cataluña": "nacidos_cataluna", "Resto de España": "nacidos_resto_espana",
                                  "Extranjero": "nacidos_extranjero"}
                    maximo_total = math.ceil(datos_p["total"].max() / 10_000) * 10_000
                    mostrar(grafico_mapa_origenes(
                        datos_p, columnas_n, formato=miles, fondo="total", dominio_fondo=[0, maximo_total],
                        color_fondo=GRIS, titulo_fondo="Fondo: total de inscripciones",
                        titulo_graf=titulo(
                            f"Inscripciones al CPNL por lugar de nacimiento, por ámbito territorial, {periodo_mapa}",
                            "CPNL · número de inscripciones · en cada ámbito, de arriba abajo: Cataluña, resto "
                            "de España y extranjero" + acumuladas)))
                    nota(f"{FUENTE_CPNL} ({periodo_mapa}); geometría, ICGC", None, "inscripciones, no personas",
                         "las tres cifras no incluyen las inscripciones sin origen")

                # Barras al 100% por ámbito territorial, ordenadas por % de nacidos en el extranjero
                barras_amb = datos_p.melt(id_vars=["ambito"], value_vars=list(columnas_origen.values()),
                                          var_name="columna", value_name="pct")
                barras_amb["origen"] = barras_amb["columna"].map({v: k for k, v in columnas_origen.items()})
                orden_amb = list(datos_p.sort_values("pct_extranjero", ascending=False)["ambito"])
                mostrar(grafico_apilado(
                    barras_amb, "ambito", "origen", "pct", COLOR_ORIGEN, orden_categoria=orden_amb,
                    dominio=[0, 118], totales={r.ambito: miles(r.total) for r in datos_p.itertuples()},
                    titulo_graf=titulo(f"Inscripciones por lugar de nacimiento, por ámbito territorial, {periodo_mapa}",
                                       "CPNL · % sobre las inscripciones con origen conocido; a la derecha, total "
                                       "de inscripciones · ordenado por % de nacidos en el extranjero"),
                    eje_valor="% de las inscripciones con origen conocido",
                    tooltip=[alt.Tooltip("ambito:N", title="Ámbito territorial")]))
                nota(FUENTE_CPNL, periodo_mapa, "inscripciones, no personas")
            else:
                maximo_total = math.ceil(datos_p["total"].max() / 10_000) * 10_000
                mostrar(grafico_mapa(
                    datos_p, "total", color=AZUL, dominio=[0, maximo_total], formato=miles,
                    titulo_graf=titulo(f"Inscripciones al CPNL, por ámbito territorial, {periodo_mapa}",
                                       "CPNL · número de inscripciones" + acumuladas),
                    titulo_leyenda="Inscripciones",
                    tooltip=[("origen_conocido", "Inscripciones con origen conocido", 0)]))
                nota(f"{FUENTE_CPNL} ({periodo_mapa}); geometría, ICGC", None, "inscripciones, no personas")
            notas_mapa += [
                "Cada inscripción se asigna a su ámbito territorial por el código de municipio, con la "
                "correspondencia oficial municipio → ámbito territorial del Idescat.",
                f"El mapa excluye las inscripciones sin municipio catalán asignado: {miles(sin_mun_mapa)} en "
                f"{periodo_mapa}.",
                "Geometría: ICGC, Divisions administratives (20/01/2026), municipios unidos por ámbito territorial."]
        notas_metodologicas(notas_mapa)


# ---------- 6. Aprendizaje (CPNL) ----------
with tab_apr:
    if es_muestra:
        st.warning("Estás viendo una muestra de 6 municipios. Para ver toda Cataluña, ejecuta "
                   "`python src/preparar_datos.py` y vuelve a abrir la app.")
    notas_apr = []
    col_n, col_v, col_p = st.columns([1, 1, 1])
    niveles_geo = ["Total CPNL", "Provincia", "Municipio"]
    nivel = col_n.radio("Nivel", niveles_geo, horizontal=True, index=2 if es_muestra else 0,
                        help="Total CPNL incluye las inscripciones sin municipio catalán asignado.")
    if nivel == "Total CPNL":
        ambito, datos = "Total CPNL", cpnl
    elif nivel == "Provincia":
        provincias = sorted(cpnl["provincia"].dropna().unique())
        ambito = col_v.selectbox("Provincia", provincias)
        datos = cpnl[cpnl["provincia"] == ambito]
    else:
        municipios = sorted(cpnl["municipio"].unique())
        inicio = municipios.index("Barcelona") if "Barcelona" in municipios else 0
        ambito = col_v.selectbox("Municipio", municipios, index=inicio)
        datos = cpnl[cpnl["municipio"] == ambito]
    anios_cpnl = sorted(cpnl["anio"].unique())
    rango_cpnl = f"{anios_cpnl[0]}–{anios_cpnl[-1]}"
    periodo = col_p.selectbox("Periodo", [f"Total {rango_cpnl}"] + [str(a_) for a_ in reversed(anios_cpnl)])
    es_total = periodo.startswith("Total")
    texto_periodo = rango_cpnl if es_total else periodo
    nota_periodo = "Inscripciones acumuladas, no personas" if es_total else "Inscripciones, no personas"

    def en_periodo(df):
        return df if es_total else df[df["anio"] == int(periodo)]

    anual = datos.groupby("anio", as_index=False).sum(numeric_only=True)
    anual["pct_extranjero"] = anual["nacidos_extranjero"] / anual["origen_conocido"] * 100
    primero, ultimo = anual.iloc[0], anual.iloc[-1]

    c1, c2, c3 = st.columns(3)
    # Referencia: el año con menos inscripciones antes de la COVID-19 (2011–2019)
    previos = anual[(anual["anio"] < 2020) & (anual["total"] > 0)]
    if previos.empty:
        referencia, texto_ref = primero, f"vs {int(primero.anio)}"
    else:
        referencia = previos.loc[previos["total"].idxmin()]
        texto_ref = f"vs {int(referencia.anio)}, mínimo antes de la COVID-19"
    c1.metric(f"Inscripciones {int(ultimo.anio)} ({ambito})", miles(ultimo.total),
              f"{num((ultimo.total / referencia.total - 1) * 100, 0, signo=True)}% {texto_ref}"
              if referencia.total else None, delta_color="off")
    c2.metric(f"Nacidos en el extranjero {int(ultimo.anio)}", pct(ultimo.pct_extranjero),
              f"{num(ultimo.pct_extranjero - primero.pct_extranjero, signo=True)} pp vs {int(primero.anio)}",
              delta_color="off")
    c3.metric(f"Nacidos en Cataluña {int(ultimo.anio)}", miles(ultimo.nacidos_cataluna),
              f"{num((ultimo.nacidos_cataluna / primero.nacidos_cataluna - 1) * 100, signo=True)}% "
              f"vs {int(primero.anio)}" if primero.nacidos_cataluna else None, delta_color="off")

    niveles = anual.melt(id_vars="anio",
                         value_vars=["nivel_inicial_basico1", "nivel_basico23_elemental",
                                     "nivel_intermedio_suficiencia"],
                         var_name="nivel", value_name="inscripciones")
    niveles["nivel"] = niveles["nivel"].map(ETIQUETAS)
    mostrar(grafico_apilado(
        niveles, "anio", "nivel", "inscripciones", COLOR_NIVEL, horizontal=False, formato=miles,
        totales={r.anio: miles(r.total) for r in anual.itertuples()},
        titulo_graf=titulo(f"Inscripciones por nivel ({ambito}), {rango_cpnl}",
                           "CPNL · inscripciones, no personas; encima, el total del año"),
        tooltip=[alt.Tooltip("anio:O", title="Año")]))
    pct_sin_mun = cpnl.loc[cpnl["municipio"] == SIN_MUNICIPIO, "total"].sum() / cpnl["total"].sum() * 100
    nota_sin_mun = (f" El Total CPNL incluye un {pct(pct_sin_mun)} de inscripciones sin municipio catalán "
                    f"asignado ({rango_cpnl}; ver Calidad de datos)." if nivel == "Total CPNL" else "")
    nota(FUENTE_CPNL, rango_cpnl, "inscripciones, no personas", "2020: caída por la COVID-19")
    notas_apr.append("Una persona puede inscribirse más de una vez al año: los datos cuentan inscripciones, "
                     "no personas." + nota_sin_mun)

    nombres_origen = {"nacidos_cataluna": "Cataluña", "nacidos_resto_espana": "Resto de España",
                      "nacidos_extranjero": "Extranjero", "sin_datos_origen": "Sin datos de origen"}
    todos = anual.melt(id_vars="anio", value_vars=list(nombres_origen),
                       var_name="origen", value_name="inscripciones")
    todos["origen"] = todos["origen"].map(nombres_origen)
    mostrar(grafico_apilado(
        todos, "anio", "origen", "inscripciones", {**COLOR_ORIGEN, "Sin datos de origen": GRIS},
        horizontal=False, formato=miles, minimo_etiqueta=8,
        totales={r.anio: miles(r.total) for r in anual.itertuples()},
        titulo_graf=titulo(f"Inscripciones por lugar de nacimiento ({ambito}), {rango_cpnl}",
                           "CPNL · inscripciones, no personas; encima, el total del año (el mismo que por nivel)"),
        tooltip=[alt.Tooltip("anio:O", title="Año")]))
    sin_datos = anual.set_index("anio")
    sin_datos = (sin_datos["sin_datos_origen"] / sin_datos["total"] * 100).loc[2020:2022]
    nota(FUENTE_CPNL, rango_cpnl, "inscripciones, no personas", "2020–2022: muchas inscripciones sin datos de origen")
    if not sin_datos.empty and sin_datos.notna().any():
        notas_apr.append(f'En 2020–2022 se dispara "Sin datos de origen" (hasta el {pct(sin_datos.max())} en '
                         f"{int(sin_datos.idxmax())}): por eso los porcentajes por origen se calculan solo sobre "
                         "las inscripciones con origen conocido.")
    notas_apr.append("En los gráficos por origen, los segmentos pequeños (menos del 8% de su barra en el absoluto, "
                     "menos del 5% en el de composición, o sin altura para el texto) muestran su valor en el tooltip.")

    origenes = todos[todos["origen"] != "Sin datos de origen"].copy()

    origenes["pct"] = origenes["inscripciones"] / origenes.groupby("anio")["inscripciones"].transform("sum") * 100
    mostrar(grafico_apilado(
        origenes, "anio", "origen", "pct", COLOR_ORIGEN, horizontal=False, dominio=[0, 100],
        minimo_etiqueta=5,
        titulo_graf=titulo(f"Composición por lugar de nacimiento ({ambito}), {rango_cpnl}",
                           "CPNL · % sobre las inscripciones con origen conocido"),
        tooltip=[alt.Tooltip("anio:O", title="Año")]))
    nota(FUENTE_CPNL, rango_cpnl, "inscripciones con origen conocido, no personas")

    regiones = {"america_sur_central": "América del Sur y Central", "ue": "Unión Europea",
                "asia": "Asia", "norte_africa": "Norte de África", "resto_europa": "Resto de Europa",
                "resto_africa": "Resto de África", "resto_mundo": "Resto del mundo"}
    reg = en_periodo(datos)[list(regiones)].sum().rename(regiones).reset_index()
    reg.columns = ["region", "inscripciones"]
    mostrar(grafico_barras(
        reg, "region", "inscripciones", color=COLOR_ORIGEN["Extranjero"], formato=miles,
        titulo_graf=titulo(f"Nacidos en el extranjero, por región ({ambito}), {texto_periodo}",
                           f"CPNL · {nota_periodo.lower()}"),
        tooltip=[alt.Tooltip("region:N", title="Región")]))
    nota(FUENTE_CPNL, texto_periodo, "inscripciones de nacidos en el extranjero, no personas")

    if nivel == "Total CPNL":
        prov = en_periodo(cpnl).groupby("provincia", as_index=False).sum(numeric_only=True)
        prov["pct_extranjero"] = prov["nacidos_extranjero"] / prov["origen_conocido"] * 100
        orden_prov = list(prov.sort_values("total", ascending=False)["provincia"])
        col_p1, col_p2 = st.columns(2)
        mostrar(grafico_barras(
            prov, "provincia", "total", color=AZUL, formato=miles, orden=orden_prov,
            titulo_graf=titulo(f"Inscripciones, por provincia, {texto_periodo}", f"CPNL · {nota_periodo.lower()}"),
            tooltip=[alt.Tooltip("provincia:N", title="Provincia")]), col_p1)
        mostrar(grafico_barras(
            prov, "provincia", "pct_extranjero", color=COLOR_ORIGEN["Extranjero"], dominio=[0, 118],
            orden=orden_prov,
            titulo_graf=titulo(f"% nacidos en el extranjero, por provincia, {texto_periodo}",
                               "CPNL · % sobre las inscripciones con origen conocido"),
            tooltip=[alt.Tooltip("provincia:N", title="Provincia")]), col_p2)
        nota(FUENTE_CPNL, texto_periodo, "inscripciones, no personas")
        notas_apr.append("Por provincia: las dos gráficas siguen el mismo orden, de más a menos inscripciones, y "
                         "no incluyen las inscripciones sin municipio catalán asignado.")

        st.subheader(f"Municipios con más inscripciones, {texto_periodo}")
        top = (en_periodo(cpnl).groupby(["municipio", "provincia"], as_index=False)
               [["total", "nacidos_extranjero", "origen_conocido", "sin_datos_origen"]].sum()
               .nlargest(10, "total"))
        top["pct_extranjero"] = (top["nacidos_extranjero"] / top["origen_conocido"] * 100).map(pct)
        for columna in ["total", "nacidos_extranjero", "sin_datos_origen"]:
            top[columna] = top[columna].map(miles)
        top = en_espanol(top[["municipio", "provincia", "total", "nacidos_extranjero", "pct_extranjero",
                              "sin_datos_origen"]])
        tabla(top, numericas=[c for c in top.columns if c not in ("Municipio", "Provincia")])
        nota(FUENTE_CPNL, texto_periodo, "inscripciones, no personas")
        notas_apr.append("Tabla de municipios: el % de nacidos en el extranjero se calcula sobre las inscripciones "
                         "con origen conocido.")

    with st.expander("Ver datos anuales"):
        st.dataframe(en_espanol(anual.drop(columns=[c for c in anual.columns if c.startswith("dif_")])),
                     hide_index=True, width="stretch")
    notas_metodologicas(notas_apr)


# ---------- 7. Calidad de datos ----------
with tab_cal:
    # La tabla de fuentes se lee de docs/fuentes_resumen.md para que app, README y documentos coincidan
    resumen_fuentes = (RAIZ / "docs" / "fuentes_resumen.md").read_text(encoding="utf-8")
    inicio_fuentes = resumen_fuentes.index("## Fuentes, enlaces y tamaño")
    fin_fuentes = resumen_fuentes.index("\n## ", inicio_fuentes + 3)
    st.markdown(resumen_fuentes[inicio_fuentes:fin_fuentes].replace(
        "está en los apartados siguientes", "está en `docs/fuentes_resumen.md`, en el repositorio"))
    st.markdown((RAIZ / "docs" / "calidad_datos.md").read_text(encoding="utf-8"))

    st.subheader("Controles automáticos por año")
    st.caption("Número de filas en las que el total no coincide con la suma de sus partes.")
    control = en_espanol(validacion)
    tabla(control, numericas=list(control.columns))
    st.caption('"Filas": municipios y una fila anual sin municipio catalán · menos filas desde 2022 '
               "(incidencia 30) · descuadres explicados en la incidencia 31")

    st.subheader("Correcciones aplicadas")
    filas_cambios = []
    for c in cambios[cambios["tipo"] == "codigo corregido"].itertuples():
        filas_cambios.append({"Corrección": "Código corregido", "Municipio": c.municipio, "Años": c.anio,
                              "Detalle": f"{c.antes} → {c.despues}",
                              "Motivo": "El municipio aparecía con el código de otro; se usa su código "
                                        "más frecuente en la serie."})
    sumadas = cambios[cambios["tipo"] == "duplicado sumado"]
    if not sumadas.empty:
        filas_cambios.append({
            "Corrección": "Filas sumadas", "Municipio": f"{SIN_MUNICIPIO} (código 000000)",
            "Años": f"{sumadas['anio'].min()}–{sumadas['anio'].max()} ({len(sumadas)} años)",
            "Detalle": "Una fila por año",
            "Motivo": 'La fuente usa el mismo código 000000 para "sense dades" (sin datos) y para '
                      "Catalunya Nord, la Franja, Illes Balears, País Valencià y el resto del Estado. "
                      "Al compartir código, la limpieza las suma en una sola fila por año."})
    tabla(pd.DataFrame(filas_cambios))
    st.caption(f"Datos del CPNL procesados el {meta['procesado'].replace('T', ' a las ')} "
               f"({'muestra' if es_muestra else 'dataset completo'}).")
