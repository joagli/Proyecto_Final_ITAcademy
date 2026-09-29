# Resumen de las fuentes

Las tres fuentes son independientes: miden cosas distintas, sobre universos distintos y con unidades distintas (personas de 2 años o más, personas de 15 años o más e inscripciones). Por eso no se unen entre sí; el año es solo el eje de lectura común.

Todas las cifras salen de documentación oficial, citada en cada tabla. Lo que no he podido comprobar en una fuente oficial figura como "pendiente de verificar".

## Fuentes, enlaces y tamaño

Una fila por fuente. Las dos últimas son tablas auxiliares para el mapa, no datos sobre la lengua. El detalle de cada fuente, con sus citas, está en los apartados siguientes.

| Fuente | Organismo | Periodicidad | Años | Universo | Tamaño de cada edición | URL de descarga |
|---|---|---|---|---|---|---|
| Censos lingüísticos | Idescat | Decenal (censos), con padrones en 1986 y 1996 | 1986, 1991, 1996, 2001, 2011 | Población de 2 años o más | Población: 1986: 5.835.954 · 1991: 5.949.177 · 1996: 5.984.334 · 2001: 6.176.751 · 2011: 7.306.072 (2011: muestra de cerca del 9% de la población) | <https://govern.cat/govern/docs/2013/11/21/10/04/983677eb-2b2a-43ae-8793-9b22bd2a6cb4.pdf> |
| ECEPOV-2021 | INE; resultados de Cataluña: Idescat | Asociada al Censo 2021 | 2021 | Población de 2 años o más (personas en viviendas familiares principales) | España: 172.444 viviendas efectivas (309.348 teóricas); Cataluña: no publicada | <https://www.idescat.cat/indicadors/?id=basics&n=10363> |
| EULP | Idescat y Departamento de Política Lingüística (Generalitat) | Quinquenal | 2003–2023 (cruces: 2008–2023) | Población de 15 años o más | Muestra efectiva: 2003: 7.257 · 2008: 7.140 · 2013: 7.255 · 2018: 8.780 · 2023: 8.682 | Tablas: <https://www.idescat.cat/pub/?id=eulp> · Datos enlazados: <https://www.idescat.cat/pub/?id=eulp&n=7218> |
| EULP por ámbitos territoriales | Idescat y Departamento de Política Lingüística (Generalitat) | Solo 2023 | 2023 | Población de 15 años o más | Muestra de 2023 (8.682), con un mínimo teórico de 450 personas en cada uno de los 16 subámbitos territoriales | <https://www.idescat.cat/pub/?id=eulp&n=3202&geo=at&f=ssv> (también n=3170 y n=20833) |
| Inscripciones del CPNL | Consorci per a la Normalització Lingüística (Dades obertes de Catalunya) | Datos anuales; actualización bienal | 2011–2023 | Inscripciones (no personas) | Inscripciones: 2011: 105.605 · 2012: 95.248 · 2013: 74.345 · 2014: 62.336 · 2015: 65.194 · 2016: 68.352 · 2017: 71.040 · 2018: 75.112 · 2019: 85.185 · 2020: 51.705 · 2021: 72.411 · 2022: 89.212 · 2023: 97.244 (total: 1.012.989) | <https://analisi.transparenciacatalunya.cat/api/v3/views/q9ct-fkjt/export.csv?accessType=DOWNLOAD> |
| Divisions administratives (auxiliar) | ICGC | Actualización periódica; versión del 20/01/2026 | 2026 | Municipios de Cataluña | 947 municipios (escala 1:1.000.000) | <https://datacloud.icgc.cat/datacloud/divisions-administratives/json_unzip/divisions-administratives-v2r2-municipis-1000000-20260120.json> |
| Códigos territoriales (auxiliar) | Idescat | Tabla vigente, descargada en septiembre de 2026 | 2026 | Municipios de Cataluña | 947 municipios, 43 comarcas y 8 ámbitos territoriales | <https://www.idescat.cat/codis/?id=50&n=9&f=ssv> · <https://www.idescat.cat/codis/?id=50&n=28&f=ssv> |

## 1. Censo lingüístico y ECEPOV-2021 (conocimiento del catalán)

