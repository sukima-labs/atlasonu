# ATLAS ONU · Plan de diseño UI/UX (11-11-2026)

Revisión hecha por atlas como diseñador UI/UX. Se revisaron las **20 pantallas** de https://sukima-labs.github.io/atlasonu/
en el **Brave de Patricio a 1440 px** y en **celular emulado** (Pixel 7 e iPhone 13 con Playwright, las mismas
condiciones que el workflow «Celular»). También se pasaron las pruebas del repositorio: `tests/accesibilidad.cjs`
(axe, WCAG 2.2 AA) y `tests/auditar_ux.cjs` (medidas a 390 px).

## 1. De dónde sale el trabajo pendiente

| Origen | Qué pide | Estado |
|---|---|---|
| **T85 · #228** (Jeisson: «ese color tierra cansa», «no veo el modo oscuro») | Marca Sukima en **modo claro y oscuro**, selector Automático/Claro/Oscuro | **Decidido: opción D.** Sin empezar: la web sigue con la paleta piedra y dorado |
| **T84 · #226** (Jeisson: «no se ve el manual de marca») | Letra de la marca (`DejaVu Sans`) incluida en el repositorio | Decidido junto con D. Sin empezar |
| **T82 · #222** | Paleta | La cierra la D: se cierra cuando T85 esté publicada |
| **T31 · #242** | Logo provisional de DIGNITYOS en el menú y en su apartado | Pendiente. Falta el archivo limpio |
| **T75 · #203** | Menú «Seguimiento de recomendaciones»: tablero, tabla, comparador de varios países, línea de tiempo, mapa | En cola. Datos de la fase 1 medidos |
| **T76 · #205** | Asistente «Tengo un caso: ¿adónde acudo?», paso a paso, con un resumen que se puede imprimir | En cola. Jeisson quiere las tres partes |
| **T77 · #207** | Guías de quejas como «guía viva», junto al asistente | En cola |
| **T83 · #224** | «Simula una asamblea (aula)»: ficha de delegación y kit del profesor | En cola, después de la fase 1 de T75 |
| **T86 · #249** | Capa «Presencia de la ONU» en el mapa y en la ficha | Falta una fuente con licencia |
| **T33 · #165** | Vista para niños y niñas | **Bloqueada** a la espera de 4 decisiones de Jeisson |
| Patricio, hoy | Que funcione bien en **escritorio y en celular como PWA** | La web **no es instalable**: no hay manifest ni service worker (T58 lo descartó «por ahora») |

Todas las ramas del repositorio están ya fusionadas en `main`: no hay trabajo a medias de nadie.

## 2. Lo que vi: diagnóstico

**Lo que ya está bien (no se toca):** axe da **0 incumplimientos** en 22 pantallas, en ES, EN y AR a 390 px y en ES a 1280 px.
No hay desbordamiento horizontal. El menú en 5 bloques (T78), la portada despejada (T80), las ayudas plegables (T79) y la
impresión en claro (T58) funcionan bien.

### Escritorio (Brave, 1440 px)
1. **Todo es del mismo tono cálido.** Fondo marrón, texto crema, dorado en botones, bordes y títulos: no hay jerarquía de color y cansa la vista (lo que dice Jeisson). Hay 366 colores escritos a mano (189 distintos) y ninguna variable.
2. **Un marco dorado alrededor del título (h1) en cada pantalla.** Es el foco del programa (`[tabindex]:focus-visible`) al cambiar de pantalla. Parece un fallo.
3. **Letra muy pequeña.** En las noticias, el texto va casi todo a 11–12 px (87 de 118 nodos). La letra no se incluye en la web: cada aparato pone la suya, y en Windows sale Segoe.
4. **Iconos del menú con caracteres Unicode** (◫ ▤ ♙ ✦ ⚖ ⛏…). Cada sistema los dibuja distinto, y ✦ sale dos veces (Relatores y DIGNITYOS).
5. **Portada:** 8 tarjetas en «Empieza por aquí», que quedan en una fila de 6 y otra de 2. La nota dice «las 14 secciones», pero el menú tiene 20. En escritorio sale una instrucción para el celular.
6. **Tratados y comités:** 9 tarjetas diminutas en una sola fila y el resto de la pantalla vacío. Es la pantalla más pobre para un tema central.
7. **«Qué falta y qué viene»:** un muro de texto sin estados visuales.
8. **Mezcla de idiomas:** con la interfaz en inglés, las etiquetas del contador siguen diciendo «VISITAS TOTALES», y el «hecho del mes» sale en español sin avisar.
9. **Banderas con emoji:** en Windows no se dibujan y sale «ES Spain».

