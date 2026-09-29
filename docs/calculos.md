# Cálculos de los indicadores

Equivalente al documento de fórmulas DAX que pide el enunciado: cada indicador que la app o los documentos **calculan** (no los que se copian tal cual de la fuente), con su fórmula, su base y dónde se usa. El código está en `app.py` y en `src/`.

Convenciones:
- "pp" = puntos porcentuales: diferencia entre dos porcentajes.
- Los porcentajes se muestran con un decimal y coma decimal; los cálculos se hacen sin redondear.
- "Origen conocido" = nacidos en Cataluña + nacidos en el resto de España + nacidos en el extranjero (sin "sin datos de origen").

## 1. Conocimiento (censo y EULP)

| Indicador | Fórmula | Base | Dónde |
|---|---|---|---|
| Variación de "sabe hablar", 1986–2011 | % 2011 − % 1986 | Población de 2 años o más | KPI de Conocimiento |
| Variación de personas que saben hablar | (personas 2011 ÷ personas 1986 − 1) × 100 | Personas de 2 años o más | KPI de Conocimiento; prueba 1 |
| Personas que saben hablar (millones) | personas_sabe_hablar ÷ 1.000.000 | Personas de 2 años o más | Gráfico de barras de Conocimiento |
| % dentro de las barras de personas | Valor publicado de "sabe hablar" de cada censo (64,0; 68,3; 75,3; 74,5; 73,2) | Población de 2 años o más | Gráfico de barras de Conocimiento |
| Personas más que saben hablar según la EULP, 2008–2023 | población 15+ 2023 × % 2023 − población 15+ 2008 × % 2008 = 6.785,1 × 80,4% − 6.162,5 × 78,3% = 630,0 miles | Población de 15 años o más | Prueba 1 |
| "Sabe hablar" por origen y edad (EULP) | Valor publicado por el Idescat (no se recalcula) | Población de 15 años o más de cada grupo | Conocimiento |
| "Sabe hablar" y "sabe escribir" por edad (mapa de calor) | Valor publicado por el Idescat (no se recalcula); la escala de color empieza en la decena inferior al mínimo de la habilidad elegida | Población de 15 años o más de cada grupo de edad | Conocimiento |

## 2. Uso (EULP)

| Indicador | Fórmula | Base | Dónde |
|---|---|---|---|
| Variación de la lengua habitual catalán | % 2023 − % 2003 (2003: datos enlazados del Idescat) | Población de 15 años o más | KPI de Uso; prueba 4 |
| Caída desde 2008 y reparto por periodos | % 2023 − % 2008; % 2023 − % 2018; % 2018 − % 2008 | Población de 15 años o más | Prueba 4 |
| Variación de la población de 15 años o más | (población 2023 ÷ población 2003 − 1) × 100 | Población de 15 años o más | KPI de Uso |
| Variación de personas con catalán como lengua inicial | (miles 2023 ÷ miles 2003 − 1) × 100 | Población de 15 años o más | KPI de Uso |
| % por lengua habitual, inicial o de identificación, por grupo | Suma de las categorías del grupo ÷ total publicado del grupo × 100. "Otras y no consta" agrupa el resto de categorías | Población de 15 años o más de cada grupo | ¿Quién lo habla?; Uso |
| Peso de cada origen en la población | Población del origen ÷ suma de los tres orígenes | Población de 15 años o más | Uso, "¿Por qué baja el porcentaje?" |
| Personas con solo catalán y con catalán solo o combinado, 2018–2023 | Miles "catalán" 2023 − miles "catalán" 2018 = 2.211,1 − 2.305,1 = −94,0 miles; miles ("catalán" + "catalán y castellano") = 2.779,3 (2018) y 2.847,6 (2023) | Población de 15 años o más | Uso, "¿Por qué baja el porcentaje?" |
| % total recompuesto (para la descomposición) | P(año) = Σ_g peso_g(año) × tasa_g(año), con g = Cataluña, resto de España y extranjero | Población de 15 años o más | Uso |
| Cambio total | P(2023) − P(2008) = −3,1 pp sin redondear (−3,0 con los valores publicados, 35,6% y 32,6%) | Población de 15 años o más | Uso |
| Efecto composición | Σ_g (peso_g 2023 − peso_g 2008) × (tasa_g 2008 + tasa_g 2023) / 2 = −0,3 pp. Kitagawa (1955), valores medios de 2008 y 2023; composición + dentro = cambio total, exactamente | Población de 15 años o más | Uso |
| Efecto dentro de los grupos | Σ_g (tasa_g 2023 − tasa_g 2008) × (peso_g 2008 + peso_g 2023) / 2 = −2,7 pp. Kitagawa (1955), valores medios de 2008 y 2023; composición + dentro = cambio total, exactamente | Población de 15 años o más | Uso |

