# ¿Se está "apagando" el catalán?

**Conocimiento, uso y aprendizaje del catalán en Cataluña con datos oficiales (1986–2023)**

Autor: Jorge Aguilar Liévanos · Proyecto final del Sprint 13, Especialización en Data Analytics de IT Academy (Barcelona Activa).

**Pregunta de investigación:** ¿se está "apagando" el catalán, como se oye a menudo? Se pone a prueba con cuatro hipótesis (cada vez menos personas lo saben, los jóvenes ya no lo saben, casi nadie lo aprende y cada vez menos personas lo usan).

**Conclusión:** no se apaga, se transforma: cada vez más personas lo saben, se sigue aprendiendo y sus hablantes habituales se mantienen en unos 2,2 millones; su peso baja en una población mayor, sobre todo porque más personas combinan catalán y castellano.

## Entregables

| Carpeta | Contenido |
|---|---|
| [`entregables/01_informe/`](entregables/01_informe/) | Artículo final: `articulo.pdf` (4 páginas, estilo artículo científico, APA) y `articulo.docx` |
| [`entregables/02_datos/`](entregables/02_datos/) | Datasets procesados y oficiales, con `diccionario_datos.md` |
| [`entregables/03_dashboard/`](entregables/03_dashboard/) | `dashboard.pdf`: todas las pestañas de la app. El dashboard se hizo en Streamlit en lugar de Power BI, con el acuerdo de la mentora |
| [`entregables/04_presentacion/`](entregables/04_presentacion/) | Presentación de la defensa: `presentacion.pptx` (20 diapositivas) y `presentacion.pdf` |

## Estructura del repositorio

```
Proyecto_Final_ITAcademy/
├── README.md
├── app.py                        App en Streamlit (8 pestañas)
├── requirements.txt              Dependencias de la app
├── requirements-dev.txt          Solo desarrollo: mapa (shapely) y capturas (Playwright)
├── .streamlit/config.toml        Tema de la app
├── src/
│   ├── preparar_datos.py         Descarga, limpieza y validación del dataset del CPNL
│   ├── preparar_eulp.py          Limpieza de las tablas de la EULP (Idescat)
│   ├── preparar_mapa.py          Geometría de los 8 ámbitos territoriales y datos por ámbito (pestaña Mapa)
│   ├── preparar_entrega.py       Copia los datos a entregables/02_datos/ y genera el diccionario
│   └── capturas.py               Capturas de cada pestaña y entregables/03_dashboard/dashboard.pdf
├── datos/
│   ├── originales/               Descargas oficiales sin tocar (CPNL, EULP, ICGC y códigos del Idescat)
│   ├── fuentes_oficiales/        Tablas oficiales pequeñas (censos, ECEPOV-2021 y serie de la EULP), con su fuente
│   ├── muestra/                  Extracto real del CPNL (6 municipios) para preparar los datos sin internet
│   └── procesados/               Datos limpios que usa la app (cpnl_*: preparar_datos.py; eulp_*: preparar_eulp.py;
│                                 mapa y datos por ámbito: preparar_mapa.py)
├── docs/
│   ├── metodologia.md            Tipo de estudio, fuentes, modelo de datos y limitaciones
│   ├── fuentes_resumen.md        Una ficha por fuente: organismo, universo, tamaño y qué no mide
│   ├── calidad_datos.md          Incidencias de las fuentes y decisiones tomadas
│   ├── calculos.md               Fórmula y base de cada indicador calculado (equivalente al documento de fórmulas DAX)
│   └── siguientes_pasos.md       Líneas de investigación futura, como hipótesis
└── entregables/                  01_informe, 02_datos, 03_dashboard y 04_presentacion
```

## Cómo ejecutar la app

Con Python 3 instalado (probado en Mac con Python 3.14), desde la carpeta del proyecto:

```bash
python3 -m venv .venv                # 1. entorno virtual (solo la primera vez)
source .venv/bin/activate            # 2. activarlo (en cada terminal nueva)
pip install -r requirements.txt      # 3. dependencias (solo la primera vez)
streamlit run app.py                 # 4. abre la app en http://localhost:8501
```

Los datos ya preparados están en `datos/procesados/`, así que la app funciona sin internet. La app vive mientras esa terminal esté abierta: si el navegador dice que no puede conectar, vuelve a ejecutar el paso 4.

Para regenerar los datos desde las fuentes oficiales:

```bash
python src/preparar_datos.py         # descarga y limpia los datos del CPNL (sin internet: --muestra)
python src/preparar_eulp.py          # limpia las tablas de la EULP (Idescat)
pip install -r requirements-dev.txt  # solo desarrollo
python src/preparar_mapa.py          # descarga ICGC e Idescat, une los municipios por ámbito territorial y comprueba la EULP
python src/preparar_entrega.py       # datos y diccionario en entregables/02_datos/
```

Para regenerar `dashboard.pdf`, con la app abierta en otra terminal:

```bash
python -m playwright install chromium
python src/capturas.py               # capturas en docs/capturas/ (no se suben) y PDF en entregables/03_dashboard/
```

