# Privacidad y datos personales

Criterios del proyecto (31-10-2026). Cambiarlos exige una tarea en la cola y una nota aquí.

## Qué datos existen hoy
| Dato | Dónde | Quién lo ve | Personal |
|---|---|---|---|
| Contador de visitas: dos números agregados (total y por país) | `sk-atlas`, el servidor de sukima-labs (`busqueda_servicio.py`) | el autor | no: ni IP, ni cookies, ni identificadores |
| País de visita | se deduce en el navegador (zona horaria o idioma) y no se envía con identidad | nadie fuera del navegador | no |
| Búsquedas en vivo | el servicio las recibe para consultar la Biblioteca Digital | el servicio, sin registro | en principio no; no se guardan |
| Datos de personas de los mandatos | solo funciones públicas: titulares, nacionalidad y actos oficiales | público | sí, pero son información pública de la función |

## Criterios
1. **Solo información pública de la función.** Para la sección de relatores (T40): nombre del mandato, periodo, país de nacionalidad, actos oficiales y enlaces a la fuente. Nada de vida privada, contacto personal, redes sociales ni fotos sin fuente.
2. **Ninguna IP ni identificador en ningún registro.** Si algún día se registran búsquedas sin resultado (para solicitudes de verificación), solo se guardan agregadas, sin IP y sin el texto libre de la persona.
3. **Ninguna cookie ni almacenamiento propio** salvo que el autor lo decida y lo declare aquí.
4. **Nada de terceros.** Ningún script, fuente o servicio externo que registre a quien visita (ver la regla gratis, abierto y privado en la cola).
5. **Derecho de rectificación:** quien aparezca en una ficha puede pedir corrección o retirada escribiendo en privado al autor (ver `SECURITY.md`).

## Decisiones pendientes del fundador
- **Reescribir el historial** para quitar la pantalla EPU retirada (PR 67 y 69) con `git filter-repo`. Es destructivo (cambia todos los hashes) y no se hace sin su confirmación. Antes de hacer público el repositorio, debe decidirse.
- **Registro de búsquedas sin resultado.** Se mantiene en evaluación: no se implementa hasta que el fundador acepte los criterios 2 y 4.
