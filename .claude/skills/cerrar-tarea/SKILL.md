---
name: cerrar-tarea
description: Cierre de cada tarea de ATLAS ONU antes de pedir /clear. Sincroniza la cola de tareas y la pantalla «Qué falta y qué viene» con lo hecho, lo que está en evaluación, lo pendiente y las ideas nuevas.
---

# Cerrar tarea (ATLAS ONU)

Úsala al terminar cada tarea, **antes** de decirle al fundador que escriba `/clear`. La pantalla «Qué falta y qué viene» (`#hojaruta` en `index.html`) y `docs/COLA_DE_TAREAS.md` tienen que contar lo mismo y estar al día.

## Pasos
1. **Cola:** marca la tarea como **hecha** con fecha y una línea de qué se hizo; actualiza «Siguiente tarea». Añade como tarea nueva (T30, T31…) toda idea, error o pedido del fundador que haya surgido en la sesión, aunque no se vaya a hacer ya.
1b. **Issues (T89, 11-11-2026):** cada tarea abierta de la cola tiene un issue con su T-número en el título, y el estado lo da el issue: se cierra cuando la tarea está hecha, no antes. Un PR que solo valora o deja algo en cola usa `Refs #n`, **nunca** `Closes #n` (si no, GitHub cierra el issue solo). Tarea nueva sin issue: se crea en el momento. El tablero es el proyecto 4 de la organización: sus automatizaciones (11-11-2026) meten solo cada issue nuevo en «Por hacer» y lo pasan a «Hecho» al cerrarlo. No se copia a mano en ningún otro sitio.
1c. **La pantalla sigue a los issues sola (T90):** el workflow «Qué falta y qué viene al día con los issues» (`.github/workflows/hoja-ruta.yml`, `scripts/hoja_ruta_github.py`) recoloca cada elemento de `data/hoja_ruta.json` según los issues de su campo `"issues"`: abierto → Pendiente; abierto con `en-evaluacion` → En evaluación; abierto y todo `idea` → Ideas; cerrado como hecho → Ya disponible; cerrado como «no se hará» → fuera. Así que **cerrar el issue basta para mover el elemento**; no se mueve a mano. Lo que sí es a mano: el texto. Un elemento nuevo de Pendiente o En evaluación lleva siempre `"issues"` (la prueba `tests/hoja_ruta_github_test.py` lo exige), o bien el issue trae en su cuerpo el bloque oculto `<!-- web` / `t: título` / `x: texto` / `-->` y entra solo. Lo interno se etiqueta `interno` y no sale.
2. **Pantalla `#hojaruta` (el texto):** se edita `data/hoja_ruta.json` (bloques `disponible`, `evaluacion`, `pendiente`, `ideas`; en los textos, `{siglas}`, `{hechos}` y `{previos}` se rellenan solos) y se reconstruye con `python3 -I scripts/build_catalog.py data/fuentes/verificacion_simbolos.json <fecha de data/catalogo.json>`. En lenguaje claro, sin jerga de tareas ni nombres de personas, reparte todo en estos bloques:
   - **Ya disponible** (lo hecho; lo recién terminado entra aquí).
   - **En evaluación** (hecho a medias o a la espera de confirmación del fundador o de una prueba en celular real).
   - **Pendiente** (en la cola, con orden).
   - **Ideas que están entrando** (ideas nuevas sin compromiso ni fecha).
   Cada cifra del texto (siglas, hechos de historia, mandatos…) debe coincidir con la real.
3. **Reservas del fundador:** no publicar lo que pidió mantener en reserva (por ejemplo, el origen académico de DIGNITYOS y el detalle de cómo funciona). Dudas, preguntar.
4. **Pruebas:** `cd tests && node smoke.cjs`, `node tests/invariantes.cjs` y `node tests/browser.cjs`. Revisar la pantalla a 390 px y en escritorio.
5. **Subir:** rama → commit → PR → fusión con el CI en verde. Dejar la carpeta limpia.
6. **Cerrar:** resumen corto y pedir `/clear`.
