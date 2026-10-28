# Qué licencia usar en ATLAS ONU: análisis y decisión

> No es asesoramiento jurídico. Es un análisis práctico para un proyecto académico público; si lo vas a entregar como Trabajo Fin de Máster, confirma con el programa si tiene normas propias sobre propiedad intelectual y difusión.

## Lo que hay que licenciar (tres cosas distintas)

| Parte | Quién es el titular | Consecuencia |
|---|---|---|
| **Código** (`index.html`, `scripts/`, `tests/`, flujos de GitHub) | Tú | Puedes elegir cualquier licencia |
| **Contenido propio** (siglas, cuadros, explicaciones, documentación) | Tú | Puedes elegir; conviene una licencia pensada para contenido |
| **Datos y textos de la ONU** (símbolos, títulos, tratados, ratificaciones) | Naciones Unidas | **No se pueden relicenciar**; se enlazan y atribuyen |

Por eso **una sola licencia para todo sería un error**: una licencia de software no es adecuada para textos, y ninguna puede cubrir lo que no es tuyo.

## Qué queremos del proyecto

1. Que sea **público y reutilizable** por estudiantes, ONG y universidades.
2. Que **te reconozcan la autoría** (importa en un proyecto académico).
3. Que no cree trabas jurídicas a quien lo use ni a ti.
4. Que no se confunda con algo oficial de la ONU.
5. Sin patentes ni intereses comerciales de por medio.

## Comparación

| Licencia | Para | Obliga a | Encaja |
|---|---|---|---|
| MIT | Código | Mantener el aviso de copyright | Fue la elegida al principio; permite cerrar el código derivado, por eso se sustituyó |
| Apache-2.0 | Código | Aviso, NOTICE y cambios; da licencia de patentes | Innecesaria: no hay patentes y añade burocracia |
| GPL / **AGPL** | Código | Publicar con la misma licencia lo derivado (AGPL también si se ofrece en red) y permite exigir autoría visible | **Sí, desde el 28-10-2026**: sigue siendo abierta (ONG y universidades pueden usarla) y evita que alguien la cierre o la reempaquete sin crédito |
| **CC BY 4.0** | Contenido | Dar crédito e indicar cambios | **Sí, para el contenido propio**: reutilizable y deja constancia de autoría |
| CC BY-SA 4.0 | Contenido | Crédito y compartir igual | Alternativa válida si quieres que todo derivado siga abierto, pero complica integrarlo en otros materiales |
| CC0 / Unlicense | Todo | Nada | No: renuncia al crédito, que es lo que más importa en lo académico |
| «Todos los derechos reservados» | Todo | — | Es lo que había: contradice que el proyecto sea público |

## Decisión aplicada

- **Código → AGPL-3.0** (`LICENSE`) con **autoría visible obligatoria** (`NOTICE.md`, términos adicionales de la sección 7). *Cambio del 28-10-2026: hasta entonces era MIT; lo ya obtenido bajo MIT sigue siendo MIT. Motivo: el fundador quiere código abierto pero que nadie lo cierre ni quite su autoría.*
- **Contenido propio → CC BY 4.0** (`LICENSE-CONTENIDO.md`).
- **Contenido de la ONU → fuera de la licencia**, con aviso explícito, atribución y enlace a cada fuente.
- Se añade `CITATION.cff` para que GitHub muestre «Cite this repository».

## Por qué esta combinación

- Es el estándar de facto en proyectos abiertos de datos y código: GitHub reconoce MIT automáticamente y muestra la licencia en el repositorio.
- **Entrada = salida**: quien contribuya con una propuesta (formulario de GitHub o código) lo hace bajo las mismas condiciones.
- **CC BY** exige que cualquiera que reutilice las siglas o los cuadros te cite, que es justo lo que busca un proyecto académico.
- Mantiene separado lo que es tuyo de lo que es de la ONU, que es lo que evita problemas.

## Qué no cubre ninguna licencia

- El nombre, el emblema y los logotipos de la ONU y de la Universidad de Alcalá: no se usan ni se licencian, y el proyecto declara que **no es oficial**.
- Datos personales: la plataforma no recoge IP ni datos propios; el contador de visitas es un servicio externo anónimo.

## Cómo cambiarla más adelante

Como único titular puedes relicenciar lo futuro cuando quieras (lo ya publicado bajo MIT/CC BY seguirá disponible para quien lo obtuvo antes). Si algún día aceptas contribuciones de otras personas, para cambiar la licencia necesitarías su consentimiento: por eso conviene decidirlo ahora.
