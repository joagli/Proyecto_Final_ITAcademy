# Metodología

Proyecto: ¿Se está "apagando" el catalán? Conocimiento, uso y aprendizaje en Cataluña.
Autor: Jorge Aguilar Liévanos.

---

## 1. Tipo de estudio

Estudio **descriptivo y observacional a partir de datos oficiales secundarios**. No se recogen datos propios: se toman estadísticas oficiales ya publicadas, se limpian, se cruzan y se describen.

Tres rasgos que lo definen:

- **Longitudinal**: se comparan los mismos indicadores a lo largo del tiempo (1986–2021 en conocimiento, 2003–2023 en uso, 2011–2023 en aprendizaje).
- **Triangulación de fuentes**: ninguna fuente responde sola a la pregunta, así que se combinan tres que miden cosas distintas.
- **Contraste de hipótesis por refutación**: se parte de la afirmación popular "el catalán se está muriendo", se deducen cuatro cosas que deberían cumplirse si fuera cierta y se comprueba cada una con datos.

**Límite explícito**: el estudio es descriptivo, no inferencial ni causal. No se calculan pruebas de significación ni se demuestran causas. Se describe lo que ha pasado y se señala hacia dónde apunta la evidencia.

## 2. Fuentes

El proyecto tiene **tres bloques de datos sobre la lengua**, independientes entre sí:

1. **Conocimiento censal**: censos lingüísticos 1986–2011 y ECEPOV-2021 (Idescat e INE).
2. **EULP**: la Encuesta de usos lingüísticos de la población (Idescat y Departamento de Política Lingüística).
3. **CPNL**: las inscripciones a los cursos de catalán (datos abiertos de la Generalitat).

Además, hay **tablas auxiliares para el mapa** (geometría del ICGC y correspondencias territoriales del Idescat). No son datos sobre la lengua: solo sirven para dibujar los ámbitos territoriales y asignar cada municipio a su ámbito territorial.

### 2.1 Conocimiento: censos lingüísticos 1986–2011 y ECEPOV-2021

- Qué mide: si la población entiende, sabe hablar, leer y escribir catalán.
- Universo: población de 2 años o más.
- Periodo: 1986, 1991, 1996, 2001, 2011 y 2021.
- Periodicidad: los censos de población son decenales (1981, 1991, 2001, 2011, 2021). El de 2011 ya no fue exhaustivo: combinó registros administrativos con una gran encuesta por muestreo, cerca del 9% de la población (INE, nota de prensa del 12/12/2013 sobre los Censos de Población y Viviendas 2011). Los años intermedios de la serie provienen de operaciones estadísticas de población equivalentes (1986 y 1996).
- **La ECEPOV-2021 es la continuación de la serie censal.** El Censo 2021 del INE se basa por primera vez en registros administrativos, y esos registros no recogen las lenguas. Para cubrir las características que no están en los registros, el INE creó la ECEPOV-2021 (Encuesta de Características Esenciales de la Población y las Viviendas, INE), que incluye el conocimiento y el uso de lenguas. El Idescat explota y publica los resultados de Cataluña, igual que hacía con los censos anteriores.
- La EULP también mide el conocimiento del catalán, pero de la población de 15 años o más y con otra pregunta. En la app, cada fuente va en su propio gráfico: nunca se mezclan en una misma serie.

**Ruptura metodológica 2011 → 2021**: además del cambio de operación, según la nota metodológica del Idescat la pregunta de conocimiento pasa de una respuesta de sí o no por habilidad a una respuesta con grados (**"bien", "con dificultad", "nada"**), y la cifra publicada de 2021 agrupa "bien" y "con dificultad". Por eso el 89,6% de 2021 **no** es comparable con el 73,2% de 2011: en la app se da en la nota, fuera de la serie 1986–2011.

### 2.2 Uso: EULP (Idescat y Departamento de Política Lingüística)

- Qué mide: lengua inicial, de identificación y habitual; usos por ámbitos; conocimiento; actitudes.
- Universo: población de 15 años o más.
- Periodicidad: quinquenal. Ediciones de 2003, 2008, 2013, 2018 y 2023.
- Tipo: **encuesta por muestreo**. En 2023, muestra efectiva de 8.682 personas, con un error aproximado del 1% para el conjunto de Cataluña y hasta cerca del 5% en territorios concretos. Muestras de todas las ediciones en `docs/fuentes_resumen.md`.
- **Comparabilidad de 2003**: según la publicación EULP 2008 del Idescat (notas metodológicas, secciones 4, 8 y 11, y capítulo 9), en 2008 cambiaron las preguntas, algunas categorías de respuesta, la selección de la muestra y el modo de entrevista. Los "Dades enllaçades 2003-2008-2013" solo recalculan los pesos y la calibración de 2003 con los criterios de 2008 (46,0% lengua habitual y 36,2% lengua inicial; los originales eran 50,1% y 40,5%). Por eso 2003 se muestra solo como referencia (línea discontinua) y los indicadores de uso se calculan desde 2008.

