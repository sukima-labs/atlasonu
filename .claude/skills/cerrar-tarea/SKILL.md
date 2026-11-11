---
name: cerrar-tarea
description: Cierre de cada tarea de ATLAS ONU antes de pedir /clear. Sincroniza la cola de tareas y la pantalla «Qué falta y qué viene» con lo hecho, lo que está en evaluación, lo pendiente y las ideas nuevas.
---

# Cerrar tarea (ATLAS ONU)

Úsala al terminar cada tarea, **antes** de decirle al fundador que escriba `/clear`. La pantalla «Qué falta y qué viene» (`#hojaruta` en `index.html`) y `docs/COLA_DE_TAREAS.md` tienen que contar lo mismo y estar al día.

## Pasos
1. **Cola:** marca la tarea como **hecha** con fecha y una línea de qué se hizo; actualiza «Siguiente tarea». Añade como tarea nueva (T30, T31…) toda idea, error o pedido del fundador que haya surgido en la sesión, aunque no se vaya a hacer ya.
1b. **Issues (T89, 11-11-2026):** cada tarea abierta de la cola tiene un issue con su T-número en el título, y el estado lo da el issue: se cierra cuando la tarea está hecha, no antes. Un PR que solo valora o deja algo en cola usa `Refs #n`, **nunca** `Closes #n` (si no, GitHub cierra el issue solo). Tarea nueva sin issue: se crea en el momento. El tablero de GitHub Projects se alimenta de esos issues; no se copia a mano en ningún sitio.
2. **Pantalla `#hojaruta`:** se edita `data/hoja_ruta.json` (bloques `disponible`, `evaluacion`, `pendiente`, `ideas`; en los textos, `{siglas}`, `{hechos}` y `{previos}` se rellenan solos) y se reconstruye con `python3 -I scripts/build_catalog.py data/fuentes/verificacion_simbolos.json <fecha de data/catalogo.json>`. En lenguaje claro, sin jerga de tareas ni nombres de personas, reparte todo en estos bloques:
   - **Ya disponible** (lo hecho; lo recién terminado entra aquí).
   - **En evaluación** (hecho a medias o a la espera de confirmación del fundador o de una prueba en celular real).
   - **Pendiente** (en la cola, con orden).
   - **Ideas que están entrando** (ideas nuevas sin compromiso ni fecha).
   Cada cifra del texto (siglas, hechos de historia, mandatos…) debe coincidir con la real.
3. **Reservas del fundador:** no publicar lo que pidió mantener en reserva (por ejemplo, el origen académico de DIGNITYOS y el detalle de cómo funciona). Dudas, preguntar.
4. **Pruebas:** `cd tests && node smoke.cjs`, `node tests/invariantes.cjs` y `node tests/browser.cjs`. Revisar la pantalla a 390 px y en escritorio.
5. **Subir:** rama → commit → PR → fusión con el CI en verde. Dejar la carpeta limpia.
6. **Cerrar:** resumen corto y pedir `/clear`.
