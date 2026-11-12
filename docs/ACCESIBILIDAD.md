# Accesibilidad e inclusión (T27)

Medido el 10-11-2026 sobre las pantallas del menú (20 entonces; desde el 11-11-2026 las pruebas recorren las 22 secciones), con herramientas libres y sin servicios externos.

## Cómo se mide
- **`tests/accesibilidad.cjs`** pasa [axe-core](https://github.com/dequelabs/axe-core) (reglas WCAG 2.0, 2.1 y 2.2,
  niveles A y AA) por cada pantalla a 390 px (celular) y a 1280 px (escritorio), en español, en inglés y en árabe (de derecha a izquierda). Corre en la CI
  (`.github/workflows/pruebas.yml`) y falla con un solo incumplimiento, así que lo arreglado no vuelve a romperse.
- `tests/movil_real.cjs` comprueba en tres teléfonos emulados el toque, el deslizamiento del menú y el zoom 2×.

## Resultado
| Criterio WCAG | Antes | Ahora | Qué se cambió |
|---|---|---|---|
| 4.1.2 / 1.3.1 Nombre de los controles | 4 selectores sin nombre (Modalidad, Figura, tipo de traza…) | 0 | Las etiquetas visibles se unen a su control (`for`); el selector y el buscador de Arqueología llevan `aria-label` (traducido a EN y FR) |
| 1.4.1 Uso del color | 4 enlaces que solo se distinguían por el color (1,04:1 con el texto de alrededor) | 0 | Los enlaces dentro de un texto, una lista o una tabla van subrayados |
| 2.5.8 Tamaño del objetivo | 9 enlaces de 18–22 px de alto (Descargas, enlaces de la tabla de trazas) | 0 | Los enlaces sueltos en listas y tablas miden al menos 24 px de alto |
| Contraste (1.4.3), idioma de la página (3.1.1), títulos, tablas, ARIA | 0 | 0 | Ya estaba bien |

Ya estaba hecho y se comprobó: enlace «Saltar al contenido», foco visible (`:focus-visible`), el menú marca la pantalla
actual (`aria-current`), se respeta «reducir movimiento», el zoom no está bloqueado y `lang` cambia con el idioma elegido.

## Modo claro y oscuro (#228)
- `tests/accesibilidad.cjs` mide cada pantalla en los dos modos y, además, la gráfica de votos de un país (barras y línea): las letras de los
  hitos (A, B, C…) deben tener 4,5:1 y el logotipo de Sukima 3:1 con su fondo. axe no mira dentro de los dibujos SVG, por eso se comprueba aparte.
- **Mapa del mundo en claro**: los colores de los países se separan del mar (#DCE7EB) con 2,7:1 como mínimo (el primer escalón de la escala y «sin datos»), no con el 3:1 que pide WCAG 1.4.11 para
  objetos gráficos. Se acepta porque el mapa nunca es la única vía: cada muestra de la leyenda lleva borde oscuro, al tocar un país sale su ficha
  en texto y, debajo del mapa, «Ver los mismos datos como lista» da el dato de la capa elegida para cada país. Subirlo a 3:1 obligaría a oscurecer el mar o a perder escalones de
  la escala; queda como mejora posible, no como fallo. «Sin ficha» (gris oscuro, #3F4552) y «sin conflicto» (violeta) se distinguen también
  por claridad, no solo por tono, y «guerra» (#A82A18) y «conflicto menor» (rosa) se separan con 1,9:1, como en oscuro.

## Lo que axe no puede medir (queda en la cola)
- **Lector de pantalla real** (NVDA, TalkBack, VoiceOver): axe comprueba nombres y estructura, no la experiencia de uso.
- **Lectura fácil**: hecha en cuatro pantallas (T65); falta la revisión de una persona.
- **Árabe, chino y ruso**: hechos (T66), con el árabe de derecha a izquierda; falta que personas nativas revisen las traducciones.
- **Conexión lenta y celulares modestos**: medido en T49, ver `docs/RENDIMIENTO.md`.
