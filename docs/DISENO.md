# ATLAS ONU · Sistema de diseño

Este documento explica **cómo se ve ATLAS y con qué piezas se construye**. Sirve para que cualquier pantalla nueva
(el seguimiento de recomendaciones de T75, el asistente «Tengo un caso» de T76, las guías de T77 o la simulación de
asamblea de T83) salga con la marca, en los dos modos de color y accesible desde el primer día, sin rehacer nada.

El plan completo y su historia están en [`PLAN_DISENO_UX.md`](PLAN_DISENO_UX.md). La marca de Sukima está en
[`assets/marca/README.md`](../assets/marca/README.md) y sus colores de origen en `assets/marca/brand_tokens.css`.

Casi toda la interfaz está en **un solo archivo**, `index.html`: las variables y los estilos van en los bloques
`<style>` del principio (los componentes de este documento, en `<style id="estilo-componentes">`) y las funciones
que pintan cada componente, en el `<script>` principal, en el bloque «P8 · componentes».

---

## 1. Variables (colores, letra y espacios)

**Regla de oro: ningún color se escribe a mano.** Todo sale de una variable de `:root`. El modo claro solo cambia el
valor de las variables (`html[data-theme=light]`), así que un componente que usa variables sale bien en los dos modos
sin hacer nada más. La impresión pasa todo a negro sobre blanco por su cuenta.

### Colores principales

| Variable | Para qué | Oscuro | Claro |
|---|---|---|---|
| `--fondo` | Fondo de la página | grafito `#10131C` | marfil `#F5F4F0` |
| `--superficie-1` … `-5` | Tarjetas, paneles, cabeceras de tabla (de más hondo a más alto) | grafitos `#161A26` … `#2C3346` | blancos y marfiles `#FFFFFF` … `#E7E4DC` |
| `--texto` | Texto normal | marfil `#F5F4F0` | grafito `#10131C` |
| `--texto-fuerte` | Títulos | blanco | grafito |
| `--texto-2` … `-6` | Texto secundario, de más a menos fuerte | grises fríos | grises grafito |
| `--enlace`, `--acento` | Enlaces, menú activo, detalles de acento | cian claro `#5CDAE4` / cian `#14C6D4` | petróleo `#0A6E78` |
| `--foco` | Anillo de foco del teclado | cian `#14C6D4` | petróleo `#0A6E78` |
| `--primario-1` | Relleno del botón principal (con letra blanca) | violeta `#7148F5` | violeta `#7148F5` |
| `--borde-1` … `-4` | Líneas y bordes | | |
| `--borde-campo` | Borde de campos de texto y opciones (3:1 o más) | `#6B7693` | `#6E7484` |
| `--exito-*`, `--aviso-*`, `--peligro-*`, `--neutro-*` | Estados (hecho, en curso, problema, neutro) | | |
| `--dato-1` … `-13`, `--mapa-*`, `--grafica-*`, `--ocre` | **Solo datos**: mapas, gráficas, leyendas | | |

**Decisión de #228 (opción D):** la página va con la marca Sukima (grafito, marfil, cian y violeta) en los dos modos.
El dorado y el ocre ya **no** son color de página: quedan solo para datos y mapas.

### Letra

- **DejaVu Sans**, incluida en el repositorio (`assets/fonts/`, con su licencia). El chino usa la letra del sistema.
- Escala (`--fs-*`): nota 13 px · secundaria 14 · base 15 (16 en el celular) · media 16 · grande 17 · destacada 18 ·
  subtítulo 20 · sección 24 · título 30–38.
- **Ningún texto baja de 13 px.** La jerarquía la dan el tamaño y el peso (600–800), no la serifa ni el color.

### Espacios

- Escala `--esp-1` … `--esp-10`: 2, 4, 6, 8, 10, 12, 14, 16, 18 y 20 px. Los huecos entre piezas (`gap`) salen de ahí.
- Zonas táctiles: **44 px** de alto como mínimo para todo lo que se toca fuera del texto corrido (botones, pastillas
  de filtro, enlaces de tarjetas). En el celular la página deja libre el alto de la barra inferior.

### Iconos

- Un juego propio de 21 iconos SVG de trazo 2 px, definidos una sola vez al principio del `<body>` (`<symbol id="i-…">`):
  `i-panorama`, `i-noticias`, `i-seleccion`, `i-buscar`, `i-relatores`, `i-paises`, `i-mapa`, `i-tratados`,
  `i-mecanismos`, `i-arqueologia`, `i-sistema`, `i-historia`, `i-siglas`, `i-recuperar`, `i-datos`, `i-alertas`,
  `i-hojaruta`, `i-descargas`, `i-fuentes`, `i-info`, `i-comparar`.
