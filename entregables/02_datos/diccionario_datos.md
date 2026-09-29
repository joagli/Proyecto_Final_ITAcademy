# Diccionario de datos

Datos de la entrega, copiados de `datos/procesados/` y `datos/fuentes_oficiales/` con `src/preparar_entrega.py`. Las fuentes y la limpieza están en `docs/fuentes_resumen.md`, `docs/calidad_datos.md` y `docs/calculos.md`.

## procesados/

### `cpnl_ambito.csv`

Inscripciones del CPNL por ámbito territorial, para cada año y para el total 2011–2023 (sin el código 000000).

112 filas y 12 columnas.

| Columna | Tipo | Descripción |
|---|---|---|
| `codigo_ambito` | texto | Código del ámbito territorial (AT01–AT08, Idescat) |
| `ambito` | texto | Ámbito territorial del Plan territorial general de Cataluña |
| `total` | número | Inscripciones totales (no personas) |
| `nacidos_cataluna` | número | Inscripciones de personas nacidas en Cataluña |
| `nacidos_resto_espana` | número | Inscripciones de personas nacidas en el resto de España |
| `nacidos_extranjero` | número | Inscripciones de personas nacidas en el extranjero (corregido desde 2022) |
| `sin_datos_origen` | número | Inscripciones sin dato de lugar de nacimiento |
| `origen_conocido` | número | Suma de los tres orígenes (base de los porcentajes por origen) |
| `periodo` | texto | Año o periodo acumulado (2011–2023) |
| `pct_cataluna` | número | % nacidos en Cataluña sobre el origen conocido |
| `pct_resto_espana` | número | % nacidos en el resto de España sobre el origen conocido |
| `pct_extranjero` | número | % nacidos en el extranjero sobre el origen conocido |

### `cpnl_cambios.csv`

Correcciones aplicadas al CPNL en la limpieza.

15 filas y 5 columnas.

| Columna | Tipo | Descripción |
|---|---|---|
| `tipo` | texto | Tipo de corrección |
| `municipio` | texto | Municipio afectado por la corrección |
| `anio` | número | Año |
| `antes` | texto | Código de municipio antes de la corrección |
| `despues` | texto | Código de municipio después de la corrección |

### `cpnl_cataluna_anual.csv`

Inscripciones del CPNL, total por año (incluye las que no tienen municipio catalán).

13 filas y 20 columnas.

| Columna | Tipo | Descripción |
|---|---|---|
| `anio` | número | Año |
| `total` | número | Inscripciones totales (no personas) |
| `nivel_inicial_basico1` | número | Inscripciones de nivel Inicial y Básico 1 |
| `nivel_basico23_elemental` | número | Inscripciones de nivel Básico 2-3 y Elemental |
| `nivel_intermedio_suficiencia` | número | Inscripciones de nivel Intermedio y Suficiencia |
| `nacidos_cataluna` | número | Inscripciones de personas nacidas en Cataluña |
| `nacidos_resto_espana` | número | Inscripciones de personas nacidas en el resto de España |
| `nacidos_extranjero` | número | Inscripciones de personas nacidas en el extranjero (corregido desde 2022) |
| `sin_datos_origen` | número | Inscripciones sin dato de lugar de nacimiento |
| `origen_conocido` | número | Suma de los tres orígenes (base de los porcentajes por origen) |
| `ue` | número | Nacidos en la Unión Europea |
| `resto_europa` | número | Nacidos en el resto de Europa |
| `norte_africa` | número | Nacidos en el norte de África |
| `resto_africa` | número | Nacidos en el resto de África |
| `america_sur_central` | número | Nacidos en América del Sur y Central |
| `asia` | número | Nacidos en Asia |
| `resto_mundo` | número | Nacidos en el resto del mundo |
| `dif_niveles` | número | Control: total − suma de niveles (0 = cuadra) |
| `dif_origen` | número | Control: total − (origen conocido + sin datos) (0 = cuadra) |
| `dif_subregiones` | número | Control: nacidos en el extranjero − suma de regiones (0 = cuadra) |

### `cpnl_municipios.csv`

Inscripciones a los cursos del CPNL. Una fila por municipio y año (2011–2023). El código 000000 agrupa las inscripciones sin municipio catalán asignado.

10.922 filas y 23 columnas.