### Celular (Pixel 7 / iPhone 13)
10. **La primera pantalla se pierde:** el aviso «Para ver más secciones…» (unos 200 px) más el contador de visitas (unos 100 px) más el antetítulo. El contenido empieza a mitad de la pantalla, **y el aviso se repite en todas las pantallas** hasta que se pulsa «Entendido».
11. **Tres franjas de ayuda una tras otra** (Lectura fácil, «Para qué sirve esta pantalla», «Instantánea…») antes del contenido, en casi todas las pantallas.
12. **Páginas larguísimas** (`auditar_ux`, en pantallas de alto): Alertas 29,9 · Relatores 28,5 · Otros mecanismos 24 · Arqueología 18,2 · Explorar 17 · Siglas 16,2 · Países 11,5.
13. **Zonas táctiles pequeñas:** Otros mecanismos tiene 118 controles de menos de 44 px, Arqueología 48 y Alertas 42. El «ⓘ Para qué sirve» mide 21 px de alto.
14. **Dos selectores de idioma** (el de la barra superior y los botones del menú).
15. **Su historia:** 8 botones de periodo apilados antes de llegar a la línea de tiempo.
16. **Explorar mandatos:** 10 filtros a la vista a la vez.
17. **No es PWA:** no se puede instalar, no tiene icono en la pantalla de inicio ni pantalla de arranque, y no abre sin conexión.

## 3. Plan de implementación

Cada fase va en su propio PR, con la CI en verde, «Celular» en verde y capturas de antes y después en el PR. El orden
reduce el riesgo: primero los arreglos sin decisión, después la base (variables) y encima lo visual.

### Fase 0 · Arreglos rápidos (1 PR, sin cambio de identidad)
- Quitar el marco del h1 al cambiar de pantalla (`h1[tabindex="-1"]:focus{outline:none}`); el foco sigue llegando al lector de pantalla.
- La nota de la portada cuenta las secciones del menú en lugar de llevar un «14» fijo, y en escritorio no se muestra la instrucción del celular.
- «Empieza por aquí» con una cuadrícula de 4×2 en escritorio y de 2 columnas en el celular.
- Etiquetas del contador traducidas en los 6 idiomas; banderas con el código del país en una pastilla (o en SVG) en lugar del emoji.
- El aviso «Para ver más secciones» sale **una sola vez** (solo en la portada, y se recuerda en el navegador). Después basta un pulso suave en el botón «Menú».
- En el celular, un solo selector de idioma (el de la barra superior), y en el menú solo un enlace.
- «ⓘ Para qué sirve» y los enlaces sueltos con 44 px de zona táctil.
- Con la interfaz en otro idioma, el contenido en español lleva la marca «(en español)».

### Fase 1 · Variables de diseño (T85, fase 1)
- Pasar los 366 colores a **variables** (`--fondo`, `--superficie`, `--texto`, `--texto-2`, `--acento`, `--borde`, `--dato-1…n`), más una escala de letra y otra de espacios.
- **Sin cambio visible.** Prueba: las capturas de las 20 pantallas tienen que salir iguales que antes (diferencia de píxeles 0).
- **Hecho (11-11-2026).** Un solo bloque `:root` al principio de la hoja con unas 260 variables por grupos: marca, fondo y superficies, texto, acento y enlaces, bordes, botón principal, estados, lectura fácil, historia, paleta de datos (`--dato-1…13`), mapa (`--mapa-*`), gráficas de votos (`--grafica-*`, `--voto-*`), transparencias (`--x-rgb`, que se usan como `rgba(var(--x-rgb),alfa)`), letra (`--fs-*`) y espacios (`--esp-*`, de momento solo en los `gap`). El mapa y las gráficas toman sus colores de las variables (la escala de cifras del mapa lee `--mapa-escala-0` y `--mapa-escala-9`).
  - Prueba: 73 capturas salen iguales píxel a píxel (diferencia 0). Son las 22 pantallas a 1440×900 y en un Pixel 7, las 8 capas del mapa, dos fichas de país, la pantalla de error de carga, el menú del celular y la vista de impresión; además, las tres gráficas de votos de dos países. En la vista de impresión hay a veces 33 píxeles con 1 o 2 niveles de diferencia en el borde derecho: es el suavizado de la letra, y también pasa entre dos capturas de la página original.
  - Colores que siguen escritos a mano: los del bloque de impresión (7) y los del marco del celular y del `theme-color` de la cabecera (4, se tocan en la fase 3).
  - **Los tonos casi iguales no se fundieron.** Se probó a fundir los 52 pares con ΔE < 2 (las letras -b, -c… de superficies, textos y bordes), y eso cambia hasta 10 niveles por canal en 69 de las 73 capturas. Como la fase 2 cambia todos esos valores, se funden allí.

