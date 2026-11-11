# Mapa del mundo: cómo está hecho y de qué licencias depende (T11 / T24)

Pantalla «Mapa del mundo» (`#mapa`): cada país se colorea según una **capa** y al tocarlo se llega a su ficha. Primera versión: 10-11-2026.

## Capas de hoy
Las cinco primeras salen de los datos que ya tienen las fichas de país (`data/atlas-data.js`), sin pedir nada nuevo a nadie; las dos últimas cargan su fichero al elegirlas (`data/conflictos.js`, `data/comunicaciones.js`):
1. **Tratados básicos de los que es parte** (0 a 9).
2. **Un tratado concreto** (parte / firmó sin ratificar / no es parte), a elegir entre los 18 del catálogo.
3. **Invitación permanente** a los mandatos temáticos.
4. **Mandato de relator para el país**.
5. **Comisión o misión de investigación**.
6. **Conflictos armados (UCDP), por año** (T68, 10-11-2026): conflictos armados estatales con combates en el país ese año, de 1946 a 2025, con selector de año. Dos colores: «guerra» (1000 o más muertes en combate en el año) y «conflicto menor» (de 25 a 999). Fuente: UCDP/PRIO Armed Conflict Dataset v26.1 (CC BY 4.0), que se cita en la leyenda con su versión. Cuenta solo conflictos entre un Estado y otro Estado o un grupo armado: no incluye la violencia contra civiles (otro conjunto de UCDP, no usado). Se regenera con `python3 -I scripts/fetch_ucdp.py` (UCDP publica una versión al año; no entra en la revisión diaria). Cuatro nombres de UCDP sin ficha (Hyderabad, Vietnam del Sur, Yemen del Sur, Taiwán) no se dibujan.
7. **Comunicaciones de los relatores recibidas**: suma de las comunicaciones enviadas a cada país en los informes conjuntos de los procedimientos especiales (junio de 2019 a noviembre de 2022, `data/comunicaciones.js`); cinco tramos (ninguna, 1–4, 5–14, 15–39, 40 o más). Es la cifra oficial, no el texto de las cartas. Ninguna de las dos capas valora a ningún Estado.

8. **Recomendaciones del EPU recibidas, por ciclo** (T68 c, 10-11-2026): cuántas recomendaciones recibió cada país en su Examen Periódico Universal, con selector de ciclo (2.º, 3.º y 4.º; el 1.º numera de otra manera y no se cuenta). Cinco tramos (menos de 150 … 300 o más) y un color aparte para «sin cifra» (el ciclo 4 aún no ha examinado a todos los países, o el informe no se pudo contar). Carga `data/epu.js` al elegirla.

