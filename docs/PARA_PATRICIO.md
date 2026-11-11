# Para Patricio: qué es ATLAS ONU y qué te toca a ti

Documento de traspaso para quien lleva la infraestructura (con `maquina`, el Claude del servidor). Está escrito para leerse de arriba abajo sin conocer el proyecto. Para el detalle de cada servicio, ve a `docs/PATRICIO_SK_ATLAS.md`.

## 1. Qué es
**ATLAS ONU – Arqueología documental**: plataforma independiente y sin fines de lucro sobre el sistema de derechos humanos de la ONU (mandatos, tratados y comités, países, historia, siglas). La autoría es solo Sukima-Labs. No es oficial de la ONU. Todo lo oficial se atribuye y se enlaza a la ONU.

Repositorio público: `sukima-labs/atlasonu`. Web: https://sukimalabs.com/atlasonu/

## 2. Qué corre y dónde (desde el 06-11-2026)

| Pieza | Dónde | Quién la lleva | Qué hace |
|---|---|---|---|
| Web (sitio estático) | GitHub Pages | GitHub (nada que mantener) | Sirve `index.html` y `data/` |
| Actualización de datos | GitHub Actions (`.github/workflows/actualizar-datos.yml`) | GitHub; cambios de workflow, por PR | Dos veces al día revisa las fuentes de la ONU, valida y publica solo `data/` en `main` |
| Búsqueda en vivo y contador de visitas | Contenedor `sk-atlas`, servicio `atlas-busqueda` | **Tú / `maquina`** | Consulta la Biblioteca Digital de la ONU por la web, que no puede hacerlo directamente (CORS); cuenta visitas |
| Exposición pública | Tailscale Funnel → `https://sk-atlas.pig-mimosa.ts.net` (puerto 443) | **Tú / `maquina`** | Publica el servicio local `127.0.0.1:8787` |
| Copias de seguridad | Copia nocturna de las 02:00 de todos los servidores de sukima-labs | **Tú / `maquina`** | Incluye `sk-atlas` y el contador `/var/lib/atlas/visitas.json` |

El mini PC (`dignityos`) **ya no ejecuta nada**. Solo se desarrolla allí.

## 3. Lo que es tuyo y lo que no
**Infraestructura** es todo lo que se queda corriendo o se expone: servicios y temporizadores de systemd, cron, servidores o puertos, túneles o Funnel, DNS, configuración de Tailscale, Cloudflare o Supabase, runners de CI, copias de seguridad y secretos. Eso lo llevas tú.

Los Claude que trabajan en clones (incluido el del mini PC) **solo tocan git y GitHub**: ramas, commits, PR e issues. No crean ni cambian infraestructura, ni siquiera «para probar». Si algo la necesita, abren un issue con la etiqueta `infra` y el fundador te avisa. **Esa es tu bandeja de entrada**: revisa los issues `infra` abiertos.

## 4. Archivo que corre en `sk-atlas`
`scripts/mini_pc/busqueda_servicio.py`. Pese al nombre de la carpeta (historia), es el código vivo. **No lo muevas ni le cambies el nombre sin hablarlo antes con el fundador**: tu despliegue depende de esa ruta.
- Solo biblioteca estándar de Python; sin dependencias.
- Escucha solo en `127.0.0.1` (puerto 8787 por defecto, `ATLAS_BUSQUEDA_PUERTO`).
- El archivo del contador se fija con `ATLAS_VISITAS_ARCHIVO` (en `sk-atlas`: `/var/lib/atlas/visitas.json`).
- Cuando cambia el código en `main`, hay que traerlo a `sk-atlas` y reiniciar el servicio: es un paso tuyo.

## 5. Principios que no se rompen (también para la infraestructura)
1. **Gratis, abierto y privado:** todo a 0 €, código abierto, sin fuga de datos.
2. **Privacidad:** el contador guarda solo dos números agregados (total y por país). Ni IP, ni cookies, ni identificadores, ni registro de búsquedas. No añadas registros de acceso que guarden IP del visitante sin hablarlo antes (ver `docs/PRIVACIDAD.md`). Revisa que el proxy o el Funnel no las guarden más tiempo del necesario.
3. **Nada de secretos en el repositorio**, que es público. Ni tokens, ni correos, ni datos personales.
4. **No se eluden bloqueos de bots** de la ONU: el servicio ya limita el ritmo (20 consultas nuevas por minuto, caché de 1 h) para no saturarla.
5. **Las salvaguardas de datos no se saltan:** si los datos se degradan, la actualización aborta sin publicar.

## 6. Qué mirar de vez en cuando
- `https://sk-atlas.pig-mimosa.ts.net/salud` responde.
- La copia de las 02:00 incluye `sk-atlas` y se puede restaurar (`docs/RECUPERACION.md`).
- Los workflows de GitHub Actions están en verde (pestaña Actions). Si la revisión diaria falla varios días, avisa con un issue.
- Que el token de cualquier cosa que uses caduque y se pueda revocar.

## 7. Decisiones abiertas que te afectan
- **T44:** decidido el 08-11-2026: el Funnel sigue expuesto (ver #138 y `docs/RECUPERACION.md`, apartado Funnel).
- Copia del contador fuera de casa: ya cubierta por la copia cifrada; confirma que la restauración se ha probado.

## 8. Dónde está cada cosa
| Tema | Documento |
|---|---|
| Visión general y reglas | `docs/CONTEXTO_PARA_NUEVAS_SESIONES.md`, `CLAUDE.md` |
| Quién publica los datos y cuándo | `docs/OPERACION.md` |
| Copias y restauración | `docs/RECUPERACION.md` |
| Privacidad | `docs/PRIVACIDAD.md` |
| Licencias | `docs/LICENCIA.md` |
| Servicio `sk-atlas` en detalle | `docs/PATRICIO_SK_ATLAS.md` |
| Historia del mini PC (no usar) | `docs/MINI_PC.md`, `scripts/mini_pc/` |