| Campo | Detalle |
|---|---|
| Organismo | Idescat (Institut d'Estadística de Catalunya). 2021: Idescat a partir de la ECEPOV-2021 (Encuesta de Características Esenciales de la Población y las Viviendas, INE) |
| Tipo | Censos y padrones con preguntas de lengua (1986, 1991, 1996, 2001 y 2011). El censo de 2011 ya no fue exhaustivo: combinó registros administrativos con una gran muestra de 1.621.643 hogares y 4.107.465 personas, cerca del 9% de la población (INE, nota de prensa del 12/12/2013 sobre los Censos de Población y Viviendas 2011). 2021: censo basado en registros administrativos; las lenguas, en la encuesta por muestreo ECEPOV-2021 |
| Universo | Población de 2 años o más residente en Cataluña |
| Tamaño (población de 2 años o más) | 1986: 5.835.954 · 1991: 5.949.177 · 1996: 5.984.334 · 2001: 6.176.751 · 2011: 7.306.072 · 2021: 7.467.000 (publicado en miles) |
| Muestra de la ECEPOV-2021 | El INE no publica la muestra por comunidad autónoma. En España, 172.444 viviendas efectivas (309.348 teóricas). El diseño garantiza estimaciones por comunidad (CV en torno al 4% para proporciones del 5%). Universo: personas en viviendas familiares principales. Trabajo de campo de abril de 2021 a febrero de 2022. Fuente: INE, informe metodológico estandarizado de la ECEPOV |
| Periodo | 1986–2021 |
| Unidad | Persona |
| Qué NO mide | El uso de la lengua: solo pregunta si la persona entiende, sabe hablar, leer y escribir. Además, en 2021 la pregunta cambia ("bien", "con dificultad", "nada"), por lo que 2021 no es comparable con 1986–2011 |
| Archivos | `datos/fuentes_oficiales/censo_conocimiento.csv`, `conocimiento_edad_2021.csv` |

Fuentes: [INE, Censos de Población y Viviendas 2011, nota de prensa del 12/12/2013](https://www.ine.es/prensa/np824.pdf) (muestra del censo de 2011); [INE, informe metodológico estandarizado de la ECEPOV-2021](https://www.ine.es/dynt3/metadatos/es/RespuestaPrint.html?oper=448) (muestra, universo y trabajo de campo); Idescat, Censo lingüístico, nota de prensa del 21/11/2013, tablas 1 y 2 ([PDF](https://govern.cat/govern/docs/2013/11/21/10/04/983677eb-2b2a-43ae-8793-9b22bd2a6cb4.pdf)); Idescat, Dossier núm. 17 (2014), datos definitivos del Censo 2011; [Idescat, indicador de conocimiento del catalán](https://www.idescat.cat/indicadors/?id=basics&n=10363).

Nota: en los CSV, "n=10363" es el identificador del indicador en la web del Idescat, no el tamaño de la muestra.

## 2. Encuesta de usos lingüísticos de la población (EULP)

| Campo | Detalle |
|---|---|
| Organismo | Idescat y Departamento de Política Lingüística (Generalitat de Catalunya) |
| Tipo | Encuesta por muestreo, quinquenal |
| Universo | Población de 15 años o más residente en Cataluña |
| Tamaño de la muestra | Ver la tabla siguiente, con el tipo de muestra y la fuente de cada cifra |
| Población de 15 años o más a la que se elevan los resultados | 2003: 5.619,5 miles (datos enlazados; 5.471,2 en los datos originales) · 2008: 6.162,5 · 2013: 6.253,8 · 2018: 6.386,6 · 2023: 6.785,1 |
| Periodo | 2003–2023 (Cataluña). Cruces por sexo, edad y lugar de nacimiento: 2008–2023 |
| Unidad | Persona (resultados elevados a la población, en miles) |
| Qué NO mide | A los menores de 15 años. Mide el uso declarado por la persona, no observado. Las celdas con menos de 20 casos muestrales no se publican (dato confidencial). Según la metodología del Idescat, las novedades metodológicas de 2008 y 2013 hacen que los datos originales de 2003 no sean comparables; para compararlos se publicaron las "Dades enllaçades 2003–2008–2013" |
| Archivos | `datos/fuentes_oficiales/eulp_cataluna.csv`, `datos/originales/idescat_eulp/`, `datos/procesados/eulp_*.csv` |

**Muestras de la EULP por edición**

| Edición | Muestra teórica | Muestra efectiva (final) | Error (Cataluña) | Fuente |
|---|---|---|---|---|
| 2003 | Pendiente de verificar | 7.257 entrevistas ("mostra final"). El documento EULP 2013 del Idescat da n=7.259 | Pendiente de verificar | Idescat, metodología web (apartado 3.4.1); Idescat, *EULP 2013*, p. 17 |
| 2008 | 7.300 | 7.140 (tasa de respuesta del 97,8%) | ±1,32% | Idescat, *EULP 2008*, notas metodológicas, secciones 4 y 8 |
| 2013 | 7.500 (diseño); 7.492 contando la prueba piloto | 7.255 (tasa de respuesta del 96,8%) | 1,16% según la web; 1,36% según el documento EULP 2013 | Idescat, metodología web; Idescat, *EULP 2013*, pp. 15 y 19 |
| 2018 | 9.000 | 8.780 ("mostra final") | 1,03% | Generalitat, *Dossier EULP 2018*, ficha técnica, p. 48 (página impresa y del PDF; la 47 no contiene la ficha) |
| 2023 | 9.000 | 8.682 | 1% (máximo del 5% en cada uno de los 16 subámbitos territoriales) | Idescat, metodología web |

Fuentes: [Idescat, EULP, metodología](https://www.idescat.cat/pub/?id=eulp&m=m) (muestras, errores, universo y comparabilidad); [Idescat, *EULP 2008*](https://www.idescat.cat/serveis/biblioteca/docs/cat/eulp2008.pdf) (muestra de 2008 y cambios metodológicos respecto a 2003); [Idescat, *Estadística social 2013. EULP*](https://www.idescat.cat/serveis/biblioteca/docs/cat/eulp2013.pdf) (muestras de 2003, 2008 y 2013); [Generalitat, Dossier EULP 2018, ficha técnica, p. 48](https://llengua.gencat.cat/web/.content/documents/dadesestudis/altres/arxius/dossier-eulp-2018.pdf) (muestra final de 2018); [Idescat, datos enlazados 2003-2008-2013](https://www.idescat.cat/pub/?id=eulp&n=7218) y [datos originales de 2003](https://www.idescat.cat/pub/?id=eulp&n=1059) (población de 2003); [Idescat, indicadores básicos de la EULP](https://www.idescat.cat/indicadors/?id=basics&n=10364) (población de 15 años o más).

## 3. Inscripciones a los cursos del CPNL (aprendizaje)

| Campo | Detalle |
|---|---|
| Organismo | Consorci per a la Normalització Lingüística (CPNL), publicado en el portal de datos abiertos de la Generalitat de Catalunya |
| Tipo | Registro administrativo |
| Universo | Inscripciones a los cursos de catalán del CPNL |
| Tamaño | 1.012.989 inscripciones en 2011–2023 (suma de la columna del total del dataset oficial tras la limpieza documentada en `docs/calidad_datos.md`), en 10.922 filas municipio-año: 889 municipios y una fila anual sin municipio catalán asignado (código 000000) |
| Periodo | 2011–2023 |
| Unidad | Inscripción, no persona |
| Qué NO mide | Personas distintas: una persona puede inscribirse más de una vez al año. Tampoco mide el aprendizaje fuera del CPNL ni si la persona termina o aprueba el curso. El origen solo se conoce en una parte de las inscripciones (muchas sin datos en 2020–2022) |
| Archivos | `datos/originales/cpnl_inscripciones_raw.csv`, `datos/procesados/cpnl_*.csv` |

Fuente: [Generalitat de Catalunya, Inscripciones a los cursos del CPNL (dataset q9ct-fkjt)](https://analisi.transparenciacatalunya.cat/d/q9ct-fkjt).

## 4. Mapa: ámbitos territoriales

| Campo | Detalle |
|---|---|
| Geometría | ICGC, Divisions administratives v2r2 (20/01/2026), municipios a escala 1:1.000.000, en coordenadas geográficas (lon/lat) |
| Correspondencias | Idescat, códigos territoriales: municipios con su comarca (id=50&n=9) y ámbitos territoriales de planificación con sus municipios (id=50&n=28): 947 municipios en 8 ámbitos territoriales |
| Datos EULP por ámbito territorial | Idescat, EULP 2023 por ámbitos territoriales del Plan territorial general de Cataluña (publicado el 27/11/2025): lengua habitual (n=3202), lengua inicial (n=3170) y conocimiento de lenguas (n=20833). Solo 2023 |
| Control | La lengua habitual por ámbito territorial coincide con la nota del Idescat: Terres de l'Ebre 66,8%, Comarques Centrals 59,6%, Ponent 51,1%, Alt Pirineu i Aran 50,5%, Comarques Gironines 45,0%, Camp de Tarragona 37,9%, Penedès 34,6% y Metropolità 24,7% |
| Qué NO mide | La EULP por ámbito territorial tiene más error que la de Cataluña (hasta un 5% por subámbito territorial). No hay serie por ámbitos territoriales comparable para 2013 y 2018. El mapa del CPNL excluye las inscripciones sin municipio catalán asignado (27.957 en 2011–2023) |
| Archivos | `datos/originales/icgc/`, `datos/originales/idescat_codis/`, `datos/originales/idescat_eulp_territorio/`, `datos/procesados/mapa_ambitos.geojson`, `mapa_centroides.csv`, `eulp_territorio.csv`, `cpnl_ambito.csv` |

Fuentes: [ICGC, Divisions administratives](https://datacloud.icgc.cat/datacloud/divisions-administratives/json_unzip/); [Idescat, códigos territoriales](https://www.idescat.cat/codis/?id=50); [Idescat, EULP 2023, resultados territoriales](https://www.idescat.cat/novetats/?id=5382).