| Columna | Tipo | Descripción |
|---|---|---|
| `codigo_municipio` | texto | Código INE del municipio (6 dígitos); 000000 = sin municipio catalán asignado |
| `municipio` | texto | Nombre del municipio |
| `provincia` | texto | Provincia (de los dos primeros dígitos del código) |
| `anio` | número | Año |
| `total` | número | Inscripciones totales (no personas) |
| `nivel_inicial_basico1` | número | Inscripciones de nivel Inicial y Básico 1 |
| `nivel_basico23_elemental` | número | Inscripciones de nivel Básico 2-3 y Elemental |
| `nivel_intermedio_suficiencia` | número | Inscripciones de nivel Intermedio y Suficiencia |
| `nacidos_cataluna` | número | Inscripciones de personas nacidas en Cataluña |
| `nacidos_resto_espana` | número | Inscripciones de personas nacidas en el resto de España |
| `nacidos_extranjero` | número | Inscripciones de personas nacidas en el extranjero (corregido desde 2022) |
| `sin_datos_origen` | número | Inscripciones sin dato de lugar de nacimiento |
| `origen_conocido` | número | Suma de los tres orígenes (base de los porcentajes por origen) |
| `ue` | número | Nacidos en la Unión Europea |
| `resto_europa` | número | Nacidos en el resto de Europa |
| `norte_africa` | número | Nacidos en el norte de África |
| `resto_africa` | número | Nacidos en el resto de África |
| `america_sur_central` | número | Nacidos en América del Sur y Central |
| `asia` | número | Nacidos en Asia |
| `resto_mundo` | número | Nacidos en el resto del mundo |
| `dif_niveles` | número | Control: total − suma de niveles (0 = cuadra) |
| `dif_origen` | número | Control: total − (origen conocido + sin datos) (0 = cuadra) |
| `dif_subregiones` | número | Control: nacidos en el extranjero − suma de regiones (0 = cuadra) |

### `cpnl_validacion.csv`

Controles de coherencia del CPNL: filas que no cuadran, por año.

13 filas y 5 columnas.

| Columna | Tipo | Descripción |
|---|---|---|
| `anio` | número | Año |
| `filas` | número | Número de filas del año |
| `falla_niveles` | número | Filas con descuadre por nivel |
| `falla_origen` | número | Filas con descuadre por origen |
| `falla_subregiones` | número | Filas con descuadre por región |

### `eulp_ambitos_segmento.csv`

EULP: lengua usada en cada ámbito de uso (hogar, amigos, comercio...). Una fila por año, ámbito, segmento y categoría de uso.

5.256 filas y 10 columnas.

| Columna | Tipo | Descripción |
|---|---|---|
| `año` | número | Año (edición de la EULP) |
| `ambito` | texto | Ámbito de uso de la lengua (con los amigos, en el comercio...) |
| `tipo_segmento` | texto | Variable de corte: sexo, edad o lugar de nacimiento |
| `segmento` | texto | Grupo dentro del corte ('total' = todos) |
| `orden_segmento` | número | Orden para los gráficos |
| `categoria` | texto | Categoría de lengua o de uso (las menores se agrupan en 'Otras y no consta') |
| `orden_categoria` | número | Orden para los gráficos |
| `miles` | número | Miles de personas |
| `total` | número | Población de referencia del ámbito (miles) |
| `pct` | número | % sobre el total del grupo |

### `eulp_conocimiento_segmento.csv`

EULP: % que conoce el catalán (entender, hablar, leer, escribir) por sexo, edad y lugar de nacimiento. Una fila por año, segmento y habilidad.

455 filas y 6 columnas.

| Columna | Tipo | Descripción |
|---|---|---|
| `año` | número | Año (edición de la EULP) |
| `tipo_segmento` | texto | Variable de corte: sexo, edad o lugar de nacimiento |
| `segmento` | texto | Grupo dentro del corte ('total' = todos) |
| `orden_segmento` | número | Orden para los gráficos |
| `habilidad` | texto | Entender, saber hablar, leer, escribir o las cuatro |
| `pct` | número | % sobre el total del grupo |

### `eulp_lengua_segmento.csv`

EULP: lengua inicial, de identificación y habitual por sexo, edad y lugar de nacimiento. Una fila por año, indicador, segmento y categoría de lengua.

448 filas y 10 columnas.

| Columna | Tipo | Descripción |
|---|---|---|
| `año` | número | Año (edición de la EULP) |
| `indicador` | texto | Lengua inicial, de identificación o habitual |
| `tipo_segmento` | texto | Variable de corte: sexo, edad o lugar de nacimiento |
| `segmento` | texto | Grupo dentro del corte ('total' = todos) |
| `orden_segmento` | número | Orden para los gráficos |
| `categoria` | texto | Categoría de lengua o de uso (las menores se agrupan en 'Otras y no consta') |
| `orden_categoria` | número | Orden para los gráficos |
| `miles` | número | Miles de personas |
| `total` | número | Población del grupo (miles) |
| `pct` | número | % sobre el total del grupo |

