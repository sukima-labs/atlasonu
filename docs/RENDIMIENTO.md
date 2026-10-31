# Rendimiento y uso sin conexión (medido el 31-10-2026)

## Qué descarga la página al abrirse
| Archivo | Tamaño | Comprimido (gzip) | Cuándo se carga |
|---|---|---|---|
| `data/atlas-data.js` | 1,39 MB | 169 KB | al abrir: contiene el catálogo que usan todas las pantallas |
| `data/comunicaciones.js` | 10,5 KB | — | al abrir la pantalla que lo necesita |
| `data/jurisprudencia.js` | 17,6 KB | — | al abrir su pantalla |
| `data/catalogo.json` | 1,75 MB | 180 KB | **no lo carga la página**: es la fuente que genera `atlas-data.js` y el Excel |

Las pantallas de países, votaciones y jurisprudencia ya se cargan bajo demanda. El resto del catálogo va dentro de `atlas-data.js`, así que hoy el peso de arranque es ese archivo.

## Conclusiones
- **El catálogo ya no es el problema de la tarea original:** la página no carga `catalogo.json` (1,7 MB). El archivo que pesa al abrir es `atlas-data.js`, 169 KB comprimidos, que Pages sirve comprimido.
- **Diferir `atlas-data.js` no se hace ahora.** Todas las pantallas leen ese objeto global al arrancar; separarlo por pantallas toca el código de todas ellas y no se puede probar aquí (falta Playwright para `tests/browser.cjs`). Se registra como T58.
- **Service worker (PWA): no ahora.** Un *service worker* con caché puede servir datos viejos después de una revisión diaria; la página ya usa un parámetro de versión por cada 5 minutos. Hay que decidir la estrategia antes de añadirlo.
- **Modo impresión:** la hoja de estilos ya oculta menús y controles al imprimir (`@media print`). No se ha comprobado una impresión completa de cada pantalla; se incluye en T58.
- **Conexión lenta:** no se ha medido (requiere navegador con red limitada). Pendiente con T55 (Playwright).