- Se usan así: `<svg class="ic" aria-hidden="true" focusable="false"><use href="#i-mapa"/></svg>`. Son **decorativos**:
  el texto de al lado dice lo que hace el botón. No se usan emojis ni símbolos Unicode como iconos (cada sistema los
  dibuja distinto).

---

## 2. Componentes

Cada componente tiene una función que devuelve su HTML. Los textos de la interfaz van en español y los traduce
`assets/idiomas.js`; los datos (símbolos de documentos, nombres de países) no se traducen.

### 2.1 Pastilla de estado con su fuente — `pastilla(estado, texto, fuente)`

Dice **en qué estado está algo y quién lo dice**: «Apoyada · según A/HRC/52/10», «Pendiente · según #261»,
«Sin información».

```js
pastilla('ok', 'Apoyada', { t: 'A/HRC/52/10', url: 'https://digitallibrary.un.org/…' })
pastilla('neutro', 'Pendiente', { t: '#261', url: 'https://github.com/sukima-labs/atlasonu/issues/261', etiqueta: 'Tarea #261 en GitHub' })
pastilla('parcial', 'Corregido', { html: 'según <a href="…">Biblioteca Digital</a>' })  // frase de interfaz: va entera en el diccionario
pastilla('nd')                                                                        // «Sin información»
```

| Estado | Para qué | Marca (además del color) |
|---|---|---|
| `ok` | Hecho, apoyada, exacto | punto lleno |
| `parcial` | Corregido, en parte | medio punto |
| `aviso` | En curso, prioridad media, revisar | triángulo |
| `mal` | Bloqueado, rechazada, prioridad alta | cuadrado |
| `neutro` | Pendiente, tomó nota, prioridad baja | punto hueco |
| `nd` | Sin información (borde de rayas) | raya |

Reglas:
- **El estado nunca va solo por el color**: siempre lleva su palabra y su marca.
- **La fuente es lo que permite comprobarlo.** Si hay documento, se enlaza. Si no hay dato, se pone «Sin información»
  (`pastilla('nd')`); **nunca se rellena un estado que no está en la fuente**.
- La fuente `{t, url}` es un símbolo o un número y no se traduce; `{html}` es una frase de interfaz que sí se traduce
  (hay que añadirla entera a los diccionarios).
