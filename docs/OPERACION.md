# Operación: quién publica los datos y cuándo

Hay dos automatizaciones que actualizan `data/` en `main`. Este documento dice cuál manda y por qué.

| Qué | Cuándo (hora de España) | Dónde corre | Qué hace |
|---|---|---|---|
| `atlas-onu.timer` (mini PC) | 00:00 y 12:00, con hasta 2 min de retraso aleatorio | `scripts/mini_pc/actualizar_local.sh` | `fetch` y `reset --hard origin/main`, revisa las fuentes, sube solo `data/` si hay cambios y hace `push` directo. Si el `push` falla, deja el repositorio igual que `origin/main` y no reintenta |
| `actualizar-datos.yml` (GitHub Actions) | 00:17 y 12:17 en invierno (13:17 y 01:17 en verano) | `scripts/actualizar_datos.sh` en `ubuntu-latest` | revisa las fuentes, confirma solo `data/`, hace `pull --rebase` y `push`, y pide a Pages que reconstruya el sitio |

## Qué manda
- **Manda el mini PC.** Su revisión corre antes que la de Actions en invierno y en verano, así que suele llegar primero.
- **Actions es respaldo.** Si el mini PC está apagado o sin red, Actions revisa igual. Como rebasa antes de subir, convive con un `push` previo del mini PC sin perder cambios.
- Ninguno de los dos toca el código: solo `data/`.

## Riesgo conocido
Si ambos encuentran cambios a la vez, el segundo `push` puede fallar o rebasar sobre el primero. El mini PC no reintenta, así que sus cambios se recogerán en la siguiente ejecución. Se vigila en T54.

## Pruebas de navegador en el mini PC
Playwright no va en `package.json` (el repositorio no tiene dependencias). Se instala sin guardarlo en el proyecto y se fija a la misma versión que el CI (`.github/workflows/pruebas.yml`):

```
npm i --no-save playwright@1.64.1 && npx playwright install chromium
node tests/browser.cjs > <carpeta de salida>/browser.txt 2>&1
```

`node_modules/` está en `.gitignore`. Comprobado el 31-10-2026: 199 comprobaciones, 0 fallos (T64).

Relacionado: `docs/COLA_DE_TAREAS.md`, `scripts/mini_pc/instalar.sh`.