### 2.3 Aprendizaje: inscripciones del CPNL (Generalitat, datos abiertos)

- Qué mide: inscripciones a los cursos de catalán para adultos, por municipio, grupo de nivel y lugar de nacimiento.
- Periodo: 2011–2023. 10.922 filas: 889 municipios y una fila anual sin municipio catalán asignado (código 000000, que agrupa "sense dades" y territorios de fuera de Cataluña).
- Tipo: **registro administrativo**, no encuesta. No tiene margen de error muestral, pero sí errores de registro (ver `docs/calidad_datos.md`).
- Unidad: **inscripciones, no personas**. Una misma persona puede inscribirse más de una vez al año.
- En la app, el "Total CPNL" incluye la fila sin municipio catalán asignado (un 2,8% de las inscripciones de 2011–2023); las provincias y el mapa no la incluyen.

### 2.4 Territorio: ámbitos territoriales del Plan territorial general de Cataluña (Idescat e ICGC)

- Qué aporta: el mapa de la app, con los 8 ámbitos territoriales del Plan territorial general de Cataluña, el nivel en el que el Idescat publica la EULP por territorios.
- EULP por ámbito territorial: solo 2023 (lengua habitual, lengua inicial y "sabe hablar"), publicada el 27/11/2025. El error teórico máximo es del 5% en cada uno de los 16 subámbitos territoriales de muestreo.
- Geometría: municipios del ICGC unidos por ámbito territorial con la correspondencia oficial municipio → ámbito territorial del Idescat. No se unen comarcas porque Anoia y Moianès están repartidas entre dos ámbitos territoriales.
- CPNL por ámbito territorial: cada inscripción se asigna por su código de municipio; se excluye la fila sin municipio catalán asignado.

## 3. Por qué tres fuentes y no una

| | Censo / ECEPOV-2021 | EULP | CPNL |
|---|---|---|---|
| Qué mide | Conocimiento | Uso y conocimiento | Aprendizaje |
| Universo | 2 años o más | 15 años o más | Inscripciones |
| Serie | 1986–2021 | 2003–2023 | 2011–2023 |
| Tipo | Censo y encuesta oficial | Encuesta por muestreo | Registro administrativo |

- La EULP no puede responder si el catalán lleva décadas muriéndose: empieza en 2003.
- El censo no puede responder si la gente lo usa: nunca lo pregunta.
- El CPNL no dice nada sobre la población general: solo sobre quien se apunta a un curso.

**Dos cifras distintas de "sabe hablar"**: ECEPOV-2021 da 89,6% y EULP 2023 da 80,4%. No es una contradicción: universos distintos (2 años o más frente a 15 años o más, y la escuela hace que casi toda la población escolar lo sepa) y preguntas distintas (la de 2021 incluye "con dificultad").

## 4. Qué se usa de cada fuente

| Fuente | Se usa | Pestaña de la app |
|---|---|---|
| Censo / ECEPOV-2021 | Serie 1986–2011 de las cuatro habilidades; 2021 como punto aparte | Conocimiento |
| EULP | Lengua habitual e inicial 2003–2023; conocimiento y uso por sexo, edad y lugar de nacimiento 2008–2023; usos por ámbitos | Uso · ¿Quién lo habla? · ¿Con quién se usa? |
| CPNL | Inscripciones por año, nivel y origen, para el total del CPNL, provincia, municipio y ámbito territorial | Aprendizaje · Mapa |

## 5. Modelo de datos

No hay una base de datos relacional, y es una decisión consciente: **las tres fuentes no se pueden unir entre sí**, porque sus unidades de análisis son distintas (personas de 2 años o más, personas de 15 años o más, inscripciones). Cruzarlas en una sola tabla sería un error metodológico.

Lo que hay son **tablas independientes en formato largo (tidy)**, cada una con su propio grano, que comparten el año como eje conceptual de lectura, no como clave de unión (los años de cada fuente ni siquiera coinciden).