- `etiqueta` (opcional) es el nombre del enlace para el lector de pantalla cuando el texto visible no basta
  («#261» → «Tarea #261 en GitHub»). Va en los diccionarios (con `{n}` en lugar de la cifra).
- En el celular, el enlace de la fuente mide 44 px de alto sin mover nada (relleno transparente que se pinta por
  encima de lo que sigue, para que todo el área responda al dedo).
- **La palabra del estado nunca se parte.** En una tabla, la celda del estado lleva `class="td-est"` (ancho mínimo
  de 9,5em). Si la fila ya tiene un enlace al mismo registro, la pastilla va **sin fuente**: no se repite el enlace.
- Se usa hoy en **Qué falta y qué viene** (estado de cada tarea y su issue de GitHub) y en **Alertas de cotejo**
  (prioridad de cada alerta y estado de cada número; ahí la fuente es el enlace «Registro» de la misma fila).

### 2.2 Comparador de varios países — `comparador({cols, filas, cab, etiqueta, vacio})`

Pone países lado a lado. La **primera columna (el aspecto) se queda fija** y el resto se desliza de lado.

```js
comparador({
  etiqueta: 'Comparación entre países', cab: 'Aspecto',
  cols: [esc(a.es), esc(b.es), esc(c.es)],                       // ya escapados
  filas: [{ h: 'Grupo regional', v: ['…', '…', '…'], dif: true }],  // dif: la fila cambia entre países (raya de acento)
  vacio: 'En estos aspectos los dos países están igual.'
})
```

Reglas:
- Con **uno o dos países** la tabla cabe entera también en el celular (las columnas se reparten el ancho).
- Con **tres o más**, en el celular se desliza de lado dentro de su caja (nunca la página entera) y aparece la pista
  «Desliza de lado para ver todas las columnas.». Después de pintarlo, llama a `cmpxDesborda()`.
- La caja es una región con nombre. **Solo cuando hay algo que deslizar** `cmpxDesborda()` le da `tabindex="0"`, así
  que se desliza con las flechas del teclado; si cabe entera, no añade una parada inútil al tabulador.
- En el celular, el resaltado de la fila bajo el puntero solo existe con ratón (`@media (hover:hover)`): con el dedo
  se quedaría pegado a la última fila tocada.
- Cada fila lleva su aspecto como cabecera de fila (`<th scope="row">`): el lector de pantalla lo lee con cada dato.
- Ya lo usan **«Comparar con otro país»** en la ficha de país (dos países) y **«Seguimiento de recomendaciones»** (T75, hasta seis). T83 lo usará con más.

### 2.3 Asistente paso a paso — `asistente(caja, {pasos, resultado, enPruebas, aviso})`

Una pregunta por vista, barra de pasos, «Atrás» y un resumen que se puede imprimir. Para T76 y T77.

```js
const a = asistente(document.getElementById('miCaja'), {
  pasos: [
    { titulo: 'Corto', pregunta: '¿…?', ayuda: 'Texto opcional', opciones: [['valor1', 'Texto 1'], ['valor2', 'Texto 2']] },
    …
  ],
  resultado: R => '<p>…</p>',   // HTML del final, según las respuestas R
  enPruebas: true               // franja «En pruebas» (por defecto, sí)
});
a.ir(0); a.respuestas();
```

Reglas:
- **Una sola pregunta por vista**, con opciones grandes (48 px) de las que se elige una.
- Si se pulsa «Siguiente» sin elegir, avisa «Elige una opción para seguir.» y lleva el foco a las opciones. Las
  opciones quedan con `aria-invalid="true"` y `aria-describedby` apuntando al aviso; al elegir, se quitan.
- Al cambiar de paso, **el foco va a la pregunta nueva**, para que el lector de pantalla la lea.
- «Atrás» recuerda lo que se había elegido. El resumen tiene «Cambiar las respuestas», «Empezar de nuevo» e
  «Imprimir el resumen» (se imprime solo el asistente, con su franja «En pruebas»).
- **Mientras una herramienta esté en pruebas, lleva la franja.** Su aviso por defecto es «Esta herramienta está en
  pruebas: comprueba siempre la información en la fuente oficial.»
- Las preguntas, las opciones y el resultado son **contenido**: siguen las reglas de su tarea (T76, T77) y van en los
  diccionarios de idiomas. Hoy **ninguna pantalla usa el asistente**; se prueba con una muestra en
  `tests/componentes.cjs`.

### 2.4 Línea de tiempo compacta — `lineaCompacta(lista, etiqueta)`

Una recomendación a lo largo de los ciclos del EPU (T75): cada punto es un ciclo con su fecha y su pastilla.

```js
lineaCompacta([
  { ciclo: 'Ciclo 2', fecha: '2012', est: 'ok', txt: 'Apoyada', fuente: { t: 'A/HRC/…', url: '…' } },
  { ciclo: 'Ciclo 3', fecha: '2017', est: 'nd' },                // sin dato: «Sin información»
  { ciclo: 'Ciclo 4', fecha: '2022', est: 'nd', actual: true },  // el ciclo en curso
], 'La recomendación en cada ciclo')
```

En escritorio va en horizontal; en el celular, en vertical. Cada estado sale con su fuente, igual que la pastilla.
Un ciclo sin dato se pone con `est: 'nd'`, **nunca se deja fuera ni se rellena**. `actual: true` marca el ciclo en
curso: su punto va relleno y lleva `aria-current="step"` para el lector de pantalla (solo uno por línea).
Dentro de la línea, una pastilla que ocupa dos líneas tiene esquinas de 12 px en vez de cápsula.

### 2.5 Ficha de delegación imprimible — `fichaDelegacion({pais, codigo, sub, bloques, pie})`

Una ficha por país para la simulación de asamblea (T83). Cabe en media hoja A4 y no se parte al imprimir.

```js
fichaDelegacion({
  pais: 'Colombia', codigo: 'COL', sub: 'América Latina y el Caribe',
  bloques: [{ t: 'Grupo regional', html: '<p>…</p>' }, { t: 'Notas', html: '<span class="fd-linea"></span>', ancho: true }],
  pie: 'Fuentes: …'
})
```

- `ancho: true` hace que un bloque ocupe las dos columnas. `<span class="fd-linea"></span>` deja una línea para
  escribir a mano.
- Para imprimir solo la ficha, un botón debajo de ella:
  `<button type="button" class="btn" onclick="imprimirSolo(this.previousElementSibling)">Imprimir la ficha</button>`
  (el texto «Imprimir la ficha» ya está en los diccionarios). Al imprimir, la página marca el camino hasta ella y la hoja de impresión
  oculta todo lo demás; al terminar de imprimir, la pantalla vuelve a estar entera.
- Los datos de la ficha salen de ATLAS (con su fuente en el pie). Los textos de la simulación son de T83.

### 2.6 Imprimir una parte — `imprimirSolo(elemento)` y `marcarImpresion(elemento)`

`imprimirSolo` imprime solo ese elemento (el resumen de un asistente, una ficha). `marcarImpresion` deja la página
preparada sin abrir el diálogo y devuelve la función que lo deshace (la usan las pruebas).

---

## 3. Contraste (medido con las variables reales)

WCAG pide 4,5:1 para texto normal y 3:1 para bordes de campos y letra grande.

| Pareja | Oscuro | Claro |
|---|---|---|
| Texto sobre fondo | 16,9 | 16,9 |
| Texto secundario más suave (`--texto-6`) sobre tarjeta | 6,6 | 8,9 |
| Enlace sobre fondo | 11,1 | 5,4 |
| Botón principal: blanco sobre violeta | 5,3 | 5,3 |
| Pastilla «ok» | 9,9 | 6,9 |
| Pastilla «parcial» | 9,4 | 8,1 |
| Pastilla «aviso» | 10,2 | 6,8 |
| Pastilla «mal» | 8,3 | 7,1 |
| Pastilla «neutro» | 9,2 | 10,2 |
| Borde de campos y opciones | 3,8 | 4,7 |
| Anillo de foco sobre fondo | 8,9 | 5,4 |

**Combinaciones prohibidas:**
- Violeta como texto sobre grafito (3,5:1). El violeta va **solo** como relleno de botón con letra blanca. En claro, si
  hace falta violeta de texto, `--violeta-texto` (`#5B35D6`).
- Cian puro como texto sobre marfil (1,9:1). En claro, el texto de acento es `#0A6E78`.
- Ocre de datos sobre marfil: en claro, `#7A4E0E`.

`tests/accesibilidad.cjs` pasa axe en las 22 pantallas en los dos modos y `tests/componentes.cjs` pasa axe en todos
los componentes: **0 incumplimientos** es la regla.

---

## 4. Sí y no

| Sí | No |
|---|---|
| Usar las variables (`var(--superficie-2)`) | Escribir colores a mano (`#1A1F2C`) |
| Estado con palabra, marca y fuente (`pastilla`) | Un punto de color sin palabra |
| «Sin información» cuando no hay dato | Rellenar un estado, una fecha o una cifra que no están en la fuente |
| Iconos del juego propio, decorativos | Emojis o símbolos Unicode como iconos |
| 44 px para todo lo que se toca | Enlaces o botones diminutos fuera del texto corrido |
| Texto de 13 px o más | Letra pequeña para que «quepa» |
| Tablas anchas dentro de su caja deslizable | Que la página entera se desplace de lado |
| Cada texto nuevo de interfaz en los 5 diccionarios | Dejar texto en español con la interfaz en otro idioma |
| Violeta solo de relleno con letra blanca | Violeta como texto sobre grafito |
| Un aviso «En pruebas» en lo que está en pruebas | Presentar como definitivo lo que no está validado |

---

## 5. Cómo se añade una pantalla

1. **Sección.** Un `<section id="mi-pantalla" class="section">` dentro de `.main`, con su antetítulo
   (`<div class="eyebrow">`), su `<h1>` y su `<p class="intro">`. Las ayudas («Lectura fácil», «Para qué sirve esta
   pantalla») siguen el mismo formato que las demás.
2. **Menú.** Su botón en el bloque que le toque de `#nav`, con un icono del juego propio que no se repita. Si es de las
   más usadas, se valora para la barra inferior del celular (hoy: Inicio, Buscar, Países, Mapa y Menú).
3. **Piezas.** Primero las que ya existen: tarjetas (`.panel`, `.metric`), botones (`.btn`, `.btn.primary`), filtros
   en fila (`.toolbar`), listas de 20 en 20 con «Mostrar 20 más», y los componentes de este documento.
4. **Colores.** Solo variables. Si hace falta un color nuevo, se añade como variable en `:root` **y** en
   `html[data-theme=light]`, y se mide su contraste.
5. **Textos.** Todo texto visible nuevo, en la plantilla `idiomas/es.json`; sus traducciones, en `idiomas/<ln>.json`
   (o en Weblate) y `python3 -I scripts/idiomas.py` regenera `data/idiomas/*.js` (ver `docs/TRADUCCIONES.md`).
6. **Datos.** Cada cifra o estado, con su fuente. Lo que no se sabe se dice («Sin información»).
7. **Pruebas.** `tests/browser.cjs`, `tests/accesibilidad.cjs` (axe en los dos modos), `tests/impresion.cjs` (la
   pantalla se imprime sola y en pocas hojas) y `tests/componentes.cjs`. Capturas de antes y después, en escritorio y
   en celular, en claro y en oscuro, en el PR.
