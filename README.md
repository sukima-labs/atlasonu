# ATLAS ONU — Arqueología documental de Naciones Unidas

Plataforma académica independiente para investigar los procedimientos especiales de la ONU y localizar sus documentos originales.

**Autor y titular:** Jeisson Arley Osorio Mesa · © 2026. Todos los derechos reservados; publicar el código no concede una licencia abierta (pendiente de decisión del autor).
**Aviso:** no es un producto oficial de Naciones Unidas ni de la Universidad de Alcalá.

## Abrir
Abrir `index.html` en cualquier navegador (sin instalación). Para la web pública: GitHub Pages, rama y carpeta raíz.

## Estructura
| Ruta | Contenido |
|---|---|
| `index.html` | Aplicación (v0.6): catálogo de muestra, búsqueda ES/EN, trazas históricas, recuperación documental |
| `data/` | Catálogo Excel descargable |
| `tests/` | `smoke.cjs` (lógica, sin navegador) y `browser.cjs` (Chromium real) |
| `audit/` | Manifiesto de integridad, resultados de pruebas, inventario y auditoría contra requisitos |
| `docs/` | Traspaso original con los 13 requisitos |
| `scripts/` | Scripts de construcción previos (referencia) |
| `archive/` | Versiones previas conservadas sin modificar |

## Pruebas
```
cd tests && node smoke.cjs      # 14 pruebas de lógica
npm i playwright && node tests/browser.cjs   # 24 comprobaciones en Chromium (escritorio y móvil)
```

## Estado
Ver `audit/AUDITORIA.md`: qué cumple y qué falta, sin declarar cobertura que no existe. Hoy el catálogo es una **muestra de 28 mandatos**, no el universo completo.