### `eulp_territorio.csv`

EULP 2023 por ámbito territorial (Plan territorial general de Cataluña): lengua habitual, lengua inicial y sabe hablar. Una fila por ámbito territorial.

8 filas y 11 columnas.

| Columna | Tipo | Descripción |
|---|---|---|
| `codigo_ambito` | texto | Código del ámbito territorial (AT01–AT08, Idescat) |
| `ambito` | texto | Ámbito territorial del Plan territorial general de Cataluña |
| `año` | número | Año (edición de la EULP) |
| `poblacion_15mas_miles` | número | Población de 15 años o más (miles) |
| `habitual_catalan_miles` | número | Catalán como lengua habitual (miles) |
| `habitual_catalan_pct` | número | Catalán como lengua habitual (%) |
| `inicial_catalan_miles` | número | Catalán como lengua inicial (miles) |
| `inicial_catalan_pct` | número | Catalán como lengua inicial (%) |
| `sabe_hablar_miles` | número | Sabe hablar catalán (miles) |
| `sabe_hablar_pct` | número | Sabe hablar catalán (%) |
| `fuente` | texto | Fuente oficial de la fila |

### `mapa_ambitos.geojson`

Geometría simplificada de los 8 ámbitos territoriales (lon/lat), a partir de los municipios del ICGC.

8 elementos. Propiedades: `codigo_ambito` y `ambito`.

### `mapa_centroides.csv`

Punto interior de cada ámbito territorial, donde el mapa escribe la etiqueta.

8 filas y 4 columnas.

| Columna | Tipo | Descripción |
|---|---|---|
| `codigo_ambito` | texto | Código del ámbito territorial (AT01–AT08, Idescat) |
| `ambito` | texto | Ámbito territorial del Plan territorial general de Cataluña |
| `lon` | número | Longitud (grados) |
| `lat` | número | Latitud (grados) |

### `metadatos.json`

Origen y fecha de proceso de los datos del CPNL.

## fuentes_oficiales/

### `censo_conocimiento.csv`

Conocimiento del catalán (censos lingüísticos 1986–2011 y ECEPOV-2021). Una fila por año.

6 filas y 9 columnas.

| Columna | Tipo | Descripción |
|---|---|---|
| `anio` | número | Año |
| `poblacion_2mas` | número | Población de 2 años o más |
| `personas_sabe_hablar` | número | Personas que saben hablar catalán |
| `pct_entiende` | número | % que entiende el catalán |
| `pct_sabe_hablar` | número | % que sabe hablar catalán |
| `pct_sabe_leer` | número | % que sabe leer catalán |
| `pct_sabe_escribir` | número | % que sabe escribir catalán |
| `comparable_con_serie` | texto | 'si' si es comparable con la serie 1986–2011 |
| `fuente` | texto | Fuente oficial de la fila |

### `conocimiento_edad_2021.csv`

Conocimiento del catalán por grupo de edad en 2021 (ECEPOV-2021). Una fila por grupo.

7 filas y 6 columnas.

| Columna | Tipo | Descripción |
|---|---|---|
| `grupo_edad` | texto | Grupo de edad |
| `poblacion_miles` | número | Población del grupo (miles) |
| `sabe_hablar_miles` | número | Sabe hablar catalán (miles) |
| `pct_sabe_hablar` | número | % que sabe hablar catalán |
| `pct_sabe_escribir` | número | % que sabe escribir catalán |
| `fuente` | texto | Fuente oficial de la fila |

### `eulp_cataluna.csv`

EULP, serie de Cataluña 2003–2023: población, lengua inicial y habitual. Una fila por edición (2003: dato enlazado, solo como referencia).

5 filas y 7 columnas.

| Columna | Tipo | Descripción |
|---|---|---|
| `anio` | número | Año |
| `poblacion_15mas_miles` | número | Población de 15 años o más (miles) |
| `lengua_inicial_catalan_miles` | número | Catalán como lengua inicial (miles) |
| `lengua_inicial_catalan_pct` | número | Catalán como lengua inicial (%) |
| `lengua_habitual_catalan_pct` | número | Catalán como lengua habitual (%) |
| `lengua_habitual_castellano_pct` | número | Castellano como lengua habitual (%) |
| `fuente` | texto | Fuente oficial de la fila |
