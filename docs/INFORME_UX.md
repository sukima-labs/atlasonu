# Informe de UX de las pantallas (T15, 28-10-2026)

Medido con Chromium a 390 × 844 px sobre las 17 pantallas del menú. Ninguna se desborda de lado (el cuerpo mide 390 px); los fallos están dentro de las pantallas.

## Qué se midió y qué salió
| Pantalla | Fondo de página (en pantallas) | Tabla / ancho real | Controles < 32 px | Texto < 12 px |
|---|---|---|---|---|
| Inicio | 5,4 | — | 7 | 8 |
| Noticias | 6,7 | — | 24 | 3 |
| Explorar mandatos | 22,4 | 786 px en 364 | 6 | 117 |
| Cómo funciona la ONU | 4,2 | — | 4 | 3 |
| Historia | 3,3 | — | 4 | 78 |
| Países | **50,8** | 770 px en 364 | 3 | **528** |
| Tratados y comités | 2,3 | — | 3 | 3 |
| Siglas | 16,8 | — | 3 | 63 |
| Arqueología | 40,7 | 926 px en 364 | **546** | 195 |
| Recuperar | 3,1 | — | 3 | 3 |
| Otros mecanismos | 12,7 | 1056 px en 364 | 108 | 88 |
| Codificación | 3,4 | 770 px en 364 | 15 | 15 |
| Selección | 2,5 | — | 10 | 3 |
| Auditoría | 47,4 | 770 y 797 px en 330–364 | 77 | 171 |
| Qué falta y qué viene | 7,2 | — | 3 | 11 |
| DIGNITYOS | 2,4 | — | 3 | 3 |
| Fuentes | 5,5 | — | 10 | 3 |

## Hallazgos priorizados
1. **Tablas anchas en el celular (alta).** Seis pantallas (Explorar, Países, Arqueología, Otros mecanismos, Codificación, Auditoría) usan tablas de 770–1056 px dentro de 364 px: se desplazan de lado y se pierde la columna «Texto» o «Acto de la ONU». Es el caso que describió el fundador. Arreglo: por debajo de ~600 px, pasar cada fila a **tarjeta** (etiqueta: valor) con el mismo HTML y CSS, sin duplicar datos.
2. **Objetivos táctiles pequeños (alta).** Arqueología tiene 546 controles de menos de 32 px y Otros mecanismos 108; Noticias 24. Lo recomendable son 44 px (mínimo 24 px en WCAG 2.2 AA). Arreglo: altura mínima de 44 px en botones, enlaces de tabla y filtros solo en pantallas táctiles (`@media (pointer:coarse)`).
3. **Texto menor de 12 px (media).** Países (528 elementos), Auditoría (171), Arqueología (195) y Explorar (117). Subir el mínimo a 13–14 px en móvil.
4. **Listas muy largas (media).** Países (51 pantallas) y Auditoría (47) obligan a bajar muchísimo. Arreglo: paginar o «Ver más», y botón «↑ Arriba» general (hoy solo existe en la ficha de país, T19).
5. **«Sin enlace directo verificado» repetido (media).** 12 veces en Otros mecanismos. Arreglo: una sola nota arriba («los que no llevan enlace aún no están verificados») y en la fila solo un guion.
6. **Buscador a mano (media).** Hay buscador en Explorar, Siglas, etc., pero no uno global siempre visible; en el celular conviene una lupa fija en la barra superior que abra la búsqueda de cualquier pantalla.
7. **Orientación «dónde estoy» (baja).** El menú marca la pantalla actual (T34), pero la barra superior no la nombra; añadir el título de la pantalla junto al botón del menú.
8. **Estados vacíos y de carga (baja).** Comprobar los mensajes de «sin resultados» en cada filtro y el de la búsqueda en vivo (hoy corta a 10 s sin explicar qué hacer).

## Propuesta de orden (una pantalla por commit)
1. Tarjetas en móvil para las seis tablas (hallazgo 1) — la más pedida.
2. Tamaño táctil y tipografía mínima (2 y 3) — un solo cambio de CSS que beneficia a todas.
3. Mecanismos: nota única de «sin enlace» (5).
4. Paginación de Países y Auditoría + «↑ Arriba» global (4).
5. Título de pantalla en la barra y lupa global (6 y 7).
6. Estados vacíos (8).

## Pendiente de confirmar en el celular real
Medido con navegador de escritorio emulando 390 px; falta confirmarlo en un Android real (ver T12 y T28).
