---
name: trabajar-cola
description: Modo continuo de ATLAS ONU. Hace las tareas de docs/COLA_DE_TAREAS.md una tras otra (rama, pruebas, commit, push, PR, fusión con CI en verde, marcar hecha) sin pedir /clear entre tareas, decide por su cuenta lo que haga falta y no para hasta que la cola esté vacía o bloqueada de verdad. Úsala cuando el fundador diga «haz las tareas», «sigue con la cola» o «en automático».
---

# Trabajar la cola (ATLAS ONU)

Autorización permanente del fundador (31-10-2026): decidir por tu cuenta lo necesario, fusionar PRs con CI en verde, crear ramas y commits, y no parar hasta terminar la cola. No hace falta pedir `/clear` entre tareas en este modo. Respeta las reglas fijas de `docs/COLA_DE_TAREAS.md` (gratis, abierto, privado; lista de comprobación de interfaz; lo bloqueado por fuentes oficiales no se toca).

## Punto de partida
- Trabaja siempre desde `main` actualizado (`git checkout main && git pull --ff-only origin main`). No dependas de ramas sin fusionar: si una PR anterior sigue abierta, no la uses como base; anótala y sigue.
- Antes de empezar, `git status` debe estar limpio. Si no, no empieces: anótalo y pregunta.

## Bucle (repetir hasta vaciar la cola)
1. **Elegir:** la primera tarea «pendiente» según «Orden decidido por el asistente» en la cola. Si depende de la mano del fundador (`sudo`, celular real, Funnel, permisos que el clasificador bloquea), va a la lista corta y se pasa a la siguiente.
2. **Rama:** `git checkout -b tNN-tema` desde `main`.
3. **Hacer:** cambios mínimos, verificados por lectura. Si falta algo (un dato, una pantalla rota, un error, una idea necesaria), **añádelo a la cola** como T54, T55… y sigue. Las decisiones de política (por ejemplo, qué flujo manda cuando dos automatizaciones publican lo mismo) se toman, se documentan en `docs/OPERACION.md` y se anotan en la fila de la tarea.
4. **Probar:**
   - `node tests/smoke.cjs` y `node tests/invariantes.cjs`, con salida a la carpeta de scratchpad de la sesión, no a `/tmp` ni a `$HOME`.
   - `browser.cjs` solo si Playwright está instalado (`node -e "require('playwright')"`). Si no, dilo en el cierre y añade una tarea a la cola para instalarlo.
5. **Cola:** marca la tarea **hecha** con fecha y una línea. Recalcula «Siguiente tarea» a partir del orden decidido; no la escribas a mano.
6. **Cambios visibles:** si cambia lo que se ve o la versión, actualizar `data/hoja_ruta.json` (ver `cerrar-tarea`) y `CHANGELOG.md`.
7. **Commit y subida:** commit con identidad `Jeisson Arley Osorio Mesa <jeissonosorio10@gmail.com>` y las líneas de atribución de la sesión; `git push -u`; `gh pr create`. Esperar el CI con `gh pr checks <n> --watch --interval 20 > <scratchpad>/ci.txt` (no uses `sleep`: está bloqueado).
8. **Fusionar:** si el CI está en verde, `gh pr merge <n> --squash` **en una llamada sola**, sin encadenarlo con otros comandos (si el clasificador lo bloquea, toda la cadena se pierde). Nunca borres ramas en el mismo comando.
9. Volver al paso 1.

## Permisos bloqueados por el clasificador
Probado el 31-10-2026: se bloquearon `gh pr merge` (aunque el fundador lo autorizó), `git push --delete` en lote y encadenar comandos con merge.
- Intenta la acción autorizada **una sola vez**, en su propia llamada. Si se bloquea, no la repitas, no la rodees con otro comando equivalente.
- Anótala en la cola como «pendiente de permiso» con el número de PR o la lista de ramas, y sigue con la siguiente tarea que no la necesite. Un bloqueo no detiene la cola.
- Borrado de ramas remotas: no se intenta más de una vez por sesión. Va al resumen final.

## Cuando hay bloqueo
- **Decide** la opción más sensata, anótala en la tarea y sigue. No te detengas por dudas de estilo o alcance.
- Prueba fallida: corrige una vez; si sigue, «en evaluación» con el motivo exacto y siguiente tarea.
- CI fallido por causa ajena: anótalo y sigue.
- Solo paras si: la cola está vacía, todo lo restante depende de la mano del fundador, o la acción queda fuera de lo autorizado (exponer un servicio nuevo, publicar el repositorio, hacer público el repo).

## Al terminar
- Deja la carpeta limpia y en `main` (`git status` vacío; sin stash olvidados).
- Aviso al fundador: carga primero la herramienta con `ToolSearch` (`select:PushNotification`) y envía una frase con tareas hechas, PRs fusionadas y lo pendiente.
- Resumen en el chat: tareas hechas con su PR, en evaluación, lo que espera su mano, y lo que el clasificador bloqueó (con el comando exacto que el fundador puede ejecutar o la regla de permiso que puede añadir).
