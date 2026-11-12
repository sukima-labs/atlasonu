# Operación: quién publica los datos y cuándo

Desde el 06-11-2026 una sola automatización actualiza `data/` en `main`: GitHub Actions. El mini PC ya no ejecuta nada del proyecto.

| Qué | Cuándo (hora de España) | Dónde corre | Qué hace |
|---|---|---|---|
| `actualizar-datos.yml` (GitHub Actions) | 00:17 y 12:17 en invierno (13:17 y 01:17 en verano) | `scripts/actualizar_datos.sh` en `ubuntu-latest` | revisa las fuentes, confirma solo `data/`, hace `pull --rebase` y `push`, y pide a Pages que reconstruya el sitio |

No toca el código: solo `data/`.

**Lo que la revisión no consulta (T56, 12-11-2026):** lo que prohíben los `robots.txt`: `digitallibrary.un.org/search`,
`documents.un.org/api` y todo `ap.ohchr.org`. La verificación de símbolos (`verify_symbols.py`) y la localización de
textos (`resolve_texts.py`) trabajan sin red sobre su resultado anterior. Un símbolo nuevo queda «Sin cotejar todavía»
(`SIN_CONSULTAR`), con su aviso en el catálogo, hasta que una persona lo coteje. `BIBLIOTECA_SEARCH=si` vuelve a buscar en
la Biblioteca Digital, y solo se usa a mano y con permiso. De la Biblioteca Digital se bajan registros concretos
(`/record/N`) a 5 s como mínimo. Su OAI-PMH solo tiene el conjunto «sanctions» y no sirve para descubrir documentos.

**El ACNUDH (#313, decidido por Patricio el 12-11-2026):** `spinternet.ohchr.org` (lista de mandatos y visitas) y
`spcommreports.ohchr.org` (comunicaciones) dicen `Disallow: /` en su `robots.txt`. La revisión diaria ya no los lee:
se conservan los datos de la última lectura, con su fecha. Se pide permiso por escrito al ACNUDH; hasta tenerlo,
`OHCHR_SP=si` (que vuelve a leerlos) no se usa.

## Antes (historia, hasta el 06-11-2026)
Había un segundo publicador, `atlas-onu.timer` en el mini PC (`scripts/mini_pc/actualizar_local.sh`, 00:00 y 12:00), que corría antes que Actions y hacía `push` directo; Actions era el respaldo. Se retiró: no se vuelve a instalar ni se usa como respaldo.

## Pruebas de navegador en un clon
Playwright no va en `package.json` (el repositorio no tiene dependencias). Se instala sin guardarlo en el proyecto y se fija a la misma versión que el CI (`.github/workflows/pruebas.yml`):

```
npm i --no-save playwright@1.64.1 && npx playwright install chromium
node tests/browser.cjs > <carpeta de salida>/browser.txt 2>&1
```

`node_modules/` está en `.gitignore`. Comprobado el 31-10-2026: 199 comprobaciones, 0 fallos (T64).

Relacionado: `docs/COLA_DE_TAREAS.md` y, como historia, `docs/MINI_PC.md`.
