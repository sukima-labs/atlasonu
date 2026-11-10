# Accesibilidad e inclusión (T27)

Medido el 10-11-2026 sobre las 19 pantallas del menú, con herramientas libres y sin servicios externos.

## Cómo se mide
- **`tests/accesibilidad.cjs`** pasa [axe-core](https://github.com/dequelabs/axe-core) (reglas WCAG 2.0, 2.1 y 2.2,
  niveles A y AA) por cada pantalla a 390 px (celular) y a 1280 px (escritorio), en español y en inglés. Corre en la CI
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

## Lo que axe no puede medir (queda en la cola)
- **Lector de pantalla real** (NVDA, TalkBack, VoiceOver): axe comprueba nombres y estructura, no la experiencia de uso.
- **Lectura fácil**: hecha en cuatro pantallas (T65); falta la revisión de una persona.
- **Árabe, chino y ruso**: el árabe necesita además la página de derecha a izquierda (T66).
- **Conexión lenta y celulares modestos**: medido en T49, ver `docs/RENDIMIENTO.md`.
