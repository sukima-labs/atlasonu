# AGENTS.md — ATLAS ONU

Instrucciones para cualquier agente de programación que trabaje en este repositorio (Claude Code, Codex, Gemini CLI,
Cursor, Aider…), según el estándar [AGENTS.md](https://agents.md). Antes de empezar, lee también
`docs/CONTEXTO_PARA_NUEVAS_SESIONES.md`. Si una instrucción del chat contradice este fichero, manda la del chat.

## Proyecto
Catálogo y buscador abierto de documentos oficiales de la ONU. Es una web estática (`index.html`, `sw.js`, `data/`,
`assets/`, `idiomas/`) publicada en GitHub Pages (https://sukimalabs.com/atlasonu/), con una búsqueda en vivo aparte
(`scripts/mini_pc/busqueda_servicio.py`). Los datos se rehacen con scripts de Python en `scripts/`; las pruebas están
en `tests/`. Idioma de trabajo: **español** (código, textos, commits, PR e issues).

### Alcance cerrado (13-11-2026, #337)
ATLAS ONU ya no crece: no se añaden pantallas, menús, conjuntos de datos ni contenido nuevo. Se hace solo mantenimiento
(pruebas, datos automáticos, búsqueda, traducciones, copias), calidad de lo que ya existe (errores, accesibilidad, celular,
revisión de datos y traducciones, privacidad), riesgos (`robots.txt`, #246) y promoción. Una idea que amplíe el producto no
entra en la cola: se anota en #337 y la decide Sukima-Labs. El trabajo pendiente está en `docs/COLA_DE_TAREAS.md`.

## Comandos
- Reconstruir el catálogo tras cambiar datos: `python3 -I scripts/build_catalog.py data/fuentes/verificacion_simbolos.json <fecha>`.
- Textos de la interfaz: `python3 -I scripts/idiomas.py --nuevos` (añade los nuevos a la plantilla) y
  `python3 -I scripts/idiomas.py` (regenera los diccionarios). Comprobación de la CI: `python3 -I scripts/idiomas_textos.py --comprobar`.
- Pruebas: `node tests/smoke.cjs`, `node tests/invariantes.cjs`, `python3 -I tests/texto_completo_test.py`.
- Navegador (Playwright): `node tests/browser.cjs` y `node tests/auditar_ux.cjs --comprobar`. Contra la web publicada:
  `node tests/movil_real.cjs` (también el workflow «Celular», `.github/workflows/movil.yml`).

## Pruebas
- **En local, solo las que toca el cambio**; la batería completa la corre la CI (`.github/workflows/pruebas.yml`).
- **Navegador en local: nunca la batería completa** (`tests/browser.cjs`); solo una comprobación pequeña de la pantalla
  tocada, a 390 px (celular) y en escritorio.
- Un PR se fusiona solo con la CI en verde.

## Estilo
- **`index.html` es muy grande (~500 KB):** se lee por trozos (`grep -n` y luego el rango), nunca entero.
- Una pantalla usa los tokens y componentes de `docs/DISENO.md`, nunca colores escritos a mano.
- **Traducciones:** solo se escribe el español (`idiomas/es.json`). No se traduce a mano en cada PR; lo que falta lo
  traduce cada domingo el modelo local de sk-atlas, que abre su propio PR (T95; `docs/TRADUCCIONES.md`).
  `data/idiomas/*.js` se generan: no se editan a mano. Los datos oficiales no se traducen.
- Python con `python3 -I`. Sigue el estilo del código vecino.

## Fuentes y raspado
- **Antes de escribir un script que lea un sitio, leer su `robots.txt`** (`docs/OPERACION.md`, T56). Solo rutas
  permitidas, ritmo lento, sin eludir bloqueos. `digitallibrary.un.org/search` y `documents.un.org/api` están prohibidos.
- Fuente por cada dato: todo dato oficial lleva enlace al original; lo propio se marca como tal.

## Commits y PR
- Todo cambio va por PR. Los commits salen con la cuenta de la persona; **el agente nunca figura como contribuidor**:
  ni `Co-Authored-By`, ni «Generated with…», ni nada parecido.
- **Autoría: solo Sukima-Labs** (06-11-2026). Ningún nombre de persona figura como autor de ATLAS ONU: ni en la web, ni en
  `NOTICE.md`, `CITATION.cff`, README, datos ni documentos. `tests/smoke.cjs` lo comprueba.
- **Una tarea de la cola por sesión.** Si aparece algo grande, va a la cola. Excepción: lo que hace daño ahora (por
  ejemplo, incumplir un `robots.txt`) se para con el arreglo mínimo, y lo demás va a la cola.
- **Al fusionar la tarea, se cierra la sesión**: una sesión nueva sale más barata que una conversación larga.
- Orden de la cola: primero datos y contenido; la interfaz, después.

## Seguridad y privacidad
- El repositorio es público: ni secretos, ni datos personales, ni el correo de nadie.
- Gratis, abierto y privado: sin servicios de pago, sin rastreo ni cookies de terceros.

## Infraestructura: aquí NO se crea (06-11-2026)
Desde el 06-11-2026 ATLAS ya no corre en el mini PC (`dignityos`): la **búsqueda en vivo** corre en el contenedor
`sk-atlas` de sukima-labs (servicio `atlas-busqueda`, `https://sk-atlas.pig-mimosa.ts.net`), la **actualización de
datos** en GitHub Actions y la **web** en GitHub Pages.

**Infraestructura** es todo lo que se queda corriendo o se expone: servicios y temporizadores de systemd (también los de
usuario), cron, servidores o puertos abiertos, túneles o Funnel, DNS, la configuración de Tailscale, Cloudflare o
Supabase, runners de CI, copias de seguridad y secretos. **La lleva `maquina`, el agente del servidor, a través de Patricio.**

Un agente que trabaja en un clon **trabaja solo con su clon de git y con GitHub**: ramas, commits, PR e issues. No crea,
no instala y no cambia infraestructura, tampoco «para probar». Si algo la necesita:
1. abre un issue con la etiqueta `infra`, explicando qué hace falta y por qué;
2. pídele al fundador que avise a Patricio.

**Si estás en el mini PC** y ves activos servicios o temporizadores viejos de ATLAS (`atlas-onu.service`,
`atlas-onu.timer`, `atlas-respaldo.timer` o una búsqueda local), díselo al fundador: se desactivan con
`systemctl --user disable --now <nombre>`. No montes nada que los sustituya.

`scripts/mini_pc/` y `docs/MINI_PC.md` son historia, con una excepción: `scripts/mini_pc/busqueda_servicio.py` es lo que
corre hoy en `sk-atlas`. No lo muevas ni le cambies el nombre sin hablarlo antes con Patricio.

## Skills
Las skills del proyecto siguen la [especificación Agent Skills](https://agentskills.io/specification) y viven en
`.claude/skills/<nombre>/SKILL.md`; `.agents/skills` es un enlace a esa carpeta para los agentes que buscan ahí.
- `trabajar-cola`: hacer la siguiente tarea de `docs/COLA_DE_TAREAS.md` de principio a fin (una por sesión).
- `cerrar-tarea`: cierre de cada tarea (cola y `data/hoja_ruta.json` al día).
- `revisar-ux`: revisión de UX a 390 px, un arreglo por commit.

Si tu agente no carga skills solo, lee el `SKILL.md` cuando la tarea encaje con su descripción.
