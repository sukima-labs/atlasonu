# ATLAS ONU — Arqueología documental de Naciones Unidas

Plataforma académica independiente para investigar los procedimientos especiales de la ONU y recuperar sus documentos originales **con verificación contra la fuente oficial**.

**Autor y titular:** Sukima-Labs · © 2026. Todos los derechos reservados; publicar el código no concede una licencia abierta (pendiente de decisión del autor).
**Aviso:** iniciativa académica independiente. No es un producto oficial de Naciones Unidas ni de la Universidad de Alcalá.

## Qué hace la versión 0.7
- **57 mandatos vigentes** (44 temáticos y 13 por país) tomados del índice oficial de OHCHR, con titulares actuales.
- **421 actos jurídicos** (creación, prórrogas) contrastados uno a uno con la Biblioteca Digital de la ONU: 401 localizados, 20 con reservas explicadas.
- **Ruta al texto de las 400 resoluciones localizadas:** 374 con PDF propio (comprobado leyendo su primera página; muestreo del registro 30/30) y 26 antiguas reproducidas en un informe de sesión, con páginas (p. ej. `E/CN.4/RES/1985/33` → `E/1985/22`, pp. 71–72).
- **25 mecanismos conexos** verificados: los 10 órganos de tratados (datos de la diapositiva del curso de la UAH), EPU, procedimientos 1235 y 1503, EMRIP, Foro de Minorías, ACNUDH y 8 comisiones de investigación / misiones.
- **Búsqueda inteligente** en la portada: entiende sinónimos ES/EN («desaparecidos», «comida», «niños migrantes»), corrige erratas («tortrua») y muestra, mientras escribes, mandatos, resoluciones y mecanismos relacionados con acceso directo a la ficha o al texto.
- **Búsqueda guiada** para quien no conoce la ONU, filtro de verificación, Excel descargable (`data/atlas-onu-catalogo-v07.xlsx`).
- **Arqueología documental real:** una resolución se localiza aunque el símbolo esté mal escrito (`A/HRC/54/26`, `E/CN.4/1991/42`, `20 (XXXVI)`), un borrador `L.` se traduce a la resolución adoptada y la ficha enlaza el registro y los PDF en español e inglés.
- **Distingue resolución, informe y borrador.** Si un símbolo existe pero es un informe, lo dice. Si una equivalencia es inferida, lo dice.
- **Un caso con texto leído:** la resolución 20 (XXXVI) de 1980 (Grupo de Trabajo sobre Desapariciones) está reproducida en E/1980/13, pp. 180–181; se leyó el PDF (`data/evidencias.json`).

## Abrir
Abrir `index.html` en cualquier navegador (también sin conexión: los datos van en `data/atlas-data.js`).
**Web pública:** https://sukima-labs.github.io/onu-arqueologia-documental/ (Settings → Pages → *Build and deployment* → Source: **Deploy from a branch** → Branch: `main`, carpeta `/ (root)` → Save; tarda ~1 minuto).

## Estructura
| Ruta | Contenido |
|---|---|
| `index.html` | Aplicación |
| `data/` | `catalogo.json` y `atlas-data.js` (generados), `fuentes/` (descargas oficiales y verificación), `evidencias.json`, Excel del piloto |
| `scripts/` | Descarga, normalización, verificación y construcción (`actualizar_datos.sh` ejecuta todo) |
| `tests/` | `smoke.cjs` (42 pruebas de lógica) y `browser.cjs` (Chromium real, 36 comprobaciones, escritorio y móvil) |
| `audit/` | Auditoría contra los 13 requisitos, discrepancias respecto a v0.6, inventario, manifiesto de integridad |
| `docs/` | Traspaso original |
| `archive/` | Versiones previas sin modificar |

## Reproducir
```
bash scripts/actualizar_datos.sh        # regenera datos (necesita red)
cd tests && node smoke.cjs               # lógica
npm i playwright && node tests/browser.cjs   # navegador real
```

## Límites (ver `audit/AUDITORIA.md`)
Solo mandatos **vigentes**: faltan los extinguidos. Las comisiones de investigación listadas son una selección verificada, no el universo. No hay mapas. Las explicaciones en lenguaje claro de cada resolución no están redactadas. «Localizado» significa que existe un registro con ese símbolo exacto; no sustituye leer el texto.
