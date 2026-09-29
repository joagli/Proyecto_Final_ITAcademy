"""
capturas.py
-----------
Abre la app en ejecución, hace clic en cada pestaña y guarda una captura de
página completa por pestaña en docs/capturas/. Sirve para revisar la app tal
como se ve en el navegador (títulos, etiquetas, tablas).

Con las capturas genera además el PDF del dashboard (todas las pestañas, con los
resultados de la hipótesis visibles y todas las capas y vistas del mapa), en páginas A4.

Requisitos (solo desarrollo):
    pip install -r requirements-dev.txt
    python -m playwright install chromium

Uso (con la app ya abierta en otra terminal: streamlit run app.py):
    python src/capturas.py                          # http://localhost:8501
    python src/capturas.py --url http://localhost:8502 --ancho 1280
    python src/capturas.py --sin-pdf                # solo las capturas

Además de la vista por defecto, guarda algunas variantes (ver VARIANTES).
"""

import argparse
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np
from PIL import Image
from playwright.sync_api import Error as ErrorPlaywright
from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parents[1]
CARPETA = RAIZ / "docs" / "capturas"
RUTA_PDF = RAIZ / "entregables" / "03_dashboard" / "dashboard.pdf"
TITULO_PDF = '¿Se está "apagando" el catalán? Lo que se dice y lo que dicen los datos'
AUTOR = "Jorge Aguilar Liévanos"

# Capturas adicionales por pestaña: (texto del control en el que se hace clic, sufijo del archivo).
# Después de cada variante se vuelve a la opción por defecto (el último elemento, sin sufijo).
VARIANTES = {
    "La hipótesis": [("Mostrar resultados", "con resultados"), ("Mostrar resultados", None)],
    "¿Quién lo habla?": [("Edad", "edad"), ("Sexo", "sexo"), ("Lugar de nacimiento", None)],
    "¿Con quién se usa?": [("Detallada", "vista detallada"), ("Simplificada", None)],
    "Mapa": [("Conocimiento: sabe hablar catalán", "conocimiento"),
             ("Aprendizaje: inscripciones del CPNL por origen", "aprendizaje"),
             ("Un solo mapa: los tres orígenes", "aprendizaje un mapa"),
             ("Un solo mapa: inscripciones por origen", "aprendizaje un mapa inscripciones"),
             ("Tres mapas", None),
             ("Aprendizaje: inscripciones totales por ámbito", "totales"),
             ("Uso: lengua habitual, catalán", None)],
}

# Qué capturas van al PDF, en orden. La hipótesis va con los resultados visibles.
PAGINAS_PDF = ["la_hipotesis_con_resultados", "conocimiento", "uso", "quien_lo_habla", "con_quien_se_usa",
               "mapa", "mapa_conocimiento", "mapa_aprendizaje", "mapa_aprendizaje_un_mapa",
               "mapa_aprendizaje_un_mapa_inscripciones", "mapa_totales", "aprendizaje_cpnl", "calidad_de_datos"]


def nombre_archivo(indice: int, texto: str) -> str:
    """Convierte el nombre de una pestaña en el de su archivo: "¿Quién lo habla?" -> "04_quien_lo_habla.png"."""
    sin_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    limpio = re.sub(r"[^a-z0-9]+", "_", sin_acentos.lower()).strip("_")
    return f"{indice:02d}_{limpio}.png"


def esperar_graficos(pagina) -> None:
    """Espera a que todos los gráficos visibles estén dibujados."""
    pagina.wait_for_function(
        """() => {
            const graficos = [...document.querySelectorAll('[data-testid="stVegaLiteChart"]')]
                .filter(g => g.offsetParent !== null);
            return graficos.every(g => {
                const lienzo = g.querySelector('canvas, svg');
                return lienzo && lienzo.getBoundingClientRect().height > 0;
            });
        }""",
        timeout=30_000,
    )
    pagina.wait_for_timeout(1_500)  # margen para animaciones y fuentes


def captura_completa(pagina, ruta: Path, ancho: int) -> None:
    """Streamlit desplaza el contenido dentro de un contenedor, no en la página:
    se agranda la ventana hasta la altura del contenido para capturarlo entero."""
    alto = pagina.evaluate(
        """() => Math.max(...['[data-testid="stMain"]', '[data-testid="stAppViewContainer"]',
                              'section.main', 'body']
            .map(s => document.querySelector(s))
            .filter(Boolean)
            .map(e => e.scrollHeight))"""
    )
    pagina.set_viewport_size({"width": ancho, "height": int(alto) + 40})
    esperar_graficos(pagina)
    pagina.screenshot(path=str(ruta), full_page=True)
    pagina.set_viewport_size({"width": ancho, "height": 900})


