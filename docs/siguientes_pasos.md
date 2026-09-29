# Siguientes pasos: líneas de investigación futura

Estas líneas no son conclusiones del proyecto. Son hipótesis que los datos actuales sugieren, o que no pueden responder, con la fuente oficial que permitiría estudiarlas.

## 1. Consumo audiovisual y streaming

**Hipótesis.** El bajo uso del catalán en los ámbitos digitales podría estar relacionado con un consumo audiovisual y de internet mayoritariamente en otras lenguas. En nuestros datos (EULP 2023), publicar en redes sociales es el ámbito con menos catalán (20,5% solo o más catalán, sobre la población que publica en redes) y los mensajes de móvil están entre los más bajos (24,4%).

**Fuente.** La EULP 2008 midió las horas de televisión, radio y prensa por lengua (y la EULC 2003, además, la lengua de la página de inicio de internet y del correo electrónico). Comprobado en la metodología del Idescat: ese apartado "solo está disponible para la edición de 2008". Las ediciones de 2013, 2018 y 2023 no preguntan por consumo audiovisual ni de internet; solo miden la lengua al escribir mensajes de móvil (2018 y 2023) y al publicar en redes sociales (2023). Para estudiar el streaming haría falta otra fuente, todavía por identificar.

## 2. La actitud cuando alguien habla en catalán y le contestan en castellano

**Hipótesis.** Parte de la pérdida de uso podría deberse a que muchas personas que hablan catalán cambian al castellano cuando su interlocutor contesta en castellano.

**Fuente.** EULP, preguntas de actitudes lingüísticas: "Actitud lingüística en iniciar una conversa i freqüència d'iniciar-la en català" (Idescat, n=3172) y, para comparar 2003, 2008 y 2013, los datos enlazados "Actituds en relació amb els usos lingüístics" (n=7233).

## 3. Transmisión intergeneracional

**Hipótesis.** El catalán podría transmitirse menos de padres a hijos en las familias lingüísticamente mixtas, aunque los hijos lo aprendan en la escuela.

**Fuente.** EULP, "Usos lingüístics amb els membres de la família" (Idescat, n=3271): lengua con la madre, el padre, los abuelos, la pareja y los hijos (en ediciones anteriores, el hijo mayor).

## 4. Segunda generación de inmigrantes

**Hipótesis.** Los hijos de personas nacidas en el extranjero y nacidos en Cataluña podrían conocer el catalán como sus compañeros de edad, pero usarlo menos.

**Fuente.** ECEPOV-2021 (Encuesta de Características Esenciales de la Población y las Viviendas, INE): incluye un módulo sobre la segunda generación de inmigrantes y preguntas sobre conocimiento y uso de lenguas. El INE ofrece los microdatos anonimizados en INEbase.

## 5. Turismo, trabajo y vivienda

**Hipótesis.** El uso del catalán en los ámbitos de atención al público (comercio, restaurantes y bares, clientes) podría variar con el peso del turismo en cada territorio y con la composición de la población que trabaja y reside en él.

**Fuente.** EULP, usos por ámbitos (ya en `datos/procesados/eulp_ambitos_segmento.csv`), cruzada con las estadísticas del Idescat de turismo, trabajo y vivienda por territorio.

## 6. Niveles de los cursos del CPNL

**Hipótesis.** El CPNL se ha convertido sobre todo en una puerta de entrada: crece el peso de los niveles iniciales y baja el de los avanzados.

**Datos del proyecto** (inscripciones de cada año, no seguimiento de alumnos: no se puede saber si quien empieza un nivel inicial llega después a uno avanzado):

| Nivel | 2011 | 2023 |
|---|---:|---:|
| Inicial y Básico 1 | 36,1% | 44,4% |
| Básico 2-3 y Elemental | 34,1% | 39,9% |
| Intermedio y Suficiencia | 29,8% | 15,6% |

**Fuente para seguir.** Haría falta un registro con seguimiento de alumnos (trayectorias), que el dataset abierto del CPNL (q9ct-fkjt) no tiene.

## 7. Alcance del CPNL por territorio

**Hipótesis.** El alcance del CPNL entre la población nacida en el extranjero podría ser distinto en cada ámbito territorial.

**Fuente.** Inscripciones por cada 1.000 residentes nacidos en el extranjero, por ámbito territorial: `datos/procesados/cpnl_ambito.csv` (numerador) y el Padrón continuo por lugar de nacimiento que publica el Idescat (denominador).

## 8. Distancia entre lengua de identificación y lengua habitual

**Hipótesis.** En algunos grupos, más personas se identifican con el catalán de las que lo usan habitualmente, o al revés; esa distancia podría señalar dónde hay margen de uso.

**Fuente.** EULP, lengua de identificación y lengua habitual por sexo, edad y lugar de nacimiento (ya en `datos/procesados/eulp_lengua_segmento.csv`).

## 9. Comparación con otras lenguas cooficiales

**Hipótesis.** El patrón "más conocimiento, menos peso en el uso" podría repetirse en otras lenguas cooficiales con fuerte inmigración y crecimiento de la población.

**Fuente.** Las encuestas sociolingüísticas oficiales del País Vasco (Gobierno Vasco) y de Galicia (Instituto Galego de Estatística), comparando solo indicadores con la misma definición.