### Fase 2 · Marca en modo oscuro y su letra (T85 fase 2 + T84)
- Oscuro sobre grafito `#10131C`: superficies de grafito en escalones, texto marfil `#F5F4F0`, acento cian `#14C6D4` y violeta `#7148F5` solo como relleno de botón con letra blanca. El dorado sale de la página y queda solo en datos y mapas.
- **DejaVu Sans dentro del repositorio** (woff2 recortado a latín, cirílico y árabe, con `font-display: swap`); para el chino, la letra del sistema. La jerarquía la dan el peso y el tamaño, porque la serifa desaparece.
- Escala de letra: el cuerpo pasa de 14 a **16 px** en el celular y a 15 px en escritorio; el texto secundario no baja de 13 px.
- Botón principal en violeta con letra blanca (5,3:1) y secundario con borde cian. El foco, un anillo cian visible.
- **Hecho (12-11-2026).** El `:root` pasa a la marca y se funden los tonos casi iguales de la fase 1 (de 274 variables a 175). La letra va en `assets/fonts/` (4 woff2 recortados, 146 KB en total; en español se cargan 2, unos 116 KB, y los de árabe solo con texto árabe), con `font-display: swap` y sin peticiones externas. Los textos de menos de 13 px pasan de unos 2.900 nodos a 0 (medido en las 22 pantallas a 390 y a 1440 px). **Excepción:** los rótulos de los ejes de las gráficas SVG (años y 0/50/100 en «Cómo vota en la Asamblea General»). La gráfica se encoge con la pantalla y sus letras con ella, así que en el celular se ven más pequeñas; agrandarlas haría que se monten sobre las barras. Cada gráfica trae debajo su tabla con los mismos números en letra normal; se revisa en la fase de gráficas. El menú lateral pasa de 260 a 288 px y los rótulos de grupo se aprietan menos, para que ninguna entrada ni rótulo se parta en dos líneas. Los iconos que DejaVu no tiene (ⓘ, ⌕, ⏸) se cambian por ℹ, ⚲ y ❚❚, que sí están en la letra recortada. Los campos de texto y las listas llevan un borde propio (`--borde-campo`, 3:1 o más sobre los fondos donde aparecen) y el contorno cian de los botones secundarios pasa a `#23949F` (3,5:1 o más sobre todas las superficies). El `theme-color`, el marco del celular y las pantallas de carga y sin JavaScript van en grafito. axe sigue en 0.
  - Queda para otras fases: las cifras de los ejes de las gráficas de votos (texto SVG de 11 unidades, que en el celular se ve pequeño) y los iconos Unicode del menú (fase 4).

### Fase 3 · Modo claro y selector (T85 fase 3)
- Claro sobre marfil `#F5F4F0` con texto grafito. El cian para texto pasa a `#0A6E78` (5,4:1), el violeta a `#5B35D6` y el ocre para datos a `#7A4E0E`.
- Selector **Automático / Claro / Oscuro** en la barra superior y en el menú. Por defecto sigue al aparato (`prefers-color-scheme`), y la elección se guarda solo en el navegador.
- Mapas, gráficas y leyendas con una paleta para cada modo. El `theme-color` cambia con el modo, para que la barra del celular vaya a juego. La impresión sigue en claro.

### Fase 4 · Iconos y logo
- Un **juego de iconos SVG propio** en línea (trazo de 2 px, el mismo estilo que el botón «Menú») para las 20 entradas del menú, las tarjetas y los botones. Así se ven igual en Windows, Android e iOS. Ninguno se repite.
- **T31:** logo provisional de DIGNITYOS en SVG dentro del repositorio (cuadrado redondeado con degradado azul a verde, una «D» y un escudo con visto), en el menú, en la franja de la portada y en su apartado. Se sustituye con un solo archivo cuando llegue el definitivo.

