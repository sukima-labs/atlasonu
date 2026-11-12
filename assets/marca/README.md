# Marca Sukima Labs en ATLAS ONU

Copia de la parte estable de la marca de Sukima Labs, versión **v1.1** («Logotipo 04»). La copia de referencia vive
en el repositorio de la marca de Sukima Labs; lo que hay aquí es una copia.

| Fichero | Origen en la marca v1.1 | Uso en ATLAS |
|---|---|---|
| `favicon.ico`, `favicon_16.png`, `favicon_32.png` | `03_DIGITAL/Web/` | icono de la pestaña |
| `apple_touch_icon_180.png` | `03_DIGITAL/Avatares/` | icono al guardar la web en el móvil |
| `isotipo_white.svg` | `01_LOGO/SVG/` | isotipo del pie del menú lateral (en línea en `index.html`) |
| `isotipo_color.svg` | `01_LOGO/SVG/` (vector maestro) | referencia; sobre el fondo oscuro de ATLAS no se ve, por eso se usa el blanco |
| `brand_tokens.css`, `brand_tokens.json` | `03_DIGITAL/Web/` | variables `--sukima-*` en el `:root` de `index.html`, de las que salen el fondo, el texto, el acento y la letra |

**ATLAS sigue la marca (desde la fase 2 del plan de diseño, `docs/PLAN_DISENO_UX.md`).** La paleta piedra y dorado de
antes se retiró (issue #228, opción D). El modo oscuro usa ahora los colores de la marca: fondo grafito `#10131C`,
superficies en escalones de grafito, texto marfil `#F5F4F0`, cian `#14C6D4` para enlaces, menú activo y anillo de foco,
y violeta `#7148F5` **solo** como relleno del botón principal, con letra blanca (5,3:1). El violeta no se usa como texto
sobre grafito (3,5:1). El ocre y el dorado quedan solo como colores de datos (mapas, gráficas y temas de la historia).
El título «ATLAS ONU» se mantiene; la palabra «ONU» va en cian.

**Modo claro (fase 3) y selector.** Sobre marfil `#F5F4F0` con texto grafito. El cian puro no se usa como texto sobre
marfil (1,9:1): los enlaces y el acento van en cian oscuro `#0A6E78`, el texto violeta en `#5B35D6` y el ocre de los datos
en `#7A4E0E`. El botón principal sigue en violeta `#7148F5` con letra blanca. En el menú lateral hay un selector
**Automático / Claro / Oscuro**: «Automático» sigue al aparato y las otras dos opciones se recuerdan en el navegador.

**Medido al cerrar el plan (fase 8, 12-11-2026).** En los dos modos: 0 incumplimientos de axe-core (WCAG 2.2 A/AA), ningún
texto de menos de 13 px y ningún control de menos de 44 px fuera del texto corrido en el celular (390 px). La tabla de
antes y después está en `docs/INFORME_UX.md`; el sistema de componentes, en `docs/DISENO.md`.

**Letra.** `DejaVu Sans`, la de la marca, va incluida en el repositorio (`assets/fonts/`, normal y negrita en woff2, con
su licencia en `assets/fonts/LICENSE-DejaVu.txt`). Está recortada a latín, griego, cirílico, árabe y los símbolos de la
interfaz: quien lee en español carga unos 116 KB y el árabe se descarga aparte solo cuando hace falta. No hay peticiones
a servicios de letras de terceros. El chino usa la letra del sistema. Se quitaron los títulos con serifa: la jerarquía la
dan el peso y el tamaño.

La autoría sigue escrita «Sukima-Labs», como pide el proyecto.

**Eslóganes de la marca** (no se muestran en la web; queda a decisión del proyecto):
- Institucional: «El espacio donde nacen nuevas posibilidades.»
- De posicionamiento: «Donde otros ven un vacío, nosotros vemos posibilidades.»

**Límites.** El isotipo es una reconstrucción geométrica hecha desde una imagen; no hay vector original. No es una
marca registrada y estos ficheros no sirven para producción impresa. Los signos de la marca identifican a Sukima Labs:
quien reutilice ATLAS no debe usarlos para dar a entender que Sukima Labs respalda su versión.

Si la marca publica una versión nueva, se actualizan estos ficheros desde la nueva versión; aquí no se editan a mano.

## Iconos de la interfaz (fase 4 del plan de diseño)

Los iconos del menú, de las tarjetas de la portada, de los recuadros «Para qué sirve esta pantalla» y de algunos botones
son dibujos propios de ATLAS ONU: trazos de 2 px con los extremos redondeados, en una cuadrícula de 24 × 24, del mismo
estilo que el botón «Menú». Están una sola vez al principio de `index.html` (un `<svg>` con un `<symbol id="i-…">` por
icono) y cada sitio los usa con `<use href="#i-…">`. Toman el color del texto, así que sirven en claro y en oscuro, y se
ven igual en Windows, Android e iOS (antes eran símbolos de texto que cada sistema dibujaba a su manera). Son
decorativos: los lectores de pantalla no los leen, porque el nombre ya va escrito al lado. En el menú no se repite
ninguno.

## Logo provisional de DIGNITYOS (T31)

`dignityos_provisional.svg` es un logo **provisional** hecho para ATLAS: un cuadrado redondeado con un degradado de azul
a verde, una «D» blanca y un pequeño escudo con una marca de visto. Sale en la entrada «DIGNITYOS» del menú, en la franja
de la portada y en la cabecera de su apartado, con el texto alternativo «Logo provisional de DIGNITYOS».

**No es el logo definitivo.** Cuando llegue el definitivo, basta con sustituir este archivo por el nuevo (un SVG cuadrado
con el mismo nombre); no hay que tocar nada más.
