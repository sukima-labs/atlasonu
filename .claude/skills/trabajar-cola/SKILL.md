---
name: trabajar-cola
description: Hace la siguiente tarea de docs/COLA_DE_TAREAS.md de principio a fin (rama, pruebas, commit, push, PR, fusión con CI en verde, marcar hecha), por fases si es grande, decide por su cuenta lo que haga falta y al fusionar cierra la sesión: una tarea por sesión. Úsala cuando el fundador diga «haz las tareas», «sigue con la cola» o «en automático».
compatibility: Requiere git, gh autenticado en GitHub, Node.js y Python 3, en un clon de sukima-labs/atlasonu.
---

# Trabajar la cola (ATLAS ONU)

Autorización permanente del fundador (31-10-2026): decidir por tu cuenta lo necesario, fusionar PRs con CI en verde, crear ramas y commits, y llevar la tarea hasta el final sin preguntar. **Una tarea por sesión** (Sukima-Labs, 12-11-2026, #291; manda sobre la autorización de seguir hasta vaciar la cola, aprobado por Patricio el 23-11-2026): las fases de una misma tarea van en la misma sesión; al fusionar la tarea, se cierra la sesión (en Claude Code, `/clear`) y la siguiente empieza en una sesión nueva. Respeta las reglas fijas de `docs/COLA_DE_TAREAS.md` (gratis, abierto, privado; lista de comprobación de interfaz; lo bloqueado por fuentes oficiales no se toca).

## Punto de partida
- Trabaja siempre desde `main` actualizado (`git checkout main && git pull --ff-only origin main`). No dependas de ramas sin fusionar: si una PR anterior sigue abierta, no la uses como base; anótala y sigue.
- Antes de empezar, `git status` debe estar limpio. Si no, no empieces: anótalo y pregunta.

## Pasos (una tarea)
1. **Elegir:** la primera tarea «pendiente» según «Orden decidido por el asistente» en la cola. Si depende de la mano del fundador (`sudo`, celular real, Funnel, permisos que el clasificador bloquea), va a la lista corta y se elige la siguiente.
2. **Rama:** `git checkout -b tNN-tema` desde `main`.
3. **Hacer:** cambios mínimos, verificados por lectura. Si falta algo (un dato, una pantalla rota, un error, una idea necesaria), **añádelo a la cola** como T54, T55… y sigue. Las decisiones de política (por ejemplo, qué flujo manda cuando dos automatizaciones publican lo mismo) se toman, se documentan en `docs/OPERACION.md` y se anotan en la fila de la tarea.
4. **Probar:**
   - `node tests/smoke.cjs` y `node tests/invariantes.cjs`, con salida a la carpeta de scratchpad de la sesión, no a `/tmp` ni a `$HOME`.
   - Navegador: nunca la batería completa de `browser.cjs` en local; solo una comprobación pequeña de la pantalla tocada. La batería completa la corre la CI.
5. **Cola:** marca la tarea **hecha** con fecha y una línea. Recalcula «Siguiente tarea» a partir del orden decidido; no la escribas a mano.
6. **Cambios visibles:** si cambia lo que se ve o la versión, actualizar `data/hoja_ruta.json` (ver `cerrar-tarea`) y `CHANGELOG.md`.
7. **Commit y subida:** `git commit` con la identidad ya configurada en la máquina (el historial es público: ni correos personales ni el nombre de nadie como autor de ATLAS, que figura solo como de Sukima-Labs) y **sin** líneas de atribución (ni `Co-Authored-By` ni «Generated with…»: el agente no figura como contribuidor en sukima-labs); `git push -u`; `gh pr create`. Esperar el CI **una sola vez** con `gh pr checks <n> --watch --interval 20 > <scratchpad>/ci.txt` (no uses `sleep`: está bloqueado).
8. **Fusionar:** si el CI está en verde, `gh pr merge <n> --merge --delete-branch` **en una llamada sola**, sin encadenarlo con otros comandos (si el clasificador lo bloquea, toda la cadena se pierde).
9. **Cerrar:** skill `cerrar-tarea` y fin de la sesión. No se empieza otra tarea.

## Permisos bloqueados por el clasificador
Probado el 31-10-2026: se bloquearon `gh pr merge` (aunque el fundador lo autorizó), `git push --delete` en lote y encadenar comandos con merge.
- Intenta la acción autorizada **una sola vez**, en su propia llamada. Si se bloquea, no la repitas, no la rodees con otro comando equivalente.
- Anótala en la cola como «pendiente de permiso» con el número de PR o la lista de ramas, y deja la tarea en ese punto. En la sesión siguiente se elige otra que no la necesite.
- Borrado de ramas remotas: no se intenta más de una vez por sesión. Va al resumen final.

## Cuando hay bloqueo
- **Decide** la opción más sensata, anótala en la tarea y sigue. No te detengas por dudas de estilo o alcance.
- Prueba fallida: corrige una vez; si sigue, «en evaluación» con el motivo exacto, y se cierra la sesión.
- CI fallido por causa ajena: anótalo y sigue.
- Solo paras antes de fusionar si: la cola está vacía, la tarea depende de la mano del fundador, o la acción queda fuera de lo autorizado (exponer un servicio nuevo, publicar el repositorio, hacer público el repo).

## Al terminar
- Deja la carpeta limpia y en `main` (`git status` vacío; sin stash olvidados).
- Resumen en el chat: la tarea hecha con su PR, en evaluación, lo que espera su mano, y lo que el clasificador bloqueó (con el comando exacto que el fundador puede ejecutar o la regla de permiso que puede añadir).