| Archivo | Una fila es… | Clave |
|---|---|---|
| `datos/procesados/cpnl_municipios.csv` | un municipio en un año | codigo_municipio + año |
| `datos/procesados/cpnl_cataluna_anual.csv` | un año, toda Cataluña | año |
| `datos/procesados/eulp_lengua_segmento.csv` | año + indicador + tipo de segmento + segmento + lengua | esos cinco campos |
| `datos/procesados/eulp_conocimiento_segmento.csv` | año + segmento + habilidad | esos tres campos |
| `datos/procesados/eulp_ambitos_segmento.csv` | año + ámbito + segmento + uso | esos cuatro campos |
| `datos/fuentes_oficiales/censo_conocimiento.csv` | un año censal | año |
| `datos/fuentes_oficiales/eulp_cataluna.csv` | una edición de la EULP | año |
| `datos/fuentes_oficiales/conocimiento_edad_2021.csv` | un grupo de edad en 2021 | grupo_edad |
| `datos/procesados/eulp_territorio.csv` | un ámbito territorial en 2023 | codigo_ambito |
| `datos/procesados/cpnl_ambito.csv` | un ámbito territorial en un periodo (cada año y el total 2011–2023) | codigo_ambito + periodo |
| `datos/procesados/mapa_ambitos.geojson` y `mapa_centroides.csv` | un ámbito territorial (geometría y punto de la etiqueta) | codigo_ambito |

**La única relación real** está dentro del bloque CPNL: `codigo_municipio` es el código INE del municipio y `provincia` se deriva de sus dos primeros dígitos. Es una relación de municipio a provincia (de muchos a uno). Para el mapa, el mismo código enlaza cada municipio con su comarca y su ámbito territorial (tablas oficiales del Idescat), y el ámbito territorial es la clave común de la geometría, la EULP territorial y el CPNL por ámbito territorial. Por eso importaba corregir la fila de Alfarràs que traía el código de otro municipio: una clave mal puesta rompe cualquier agregación territorial.

## 6. Proceso (ETL)

1. **Extracción**: `datos/originales/` guarda los archivos tal como los da la fuente, sin editar. El CPNL se descarga por script; las tablas de la EULP se descargan del Idescat.
2. **Transformación**: `src/preparar_datos.py` (CPNL), `src/preparar_eulp.py` (EULP) y `src/preparar_mapa.py` (mapa) limpian, corrigen y validan. `preparar_mapa.py` se detiene si la lengua habitual por ámbito territorial no coincide con la nota del Idescat.
3. **Carga**: `datos/procesados/` guarda las tablas limpias.
4. **Presentación**: `app.py` solo lee y muestra; no modifica datos.

Correcciones aplicadas y controles automáticos: ver `docs/calidad_datos.md` y la pestaña "Calidad de datos" de la app.

## 7. Limitaciones

- Estudio descriptivo: no se establecen relaciones causales.
- El mapa de la EULP solo existe para 2023: no permite ver la evolución por territorio, y las diferencias pequeñas entre ámbitos territoriales pueden caer dentro del margen de error.
- La EULP es una encuesta: las diferencias pequeñas pueden caer dentro del margen de error. Por eso la diferencia por sexo (80,9% frente a 79,9%) se interpreta como ausencia de diferencia.
- Las inscripciones del CPNL no son personas únicas.
- En 2020–2022 el origen de muchas inscripciones consta como "sin datos" (en Barcelona, el 44% en 2021). Los porcentajes por origen se calculan solo sobre inscripciones con origen conocido.
- Los cruces por sexo, edad y lugar de nacimiento de la EULP se publican desde 2008; la edición de 2003 se hizo con otra metodología. La serie general incluye 2003 solo como referencia (dato enlazado del Idescat): en 2008 cambiaron el cuestionario y el modo de entrevista.
- Entre 2008 y 2013 "Catalán y castellano" como lengua habitual cae de 735,4 a 426,6 miles; esas ediciones tuvieron cambios metodológicos que pueden influir, aunque el Idescat no cuantifica su efecto.
- Faltan dos cruces que el Idescat no publica en el mismo formato: lengua habitual por edad y lengua inicial por sexo.
- No se usan microdatos, sino tablas ya publicadas.

## 8. Reproducibilidad y cita de fuentes

Cualquier persona puede reproducir el trabajo ejecutando los dos scripts: descargan y limpian los datos y generan los mismos archivos procesados. Cada archivo de `datos/fuentes_oficiales/` incluye una columna `fuente`, y las fuentes se citan en la app y en el README, como piden las condiciones de uso del Idescat.