**Línea de tiempo (T68, #185, 11-11-2026):** deslizador de años con botón «Animar» (recorre los años solo y se detiene al cambiar de capa o de pantalla) en las capas de **conflictos** (1946–2025), **EPU** (ciclos 2 a 4), **un tratado concreto** y **tratados básicos de los que es parte** (1948 a hoy, con la fecha de ratificación o adhesión de las fichas) e **invitación permanente** (1999 a hoy). El año `hoy` es el dato actual. Cada leyenda dice «Datos al <fecha>» (la fecha de consulta de la fuente; en comunicaciones, el último informe incluido).

**«Tiempo real»:** las fuentes oficiales de la ONU no publican datos en directo; lo honesto es «actualizado cada día» (la revisión diaria de Actions) y la fecha del dato en cada capa. Pendiente (necesita datos que aún no están): visitas de relatores por año (base de visitas de OHCHR) y más temas de intensidad (ver la cola).

Cada capa tiene leyenda con las cuentas, la lista de debajo repite los mismos datos (para quien no use el mapa) y la prueba `tests/browser.cjs` comprueba que la leyenda suma los 196 países.

## El panel del país: todas las capas a la vez (T86, 11-11-2026, #230)
Caso Colombia (reporte de Jeisson): el panel solo mostraba el dato de la capa elegida y, con las capas de mandato propio y comisión de investigación (13 y 8 países), un país con mucha información parecía vacío. Ahora, al tocar un país, el panel muestra **las siete capas a la vez** (tratados básicos, invitación permanente, mandato de relator, comisión o misión, conflictos, comunicaciones y EPU) con el dato de hoy, igual para los 196; donde no hay dato dice **por qué**, y cada fila lleva a su sección de la ficha (`Ver en la ficha`). La ficha tiene «Ver en el mapa». Pendiente: capa de **presencia de la ONU** (oficinas de ACNUDH y misiones de paz; hoy «comisión o misión» solo cuenta las de investigación) y mostrar en la ficha el conflicto UCDP y la cifra del EPU. Prueba: `tests/browser.cjs` (bloque T86).

## Cómo está hecho (y por qué sin librería de mapas)
- **SVG propio**, sin MapLibre ni Leaflet: no hay teselas que pedir a nadie, ni cuenta, ni scripts de fuera, no registra a quien lo mira, y pesa 72 KB (`data/mapa.js`) en vez de cientos de KB de librería. Para un mapa de países coloreados no hace falta más.
- **Contornos:** Natural Earth, «Admin 0 – Countries», 1:50 millones, **dominio público** (<https://www.naturalearthdata.com/about/terms-of-use/>). Se simplifican y se proyectan (Miller) con `scripts/generar_mapa.py`, que se puede volver a ejecutar para regenerar `data/mapa.js`. Se descarga una vez; el sitio no carga nada de fuera.
- **Los 196 países de ATLAS** tienen forma o, si son diminutos (35, como Malta o Tuvalu), un círculo. Dos códigos de ATLAS no son el ISO de Natural Earth (`CRO` = Croacia, `RKS` = Kosovo): están en la tabla `ATLAS_A_NE` del script.
- **Lo que no tiene ficha de país** (territorios, Taiwán, Sahara Occidental…) sale como fondo gris y sin clic. Las fronteras son esquemáticas y la pantalla lo dice: ATLAS no opina sobre el estatus de ningún territorio.
- **Accesibilidad:** el dibujo es una imagen con descripción; lo operable es el selector de país, la lista y el panel con el dato (a prueba con axe-core: 0 incumplimientos). El zoom no ensancha la caja: cambia el recuadro visible del SVG (`viewBox`), así que nunca desborda la página (regla de la lista de comprobación de interfaz). «Acercar» se centra en el país elegido (o en el centro); «Ver todo el mapa» vuelve al mundo entero, centrado y con margen para que Alaska, Chukotka o Fiyi no toquen el borde. Con el ratón se arrastra; con el dedo se arrastra en horizontal y el dedo vertical sigue moviendo la página (`touch-action: pan-y`, sin `overscroll-behavior`), para que el mapa no atrape a quien quiere seguir bajando; para mover en vertical están las flechas «Mover el mapa», que también valen con el teclado (flechas, `+`, `-`, `0`). Ctrl + rueda acerca (la rueda sola desplaza la página).
- **Colores (10-11-2026, #183):** escala propia azul-verdosa de menor a mayor (de `#2b7080` a `#a8f0e4`; la luminosidad crece de forma uniforme, legible para daltónicos), violeta para «no/ninguna», lavanda para «firmó sin ratificar», gris azulado para «sin datos» y rojo y rosa para guerra y conflicto menor. Ningún dorado ni marrón de la plantilla. El marco del mapa es azul muy oscuro, distinto del fondo de la web. `tests/browser.cjs` comprueba que ningún color de las leyendas se parezca al fondo del mapa ni al dorado.

## Informe de licencias para las capas siguientes
| Fuente | Licencia y condiciones | Veredicto |
|---|---|---|
| **Natural Earth** (contornos) | Dominio público; no exige atribución (se cita igualmente). | En uso. |
| **UCDP** (Uppsala Conflict Data Program, conflictos armados) | **CC BY 4.0**: «todos los conjuntos son gratuitos y se pueden usar y redistribuir citando las publicaciones que figuran con cada uno» (<https://ucdp.uu.se/downloads/>, comprobado el 10-11-2026). Sin cuenta. | **Apta** para la capa de conflictos: se cita cada conjunto con su versión y se indica la fecha. |
| **ACLED** (eventos de conflicto) | Exige registro y aceptar sus términos; uso no comercial; limita la redistribución de los datos y el uso con sistemas de IA; el logo es reservado (<https://acleddata.com/terms-and-conditions>, <https://acleddata.com/eula>). | **Descartada**: choca con la regla del proyecto (abierto, sin cuentas, datos reutilizables con CC BY 4.0). |
| **MapLibre GL JS** / **Leaflet** (librerías) | BSD-3-Clause / BSD-2-Clause: libres. | No hacen falta por ahora; se valorarán si algún día se necesitan teselas o un mapa de calor real. |

## Capa del EPU: de dónde sale cada cifra
- **Fuente:** los informes del Grupo de Trabajo del EPU (`A/HRC/<sesión>/<n>`, Biblioteca Digital de la ONU), no la lista de documentos por país. `scripts/fetch_epu_informes.py` lista los 740 informes (y sus adiciones `/Add.1`, la respuesta del Estado) de 193 países en `data/fuentes/epu_informes.json` (una búsqueda por año, a 5 s entre peticiones: la Biblioteca corta cada búsqueda en unos 600 resultados). `texto_completo.py` los descarga con el resto de documentos de país.
- **Qué se cuenta:** cada punto numerado de la sección «Conclusions and/or recommendations» (116.1, 116.2…), sumando los párrafos de apoyadas, tomadas en nota y no apoyadas del ciclo 2. **Un mismo punto puede estar formulado por varios Estados y cuenta una vez**; no es el número de «recomendaciones por Estado» de otras bases (p. ej. UPR Info), que da cifras mayores. La leyenda lo dice.
- **Cuándo no se publica cifra:** se sigue la secuencia 1, 2, 3… de cada lista en el orden del texto (el prefijo, `116.x`, a veces trae erratas en el original y no se usa para contar); si la secuencia salta o no hay numeración el informe se descarta y queda en la lista de dudosos de `data/fuentes/epu_recomendaciones.json`, en vez de dar un número falso. A 10-11-2026: 528 de 550 informes de los ciclos 2 a 4 con cifra (96 %); los 22 dudosos son erratas del original (p. ej. `60.513` por `60.153` en Dinamarca 2021) o un formato distinto, y salen «sin cifra». Las remisiones a otros informes («paragraphs 116.28 and 116.111…») no se cuentan.
- **Ciclo 1 (2008–2011):** no se cuenta; numera las recomendaciones de otra forma (1., 2., 3. sueltos) y se confundiría con los párrafos del informe.
- **Ciclos por fecha del informe:** 2.º desde el 01-04-2012, 3.º desde el 01-04-2017, 4.º desde el 01-09-2022.
- **Cómo se renueva** (tras cada sesión del Grupo de Trabajo, tres al año; es manual, porque necesita los textos de ct/129 (sk-atlas) y no corre en Actions): `python3 -I scripts/fetch_epu_informes.py` → `ATLAS_TEXTOS_DIR=/var/lib/atlas/textos python3 -I scripts/texto_completo.py descargar` y `extraer` (o esperar a la pasada de las 03:30, que ya los incluye) → `ATLAS_TEXTOS_DIR=/var/lib/atlas/textos python3 -I scripts/epu_recomendaciones.py` → PR. Nunca dos clientes a la vez contra la Biblioteca Digital.
- **Licencia:** los documentos de la ONU son públicos y solo se publica el número contado, con el símbolo del informe del que sale; el texto no se copia.
- **Pruebas:** `tests/epu_recomendaciones_test.py` (los tres formatos, las remisiones, los huecos y que `data/epu.js` cuadra con la lista de informes) y el bloque «EPU» de `tests/browser.cjs`.

## Lo que falta (en la cola)
- Nada de las capas previstas. Ideas aparte: separar en la capa del EPU lo apoyado de lo tomado en nota (está en las adiciones `/Add.1`).
- Impresión del mapa: hecha con T58 (`tests/impresion.cjs`).
