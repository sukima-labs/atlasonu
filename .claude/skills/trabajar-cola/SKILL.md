---
name: trabajar-cola
description: Modo continuo de ATLAS ONU. Hace las tareas de docs/COLA_DE_TAREAS.md una tras otra (rama, pruebas, commit, push, PR, fusión con CI en verde, marcar hecha) sin pedir /clear entre tareas, decide por su cuenta lo que haga falta y no para hasta que la cola esté vacía o bloqueada de verdad. Úsala cuando el fundador diga «haz las tareas», «sigue con la cola» o «en automático».
---

# Trabajar la cola (ATLAS ONU)

Autorización permanente del fundador (31-10-2026): decidir por tu cuenta lo necesario, fusionar PRs con CI en verde, crear ramas y commits, y no parar hasta terminar la cola. No hace falta pedir `/clear` entre tareas en este modo. Respeta las reglas fijas de `docs/COLA_DE_TAREAS.md` (gratis, abierto, privado; lista de comprobación de interfaz; lo bloqueado por fuentes oficiales no se toca).

## Bucle (repetir hasta vaciar la cola)
1. **Elegir:** la primera tarea «pendiente» según el orden de «Orden decidido por el asistente» en la cola. Si una tarea depende de la mano del fundador (`sudo`, celular real, Funnel), se deja anotada en la lista corta y se pasa a la siguiente.
2. **Rama:** `git checkout -b tNN-tema` desde `main` actualizado (`git pull --ff-only`).
3. **Hacer:** cambios mínimos y con verificación por lectura. Si al hacer la tarea falta algo (un error, un dato, una pantalla rota, una idea necesaria), **añádelo a la cola** como nueva tarea (T54, T55…) y sigue.
4. **Probar:** `node tests/smoke.cjs` y `node tests/invariantes.cjs` (en el mini PC, con salida a un archivo en la carpeta de trabajo). `browser.cjs` solo si está instalado Playwright; si no, dilo en el cierre.
5. **Cola:** marcar la tarea **hecha** con fecha y una línea de qué se hizo; actualizar «Siguiente tarea».
6. **Pantalla «Qué falta y qué viene»:** si la tarea cambia lo que se ve, actualizar `data/hoja_ruta.json` según `cerrar-tarea`.
7. **Commit y subida:** commit con identidad `Jeisson Arley Osorio Mesa <jeissonosorio10@gmail.com>` y las líneas de atribución de la sesión; `git push -u`; `gh pr create`; esperar el CI con `gh pr checks <n> --watch`.
8. **Fusionar:** si el CI está en verde, `gh pr merge <n> --squash` (sin borrar ramas en el mismo comando).
9. Volver al paso 1.

## Cuando hay bloqueo
- **Decide** la opción más sensata, anótala en la tarea de la cola y sigue. No te detengas por dudas de estilo o alcance.
- Si una prueba falla, corrige una vez; si sigue fallando, deja la tarea en «en evaluación» con el motivo exacto y pasa a la siguiente.
- Si el CI falla por algo ajeno, anótalo y pasa a la siguiente.
- Solo paras si: la cola está vacía, todo lo restante depende de la mano del fundador, o una acción está fuera de lo autorizado (por ejemplo, exponer un servicio nuevo o publicar el repositorio). Ver `docs/COLA_DE_TAREAS.md` y la memoria del proyecto.
- Si el clasificador de permisos bloquea una acción (por ejemplo, borrar ramas remotas), no la rodees: anótalo, sigue con lo demás y repórtalo al final.

## Al terminar
- Dejar la carpeta limpia y en `main`.
- Enviar un aviso al fundador con `PushNotification` (una frase: tareas hechas, PRs fusionadas, qué quedó pendiente y por qué).
- Resumen corto en el chat: tareas hechas con su PR, tareas en evaluación, lo que espera su mano, y lo que el clasificador de permisos bloqueó.
