# Privacidad y datos personales

Criterios del proyecto (31-10-2026). Cambiarlos exige una tarea en la cola y una nota aquí.

## Qué datos existen hoy
| Dato | Dónde | Quién lo ve | Personal |
|---|---|---|---|
| Contador de visitas: dos números agregados (total y por país) | `sk-atlas`, el servidor de sukima-labs (`busqueda_servicio.py`) | el autor | no: ni IP, ni cookies, ni identificadores |
| País de visita | se deduce en el navegador (zona horaria o idioma) y no se envía con identidad | nadie fuera del navegador | no |
| Dos marcas en el navegador (`localStorage`): `atlas_visita2` (hora de la última visita contada, para no contar dos veces a la misma persona en 12 h) y `atlas_pista_menu` (ya se vio la pista del menú) | solo en el navegador de quien visita; no se envían a ningún sitio | nadie fuera del navegador | no: ni identificador ni datos de la persona |
| Búsquedas en vivo | el servicio las recibe para consultar la Biblioteca Digital | el servicio, sin registro | en principio no; no se guardan |
| Datos de personas de los mandatos | solo funciones públicas: titulares, nacionalidad y actos oficiales | público | sí, pero son información pública de la función |

## Criterios
1. **Solo información pública de la función.** Para la sección de relatores (T40): nombre del mandato, periodo, país de nacionalidad, actos oficiales y enlaces a la fuente. Nada de vida privada, contacto personal, redes sociales ni fotos sin fuente.
2. **Ninguna IP ni identificador en ningún registro.** Si algún día se registran búsquedas sin resultado (para solicitudes de verificación), solo se guardan agregadas, sin IP y sin el texto libre de la persona.
3. **Ninguna cookie ni almacenamiento propio** salvo que el autor lo decida y lo declare aquí. Declarado hoy: solo las dos marcas de `localStorage` de la tabla de arriba. Cookies, ninguna.
4. **Nada de terceros.** Ningún script, fuente o servicio externo que registre a quien visita (ver la regla gratis, abierto y privado en la cola).
5. **Derecho de rectificación:** quien aparezca en una ficha puede pedir corrección o retirada escribiendo en privado al autor (ver `SECURITY.md`).

## Decisiones pendientes del fundador
- **Reescribir el historial** para quitar la pantalla EPU retirada (PR 67 y 69) con `git filter-repo`. Es destructivo (cambia todos los hashes) y no se hace sin su confirmación. El repositorio es público desde el 06-11-2026 y esa pantalla sigue en su historial (las reescrituras de ese día solo cambiaron la autoría).
- **Registro de búsquedas sin resultado.** Se mantiene en evaluación: no se implementa hasta que el fundador acepte los criterios 2 y 4.
