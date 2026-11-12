# ATLAS ONU — reglas para cualquier Claude que trabaje en este repositorio

Este fichero lo carga Claude Code en cualquier clon: en el mini PC del fundador, en el servidor de sukima-labs o
donde sea. Antes de empezar, lee también `docs/CONTEXTO_PARA_NUEVAS_SESIONES.md`.

## Infraestructura: aquí NO se crea (06-11-2026)

**Hubo una mudanza.** Desde el 06-11-2026 ATLAS ya no corre en el mini PC (`dignityos`):
- la **búsqueda en vivo** corre en el servidor de sukima-labs, en el contenedor `sk-atlas` (servicio
  `atlas-busqueda`, publicado en `https://sk-atlas.pig-mimosa.ts.net`);
- la **actualización de datos** corre en GitHub Actions;
- la **web** está en GitHub Pages: https://sukimalabs.com/atlasonu/

**Infraestructura** es todo lo que se queda corriendo o se expone: servicios y temporizadores de systemd
(también los de usuario), cron, servidores o puertos abiertos, túneles o Funnel, DNS, la configuración de
Tailscale, Cloudflare o Supabase, runners de CI, copias de seguridad y secretos. **La lleva `maquina`, el Claude
del servidor, a través de Patricio.**

Un Claude que trabaja en un clon (en el mini PC o en cualquier otro sitio) **trabaja solo con su clon de git y con
GitHub**: ramas, commits, PR e issues. Ahí desarrolla código, datos, pruebas y documentación. Nada más: ni
servicios, ni servidores ni puertos, ni cambios en Tailscale, Cloudflare o Supabase, ni secretos. **No crea, no
instala y no cambia infraestructura**, tampoco «para probar». Si algo necesita infraestructura:
1. abre un issue con la etiqueta `infra`, explicando qué hace falta y por qué;
2. pídele al fundador que avise a Patricio.

**Si estás en el mini PC** y ves activos servicios o temporizadores viejos de ATLAS (`atlas-onu.service`,
`atlas-onu.timer`, `atlas-respaldo.timer` o una búsqueda local), díselo al fundador: se desactivan con
`systemctl --user disable --now <nombre>`. No montes nada que los sustituya: su trabajo ya se hace en otro sitio.

`scripts/mini_pc/` y `docs/MINI_PC.md` son historia, con una excepción: `scripts/mini_pc/busqueda_servicio.py` es
lo que corre hoy en `sk-atlas`. No lo muevas ni le cambies el nombre sin hablarlo antes con Patricio.

## Lo demás
- Todo cambio va por PR. Los commits salen con la cuenta de la persona, y Claude nunca figura como contribuidor:
  ni `Co-Authored-By` ni nada parecido.
- El repositorio es público: ni secretos, ni datos personales, ni el correo de nadie.
- **Autoría: solo Sukima-Labs** (06-11-2026). Ningún nombre de persona figura como autor de ATLAS ONU: ni en la web, ni en `NOTICE.md`, `CITATION.cff`, README, datos ni documentos. Las pruebas lo comprueban.
- **Cómo trabaja Claude aquí** (decisión de Sukima-Labs, 12-11-2026, #291), para gastar menos:
  - **Traducciones:** solo se escribe el español (`idiomas/es.json`). No se traduce a mano en cada PR; lo que falta va
    a una tanda periódica o a Weblate (`docs/TRADUCCIONES.md`).
  - **`index.html` es muy grande:** se lee por trozos (`grep -n` y luego el rango), nunca entero.
  - **Pruebas en local:** solo las que toca el cambio; la batería completa la corre la CI.
  - **Orden de la cola:** primero datos y contenido; la interfaz, después.
  - **Navegador en local:** nunca la batería completa (`tests/browser.cjs`); solo una comprobación pequeña de la pantalla
    tocada. La batería completa la corre la CI.
  - **Una tarea de la cola por sesión.** Si aparece algo grande, va a la cola. Excepción: lo que hace daño ahora (por
    ejemplo, incumplir un `robots.txt`) se para con el arreglo mínimo, y lo demás va a la cola.
  - **Al fusionar la tarea, se cierra la sesión**, en vez de seguir con la siguiente: una sesión nueva sale más barata
    que una conversación larga.
  - **Antes de escribir un script que lea un sitio, leer su `robots.txt`** (`docs/OPERACION.md`, T56).