def cortes_de_pagina(imagen: Image.Image, alto_pagina: int) -> list[int]:
    """Posiciones donde cortar una captura larga: filas en blanco cerca del final de cada
    página, para no partir un gráfico por la mitad."""
    gris = np.asarray(imagen.convert("L"))
    en_blanco = (gris >= 250).all(axis=1)
    alto, cortes, inicio = gris.shape[0], [], 0
    while alto - inicio > alto_pagina:
        limite = inicio + alto_pagina
        candidatas = np.flatnonzero(en_blanco[inicio + int(alto_pagina * 0.55):limite])
        corte = inicio + int(alto_pagina * 0.55) + int(candidatas[-1]) if candidatas.size else limite
        cortes.append(corte)
        inicio = corte
    return cortes + [alto]


def generar_pdf(capturas: dict[str, Path], ruta_pdf: Path) -> None:
    """Une las capturas en un PDF de páginas A4 verticales."""
    paginas = []
    for clave in PAGINAS_PDF:
        if clave not in capturas:
            print(f'Aviso: falta la captura "{clave}"; no entra en el PDF.')
            continue
        imagen = Image.open(capturas[clave]).convert("RGB")
        ancho = imagen.width
        alto_pagina = round(ancho * 297 / 210)
        inicio = 0
        for corte in cortes_de_pagina(imagen, alto_pagina):
            pagina = Image.new("RGB", (ancho, alto_pagina), "white")
            pagina.paste(imagen.crop((0, inicio, ancho, corte)), (0, 0))
            paginas.append(pagina)
            inicio = corte
    if not paginas:
        return
    ruta_pdf.parent.mkdir(parents=True, exist_ok=True)
    resolucion = paginas[0].width / 8.27     # que el ancho de la captura ocupe el ancho de un A4
    paginas[0].save(ruta_pdf, save_all=True, append_images=paginas[1:], resolution=resolucion,
                    title=TITULO_PDF, author=AUTOR, subject="Dashboard · Proyecto final · Data Analytics · IT Academy")
    print(f"PDF: {ruta_pdf.relative_to(RAIZ)} ({len(paginas)} páginas)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Captura cada pestaña de la app y genera el PDF del dashboard.")
    parser.add_argument("--url", default="http://localhost:8501")
    parser.add_argument("--ancho", type=int, default=1440, help="ancho de la ventana en píxeles")
    parser.add_argument("--sin-pdf", action="store_true", help="no generar el PDF")
    args = parser.parse_args()

    CARPETA.mkdir(parents=True, exist_ok=True)
    capturas: dict[str, Path] = {}
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        pagina = navegador.new_page(viewport={"width": args.ancho, "height": 900})
        try:
            pagina.goto(args.url, wait_until="domcontentloaded", timeout=60_000)
            pagina.wait_for_selector('[role="tab"]', timeout=60_000)
        except ErrorPlaywright:
            sys.exit(f"No se pudo abrir {args.url}. ¿Está la app en marcha (streamlit run app.py)?")

        def guardar(indice: int, texto: str) -> None:
            ruta = CARPETA / nombre_archivo(indice, texto)
            captura_completa(pagina, ruta, args.ancho)
            capturas[ruta.stem[3:]] = ruta
            print(f"Guardada: {ruta.relative_to(RAIZ)}")

        pestanas = pagina.locator('[role="tab"]')
        textos = [t.strip() for t in pestanas.all_inner_texts()]
        for i, texto in enumerate(textos, start=1):
            pestanas.nth(i - 1).click()
            esperar_graficos(pagina)
            guardar(i, texto)
            for control, sufijo in VARIANTES.get(texto, []):
                panel = pagina.locator('[role="tabpanel"]:visible')
                panel.get_by_text(control, exact=True).first.click()
                pagina.wait_for_timeout(1_500)
                esperar_graficos(pagina)
                if sufijo:
                    guardar(i, f"{texto} {sufijo}")
        navegador.close()

    if not args.sin_pdf:
        generar_pdf(capturas, RUTA_PDF)


if __name__ == "__main__":
    main()
