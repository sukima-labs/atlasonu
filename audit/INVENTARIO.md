# Inventario del ZIP de traspaso (27-oct-2026)

Integridad: 29/29 archivos coinciden con `MANIFIESTO_SHA256_ZIP_ORIGINAL.tsv`.

| Elemento | Hallazgo |
|---|---|
| Versión vigente | `ATLAS_ONU_publicacion/index.html` (62 082 B, v0.6) → ahora `index.html` |
| Datos | 28 mandatos, 11 trazas, 9 alertas, embebidos en el HTML; el Excel `atlas-onu-catalogo.xlsx` (11 hojas) es idéntico byte a byte a `Plataforma_ONU_..._PILOTO` |
| Duplicados | `atlas_v05.js` = script embebido de la v0.6; 3 ZIP previos (CORREGIDO, LISTO_PARA_GITHUB, V06) son versiones anteriores del mismo HTML; `atlas_smoke.html` es una variante del index |
| Prototipos | 2 libros Excel "Tablero" (nomenclatura ES/EN, visual) → `archive/prototipos-xlsx/` |
| Scripts | `build_*`, `extend_*`, `fix_*`, `improve_*`, `rebuild_*`, `make_real_*`, `package_*`, `test_*` en Python; verificadores JS → `scripts/` |
| Excluido del repo público | `Organos de Tratados Octubre 2026.pptx`, `Programa ONU 2026.pdf` (material del máster/UAH, no del autor). Siguen en el ZIP original de Drive |
| Excluido | `vista_tablero.png` (captura antigua) |
| Prueba previa | Chromium "no completada"; ahora completada (ver abajo) |