## 3. ¿Con quién se usa? (EULP, ámbitos de uso)

| Indicador | Fórmula | Base | Dónde |
|---|---|---|---|
| % por categoría de uso en cada ámbito | Miles de la categoría ÷ total del ámbito × 100. Es la misma base que en las tablas del Idescat | Población de 15 años o más, o la población del ámbito (hogar, estudios, trabajo, clientes, deporte, culto y redes sociales) | ¿Con quién se usa? |
| "Solo o más catalán" | % "Solo catalán" + % "Más catalán que castellano" | Igual que la fila anterior | Tarjetas, orden de las barras y gráfico de pesas |
| "Solo o más castellano" (vista simplificada) | % "Solo castellano" + % "Más castellano que catalán" | Igual que la fila anterior | Vista simplificada |
| Filtro de cobertura | Un ámbito se muestra si la suma de sus categorías con dato es ≥ 90%; si no, faltan categorías confidenciales y se oculta | — | ¿Con quién se usa? |

## 4. Aprendizaje (CPNL)

| Indicador | Fórmula | Base | Dónde |
|---|---|---|---|
| Inscripciones del año o del periodo | Σ total de las filas del ámbito elegido (Total CPNL, provincia o municipio) | Inscripciones, no personas | KPI, barras por nivel, tablas |
| Variación de inscripciones | (2023 ÷ 2011 − 1) × 100 | Inscripciones | KPI |
| Aumento desde el mínimo anterior a la COVID-19 | (2023 ÷ mínimo de 2011–2019 − 1) × 100 = (97.244 ÷ 62.336 − 1) × 100 = 56% (mínimo: 2014) | Inscripciones | Prueba 3; KPI de Aprendizaje |
| % nacidos en el extranjero | Nacidos en el extranjero ÷ origen conocido × 100 | Inscripciones con origen conocido | KPI, prueba 3, provincias, top 10 |
| Composición por origen | Inscripciones de cada origen ÷ origen conocido × 100 | Inscripciones con origen conocido | Gráfico al 100% |
| % sin municipio catalán asignado | Inscripciones del código 000000 ÷ Total CPNL × 100 = 27.957 ÷ 1.012.989 = 2,8% (2011–2023) | Inscripciones | Notas de Aprendizaje y prueba 3 |
| % sin datos de origen | Sin datos de origen ÷ total × 100 | Inscripciones | Nota del gráfico por origen |

## 5. Mapa

| Indicador | Fórmula | Base | Dónde |
|---|---|---|---|
| % catalán como lengua habitual y como lengua inicial por ámbito territorial | Miles "Català" ÷ total del ámbito territorial × 100 (tablas del Idescat por ámbitos territoriales, en miles) | Población de 15 años o más del ámbito territorial | Mapa |
| % "sabe hablar" por ámbito territorial | Valor publicado por el Idescat (no se recalcula) | Población de 15 años o más del ámbito territorial | Mapa |
| % de inscripciones por origen y ámbito territorial | Inscripciones de cada origen ÷ origen conocido del ámbito territorial × 100; en el periodo total se suman primero los 13 años | Inscripciones con origen conocido, sin la fila sin municipio | Mapa |
| Inscripciones totales por ámbito territorial | Σ total de las inscripciones de los municipios del ámbito territorial; en el periodo total se suman los 13 años (985.032 en 2011–2023, sin las 27.957 sin municipio) | Inscripciones, no personas | Mapa (capa de totales) y barra al 100% por ámbito territorial |
| Ámbito territorial de cada municipio | Correspondencia oficial del Idescat (códigos territoriales id=50&n=28), por código de municipio | — | `src/preparar_mapa.py` |

## 6. Controles de calidad

| Control | Fórmula | Dónde |
|---|---|---|
| Descuadre por nivel | total − (inicial y básico 1 + básico 2-3 y elemental + intermedio y suficiencia) | `src/preparar_datos.py` |
| Descuadre por origen | total − (origen conocido + sin datos de origen) | `src/preparar_datos.py` |
| Descuadre por región | nacidos en el extranjero − Σ regiones de nacimiento | `src/preparar_datos.py` |
| Nacidos en el extranjero desde 2022 | Valor de la fuente − sin datos de origen (la fuente los suma desde 2022) | `src/preparar_datos.py` |
| Control del mapa | % de lengua habitual por ámbito territorial redondeado a un decimal = valores de la nota del Idescat del 27/11/2025 | `src/preparar_mapa.py` |
