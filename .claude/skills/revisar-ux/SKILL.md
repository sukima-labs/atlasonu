---
name: revisar-ux
description: Revisión de UX y calidad de código de ATLAS ONU con apoyo de Claude Code. Mide las pantallas a 390 px, corrige los fallos por orden de prioridad (uno por commit) y cierra con la skill cerrar-tarea. Úsala cuando el fundador pida mejorar la interfaz o corregir errores de UX.
---

# Revisar UX (ATLAS ONU)

1. **Medir:** `node tests/auditar_ux.cjs > salida.txt`, con Playwright instalado como dice `docs/OPERACION.md`. Compara con `docs/INFORME_UX.md` (valores de partida del 28-10-2026).
2. **Elegir:** el siguiente paso pendiente del informe. Un paso, un commit.
3. **Corregir** con el estilo del código vecino. Las tablas pasan a tarjetas en móvil con `etiquetarTablas()`: no duplicar datos.
4. **Probar:** `node tests/smoke.cjs`, `node tests/invariantes.cjs`, `node tests/browser.cjs`, y la lista de comprobación de interfaz de `docs/COLA_DE_TAREAS.md` (360–412 px, horizontal, zoom 200 %, texto grande, botón atrás). Mirar una captura a 390 px.
5. **Registrar:** actualizar la tabla de `docs/INFORME_UX.md` con los números nuevos y cerrar con `cerrar-tarea`.

Reglas: gratis, abierto y privado (sin servicios externos); nada del TFM ni del detalle de DIGNITYOS; no pedir al fundador que ejecute comandos (trabaja desde el celular).