## Fuentes y enlaces

Todas las fuentes son oficiales y públicas. Una fila por fuente; las dos últimas son tablas auxiliares para el mapa, no datos sobre la lengua. El detalle de cada fuente, con sus citas, está en [`docs/fuentes_resumen.md`](docs/fuentes_resumen.md).

| Fuente | Organismo | Periodicidad | Años | Universo | Tamaño de cada edición | URL de descarga |
|---|---|---|---|---|---|---|
| Censos lingüísticos | Idescat | Decenal (censos), con padrones en 1986 y 1996 | 1986, 1991, 1996, 2001, 2011 | Población de 2 años o más | Población: 1986: 5.835.954 · 1991: 5.949.177 · 1996: 5.984.334 · 2001: 6.176.751 · 2011: 7.306.072 (2011: muestra de cerca del 9% de la población) | <https://govern.cat/govern/docs/2013/11/21/10/04/983677eb-2b2a-43ae-8793-9b22bd2a6cb4.pdf> |
| ECEPOV-2021 | INE; resultados de Cataluña: Idescat | Asociada al Censo 2021 | 2021 | Población de 2 años o más (personas en viviendas familiares principales) | España: 172.444 viviendas efectivas (309.348 teóricas); Cataluña: no publicada | <https://www.idescat.cat/indicadors/?id=basics&n=10363> |
| EULP | Idescat y Departamento de Política Lingüística (Generalitat) | Quinquenal | 2003–2023 (cruces: 2008–2023) | Población de 15 años o más | Muestra efectiva: 2003: 7.257 · 2008: 7.140 · 2013: 7.255 · 2018: 8.780 · 2023: 8.682 | Tablas: <https://www.idescat.cat/pub/?id=eulp> · Datos enlazados: <https://www.idescat.cat/pub/?id=eulp&n=7218> |
| EULP por ámbitos territoriales | Idescat y Departamento de Política Lingüística (Generalitat) | Solo 2023 | 2023 | Población de 15 años o más | Muestra de 2023 (8.682), con un mínimo teórico de 450 personas en cada uno de los 16 subámbitos territoriales | <https://www.idescat.cat/pub/?id=eulp&n=3202&geo=at&f=ssv> (también n=3170 y n=20833) |
| Inscripciones del CPNL | Consorci per a la Normalització Lingüística (Dades obertes de Catalunya) | Datos anuales; actualización bienal | 2011–2023 | Inscripciones (no personas) | Inscripciones: 2011: 105.605 · 2012: 95.248 · 2013: 74.345 · 2014: 62.336 · 2015: 65.194 · 2016: 68.352 · 2017: 71.040 · 2018: 75.112 · 2019: 85.185 · 2020: 51.705 · 2021: 72.411 · 2022: 89.212 · 2023: 97.244 (total: 1.012.989) | <https://analisi.transparenciacatalunya.cat/api/v3/views/q9ct-fkjt/export.csv?accessType=DOWNLOAD> |
| Divisions administratives (auxiliar) | ICGC | Actualización periódica; versión del 20/01/2026 | 2026 | Municipios de Cataluña | 947 municipios (escala 1:1.000.000) | <https://datacloud.icgc.cat/datacloud/divisions-administratives/json_unzip/divisions-administratives-v2r2-municipis-1000000-20260120.json> |
| Códigos territoriales (auxiliar) | Idescat | Tabla vigente, descargada en septiembre de 2026 | 2026 | Municipios de Cataluña | 947 municipios, 43 comarcas y 8 ámbitos territoriales | <https://www.idescat.cat/codis/?id=50&n=9&f=ssv> · <https://www.idescat.cat/codis/?id=50&n=28&f=ssv> |

Páginas de referencia de cada fuente (las mismas del anexo de la presentación):

- Uso: Encuesta de usos lingüísticos de la población (EULP), Idescat y Generalitat: <https://www.idescat.cat/pub/?id=eulp>
- Uso por ámbito territorial (EULP 2023), Idescat: <https://www.idescat.cat/novetats/?id=5382>
- Conocimiento: censos y ECEPOV-2021, Idescat: <https://www.idescat.cat/indicadors/?id=basics&n=10363>
- Censo lingüístico 2011 (nota de prensa), Idescat: <https://govern.cat/govern/docs/2013/11/21/10/04/983677eb-2b2a-43ae-8793-9b22bd2a6cb4.pdf>
- ECEPOV-2021, informe metodológico, INE: <https://www.ine.es/dynt3/metadatos/es/RespuestaPrint.html?oper=448>
- Aprendizaje: inscripciones al CPNL, Dades obertes de Catalunya: <https://analisi.transparenciacatalunya.cat/d/q9ct-fkjt>
- Mapa: divisiones administrativas, ICGC: <https://www.icgc.cat/ca/Geoinformacio-i-mapes/Dades-i-productes/Geoinformacio-cartografica/Divisions-administratives>
- Código, datos y dashboard: <https://github.com/joagli/Proyecto_Final_ITAcademy>
