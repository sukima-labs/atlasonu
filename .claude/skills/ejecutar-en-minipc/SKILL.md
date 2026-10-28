---
name: ejecutar-en-minipc
description: Regla del fundador para ATLAS ONU: todo programa, prueba, script o descarga se ejecuta en el mini PC (esta máquina, DIGNITYOS) y en segundo plano con la salida a un archivo, para no gastar tokens leyendo salidas largas. Úsala antes de ejecutar cualquier comando que no sea trivial.
---

# Ejecutar en el mini PC, sin gastar tokens (ATLAS ONU)

Pedido del fundador (28-10-2026): «siempre que ejecutes algo, hazlo en el mini PC, no gastes tokens a lo tonto».

Esta carpeta ya vive en el mini PC (`~/Documentos/atlas-onu`), así que **ejecutar aquí es ejecutar en el mini PC**. Lo que hay que evitar es traer la salida entera a la conversación.

## Reglas
1. **Todo lo que tarde o imprima mucho** (pruebas, `build_*`, `fetch_*`, `verify_symbols`, `subir_tarea.sh`, descargas) va con `run_in_background` y con la salida a un archivo del scratchpad: `cmd > <scratchpad>/x.log 2>&1`. Luego leer solo `tail -n 5` o un `grep` de fallos.
2. **Nunca imprimir** JSON grandes, catálogos ni listados completos: usar `python3 -I - <<E` que imprima solo cifras o diferencias, y `cut -c1-200`.
3. **No esperar con sondeos** ni repetir lecturas: un solo aviso de fin, una sola lectura de la cola del registro.
4. **Agrupar** pasos independientes en un único comando (build → pruebas → commit) y mirar solo el resultado final.
5. **Pruebas de navegador** (`tests/browser.cjs`, Playwright) y cualquier cosa pesada: en el mini PC o en el CI; no pegar sus capturas ni su salida completa.
6. Seguir las reglas de siempre: ramas, nada de `sudo` ni Funnel por mi cuenta, carpeta limpia al terminar (el temporizador hace `reset --hard origin/main`).
