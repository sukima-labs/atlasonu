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

Cada capa tiene leyenda con las cuentas, la lista de debajo repite los mismos datos (para quien no use el mapa) y la prueba `tests/browser.cjs` comprueba que la leyenda suma los 196 países.

## Cómo está hecho (y por qué sin librería de mapas)
- **SVG propio**, sin MapLibre ni Leaflet: no hay teselas que pedir a nadie, ni cuenta, ni scripts de fuera, no registra a quien lo mira, y pesa 72 KB (`data/mapa.js`) en vez de cientos de KB de librería. Para un mapa de países coloreados no hace falta más.
- **Contornos:** Natural Earth, «Admin 0 – Countries», 1:50 millones, **dominio público** (<https://www.naturalearthdata.com/about/terms-of-use/>). Se simplifican y se proyectan (Miller) con `scripts/generar_mapa.py`, que se puede volver a ejecutar para regenerar `data/mapa.js`. Se descarga una vez; el sitio no carga nada de fuera.
- **Los 196 países de ATLAS** tienen forma o, si son diminutos (35, como Malta o Tuvalu), un círculo. Dos códigos de ATLAS no son el ISO de Natural Earth (`CRO` = Croacia, `RKS` = Kosovo): están en la tabla `ATLAS_A_NE` del script.
- **Lo que no tiene ficha de país** (territorios, Taiwán, Sahara Occidental…) sale como fondo gris y sin clic. Las fronteras son esquemáticas y la pantalla lo dice: ATLAS no opina sobre el estatus de ningún territorio.
- **Accesibilidad:** el dibujo es una imagen con descripción; lo operable es el selector de país, la lista y el panel con el dato (a prueba con axe-core: 0 incumplimientos). El zoom desplaza dentro de su marco, sin desbordar la página (regla de la lista de comprobación de interfaz).

## Informe de licencias para las capas siguientes
| Fuente | Licencia y condiciones | Veredicto |
|---|---|---|
| **Natural Earth** (contornos) | Dominio público; no exige atribución (se cita igualmente). | En uso. |
| **UCDP** (Uppsala Conflict Data Program, conflictos armados) | **CC BY 4.0**: «todos los conjuntos son gratuitos y se pueden usar y redistribuir citando las publicaciones que figuran con cada uno» (<https://ucdp.uu.se/downloads/>, comprobado el 10-11-2026). Sin cuenta. | **Apta** para la capa de conflictos: se cita cada conjunto con su versión y se indica la fecha. |
| **ACLED** (eventos de conflicto) | Exige registro y aceptar sus términos; uso no comercial; limita la redistribución de los datos y el uso con sistemas de IA; el logo es reservado (<https://acleddata.com/terms-and-conditions>, <https://acleddata.com/eula>). | **Descartada**: choca con la regla del proyecto (abierto, sin cuentas, datos reutilizables con CC BY 4.0). |
| **MapLibre GL JS** / **Leaflet** (librerías) | BSD-3-Clause / BSD-2-Clause: libres. | No hacen falta por ahora; se valorarán si algún día se necesitan teselas o un mapa de calor real. |

## Lo que falta (en la cola)
- Capa de **recomendaciones del EPU** por país: hoy ATLAS solo tiene la lista de documentos del EPU de cada país, no el número de recomendaciones; habría que leer los informes.
- Impresión del mapa (junto con T58).