### Fase 5 · Distribución en el celular y pantallas largas
- **Contador de visitas** en una sola línea compacta (o al pie de la página en el celular): deja libres unos 100 px arriba.
- **Las ayudas juntas en una franja**: una fila con «Lectura fácil · Para qué sirve · Fecha de los datos», y cada una se despliega al tocarla.
- **Listas paginadas**: Relatores, Alertas, Otros mecanismos, Arqueología, Explorar, Siglas y Países muestran 20 elementos y un botón «Mostrar 20 más». Llevan el recuento («20 de 236») y los filtros pegados arriba. La búsqueda y las descargas siguen usando todos los datos.
- **Otros mecanismos y Arqueología**: en el celular, cada fila de la tabla pasa a ser una tarjeta con botones de 44 px.
- **Explorar mandatos**: 3 filtros principales y un botón «Más filtros (7)».
- **Su historia**: los periodos pasan a ser una fila de pastillas que se desliza en horizontal.
- **Tratados y comités**: cuadrícula de 3×3 (1 columna en el celular) con tarjetas más grandes, cuántos Estados son parte y una barra de ratificación.
- **Qué falta y qué viene**: tarjetas con una pastilla de estado (Hecho, En curso, Pendiente, Bloqueado) y un filtro.
- Una **barra inferior en el celular** con las 4 entradas que más se usan (Inicio, Buscar, Países, Mapa) más «Menú». Es **opcional**: cambia la navegación, así que antes se lo enseño a Jeisson con capturas.

### Fase 6 · PWA instalable
- `manifest.webmanifest` con nombre, iconos de la marca (192, 512 y *maskable*), `display: standalone` y los colores de los dos modos; meta para iOS (`apple-touch-icon`, que ya existe).
- **Service worker «primero la red»**: con conexión siempre sirve lo último (HTML y `data/*.js`) y solo tira de la copia si no hay red. Así se evita el riesgo que hizo descartar la PWA en T58 (datos viejos después de la revisión diaria). Sin caché de la búsqueda en vivo.
- Un aviso discreto de «Sin conexión: datos del <fecha>» cuando se use la copia.
- Pruebas: Lighthouse PWA (instalable), un arranque sin red en Playwright y comprobar que, después de publicar, la web carga la versión nueva.

### Fase 7 · Componentes para lo que viene de Jeisson (T75, T76, T77, T83, T86)
Se construyen ya sobre las variables nuevas, para que esas pantallas nazcan con la marca y no haya que rehacerlas:
- **Pastilla de estado con su fuente** («Apoyada · según A/HRC/…», «Sin información»), para el tablero de T75 y para «Qué falta».
- **Comparador de varios países** (columnas fijas y desplazamiento horizontal en el celular), para T75 y T83.
- **Asistente paso a paso**: barra de pasos, una pregunta por pantalla, «Atrás», y un resumen que se imprime. Para T76 y T77, con la franja «En pruebas».
- **Línea de tiempo compacta** de una recomendación entre ciclos (T75).
- **Ficha de delegación imprimible** (T83).
- La capa «Presencia de la ONU» del mapa (T86) usará la paleta de datos de los dos modos en cuanto haya fuente con licencia.

Los datos y contenidos de cada una de esas tareas siguen su propio orden en la cola. Lo que cambia es que su interfaz ya
sale con estos componentes. **T33 (infancia)** no entra hasta que Jeisson conteste #165.

### Fase 8 · Medir y cerrar
- `tests/browser.cjs` y `tests/accesibilidad.cjs` corren en **los dos modos**; `impresion.cjs`, `movil_real.cjs` y `auditar_ux.cjs` también.
- Objetivo medible: **axe 0** en claro y en oscuro. Ninguna página del celular pasa de unas 8 pantallas de alto sin paginar. No queda ningún control de menos de 44 px fuera del texto corrido. El texto no baja de 13 px.
- Capturas de antes y después (escritorio y celular, claro y oscuro) en cada PR. Se actualizan `docs/INFORME_UX.md`, `assets/marca/README.md`, la cola y la pantalla «Qué falta y qué viene».
- Al terminar se cierran #222, #226, #228 y #242 con su prueba.

## 4. Riesgos y decisiones
- **Presentación:** las fases 1–3 cambian toda la imagen. Si la presentación es pronto, se publican de 0 a 2 (oscuro con la marca) y el claro sale después. **Dime la fecha si la hay.**
- **Barra inferior en el celular (fase 5)** y **paginación**: son cambios de navegación, así que se los enseño a Jeisson con capturas antes de fusionar.
- **PWA (fase 6):** reabre la decisión de T58 porque lo pides tú. El service worker «primero la red» la resuelve, pero si prefieres solo el manifest (instalable, sin uso sin conexión), se queda en eso.
- **Logo de DIGNITYOS:** lo hago provisional. Si Jeisson tiene el SVG, se cambia un archivo.
