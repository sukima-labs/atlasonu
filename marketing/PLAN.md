# Proyecto de promoción de ATLAS ONU (11-11-2026 → 10-02-2027)

Un trimestre, **0 €**, con las herramientas que tiene el asistente: navegador real (Chrome/Brave con las sesiones del equipo, con una extensión del navegador), búsqueda web, `gh`, el servidor `sk-atlas`, Playwright para generar imágenes y capturas, Gmail/Drive/Calendar/Sheets conectados para correos y seguimiento. Lo hace el asistente de ATLAS; lo que es público y no se deshace pasa antes por quien lleva el proyecto (ver «Puertas de aprobación»).

## Objetivo
Pasar de **cero audiencia a una base pequeña pero real de personas que usan ATLAS para citar a la ONU**, y dejar la visibilidad web montada para que siga creciendo sin esfuerzo.

### Metas a 90 días (hipótesis; se revisan cada semana con datos)
| Indicador | Hoy | 30 días | 90 días |
|---|---|---|---|
| Estrellas en GitHub | 0 | 15 | 100 |
| Visitas totales de la web (contador) | 57 | 400 | 3.000 |
| Personas distintas que ven el repo (14 d) | 3 | 60 | 300 |
| Enlaces entrantes de dominios distintos | 0 | 3 | 12 |
| Directorios y listas donde figura | 0 | 3 | 8 |
| Conversaciones de uso reales (entrevistas, issues, respuestas) | 0 | 5 | 20 |
| Docentes o centros que lo mencionan en una guía de curso | 0 | 0 | 2 |

La meta que manda es la última fila. Las estrellas son un termómetro, no el fin.

## Principio de método
**Aportar antes de pedir.** En cada comunidad: primero responder y ayudar con ATLAS (cuando de verdad responde la pregunta), después mostrarlo. Nunca mensajes masivos ni repetir la misma pieza en cien sitios.

## Fases

### Fase 0 · Base (semana 1, 11–17 nov) — lo hace el asistente en el repo
Sin esto, cada enlace compartido sale a medias.
- [x] Módulo `marketing/` (este) y medición de la línea base.
- [ ] **T69** Imagen para compartir 1200×630 generada con Playwright desde la marca (`assets/marca/`), `og:image`, `og:image:alt`, `twitter:card=summary_large_image`, `canonical`, `sitemap.xml`, `robots.txt`. Un PR pequeño sobre `index.html` (después de fusionar las ramas de mapas, para no pisarlas).
- [ ] **T70** `README.en.md` de 10–15 líneas (qué es, para quién, enlaces) y enlazarlo en el README. Descripción y *topics* del repo (ya hay 5; añadir `un-human-rights`, `special-rapporteurs`, `open-data`, `spanish`, `human-rights-law`).
- [ ] **T71** Páginas de aterrizaje indexables (estáticas, una por mandato y por país, o al menos las 57 de mandatos): el sitio usa `#` y Google no indexa cada sección. Es la mayor palanca de tráfico duradero («relator especial sobre la tortura» → ficha). **Decisión de su fundador** (cambia la arquitectura de la web); aquí se deja el diseño y la estimación.
- [ ] Pedir al fundador: activar **GitHub Discussions**, la integración **Zenodo** (DOI), y fijar la imagen social del repo (ajuste manual, la API no lo permite).

### Fase 1 · Investigación y primeros apoyos (semanas 1–3)
Con el navegador, solo lectura:
1. **Mapa de comunidades y reglas**: leer las reglas de autopromoción de cada sitio y apuntarlas en `CANALES.md` (ya hecho para Hacker News; pendiente Reddit, Mastodon, Bluesky, LinkedIn, foros docentes).
2. **Términos de búsqueda reales** (autocompletado y «otras preguntas» del buscador): decidir los títulos de las páginas de aterrizaje y de los textos.
3. **Listado de contactos públicos** (departamentos y másteres de DDHH, bibliotecas ONU depositarias, ONG): solo datos públicos institucionales, sin datos personales, en una hoja de cálculo privada (nunca en el repo).
4. **Directorios**: preparar las solicitudes (Academia de Ginebra, listas *awesome*, Wikidata/recursos educativos abiertos, guías de investigación de bibliotecas, OER Commons). Cada una con su regla de admisión; solo donde ATLAS encaje de verdad.

### Fase 2 · Lanzamiento suave en español (semanas 3–6)
Objetivo: los primeros 20–50 usuarios reales y las primeras respuestas.
- **Correo a docentes y másteres** (borrador en `contenidos/03_correo_docentes.md`): corto, con un caso de uso («encuentra el mandato, el informe y la cita APA en 2 minutos») y la oferta de una sesión de 15 minutos. Pocas decenas, personalizados uno a uno; nada de listas.
- **LinkedIn y Mastodon/Bluesky** (cuenta del proyecto): publicación de presentación y después una pieza útil por semana (ver calendario).
- **Entrevistas de 15 min** con 5–10 personas que sí usan estos documentos: qué buscan, qué les estorba, cómo lo explicarían. Resultado en `REGISTRO.md`, sin nombres.
- **Responder preguntas abiertas** donde ATLAS sirva de verdad (foros de estudiantes de derecho, comunidades de DDHH), con enlace solo si responde.

### Fase 3 · Lanzamiento técnico en inglés (semanas 6–9)
Objetivo: visibilidad de la comunidad de software libre y de datos abiertos.
- **Show HN** (borrador en `contenidos/04_show_hn.md`) cuando el producto pase una revisión de arranque en frío (la web se prueba con el flujo «Celular» y desde un navegador limpio). Se publica un martes–jueves por la mañana (hora del Este de EE. UU.) y el asistente se queda atendiendo los comentarios las primeras horas. No se pide a nadie que vote.
- Comunidades de datos abiertos y derechos humanos (reglas por canal en `CANALES.md`), con el `README.en.md` como puerta.
- Posible entrada de blog técnico («Cómo verificamos 422 actos jurídicos contra la fuente») en el propio sitio o dev.to.

### Fase 4 · Hitos y constancia (semanas 6–13)
- **Calendario con gancho** (ver abajo): una pieza útil por semana, con un enlace profundo a la parte de ATLAS que la respalda.
- **10 de diciembre, Día de los Derechos Humanos**: pieza especial («qué relator existe para cada derecho»), con imagen y cita APA.
- **Nota de prensa** (borrador en `contenidos/05_nota_prensa.md`) a medios especializados en español **solo cuando haya algo noticioso comprobable**: una cifra nueva, una capa del mapa, una colaboración. No antes.
- **Informe del trimestre** (`REGISTRO.md`): qué funcionó, qué no, qué se repite.

## Calendario editorial (una pieza por semana; 1 idea → 3 formatos)
| Semana | Tema (con enlace profundo) | Formato |
|---|---|---|
| 1 | Qué es ATLAS y por qué existe | Presentación (hilo + LinkedIn) |
| 2 | «¿Ante quién reclamo?»: la búsqueda guiada | Capturas animadas (GIF) |
| 3 | Cómo citar una resolución antigua de la ONU (arqueología documental) | Guía corta con ejemplo real |
| 4 | El mapa de quién ratificó qué (capas) | Imagen + enlace al mapa |
| 5 | Qué hace un relator especial: los 57 mandatos | Hilo |
| 6 | Show HN / comunidades de datos abiertos | Entrada técnica |
| 7 | «Preguntar a los documentos»: IA que cita o calla | Demo corta |
| 8 | La ficha de un país: ratificaciones, EPU, visitas | Caso (varios países) |
| 9 | 10 de diciembre | Pieza especial |
| 10–13 | Novedades detectadas en las fuentes (datos propios de cada semana) | Resumen semanal automatizable |

## Cómo se mide (sin traicionar el «sin rastreo»)
La web no lleva analítica y no la va a llevar. Se usa:
- el **contador propio** (total y por país, sin identificadores) mediante `metricas/medir.py`;
- el **tráfico del repo** de GitHub (visitas, personas distintas, clones y de dónde llegan; solo 14 días de histórico, por eso se guarda cada semana);
- **estrellas, forks, issues y menciones** (búsqueda web y avisos de GitHub);
- **enlaces con parámetro** (`?utm=…`) solo cuando el destino es el repo, donde GitHub informa de las referencias; la web los ignora;
- **cualitativo**: respuestas, entrevistas, peticiones.
Hay un límite honesto: no sabremos cuántas personas llegan a la web desde cada canal. Si hiciera falta, un contador de procedencia agregado y sin identificadores sería una decisión de producto de su fundador.

## Puertas de aprobación (qué se hace solo y qué no)
| Se hace sin pedir | Se pide antes (acto externo) |
|---|---|
| Investigar, leer, medir, analizar la competencia | Crear cuentas del proyecto en redes (se crean con el correo de Sukima-Labs, no personal) |
| Escribir y ajustar borradores, imágenes y capturas | **Publicar** cualquier pieza (red social, foro, Show HN) |
| Cambios en el repo por PR (con la CI en verde) | **Enviar** correos o mensajes a terceras personas |
| Preparar solicitudes a directorios y hojas de contactos | Enviar solicitudes a directorios; cambiar ajustes del repo (Discussions, Zenodo, imagen social) |
| Anotar el registro | Cualquier gasto (no lo hay) |

Cada acto aprobado se apunta en `REGISTRO.md` con fecha, canal, enlace y quién lo aprobó.

## Riesgos y cómo se evitan
| Riesgo | Medida |
|---|---|
| Una cifra o traducción errónea en una pieza pública | Las cifras salen de `cifras.py`; no se publican traducciones sin revisar como «oficiales»; el aviso de «iniciativa independiente» va siempre |
| Que se tome por oficial de la ONU | Aviso fijo; ningún logotipo ni emblema de la ONU en las piezas |
| Ser tratado como spam | Una pieza útil por semana, sin repetir texto, leer reglas antes, responder a quien conteste |
| Quedarse sin tiempo para atender el lanzamiento | Solo se lanza cuando el asistente puede estar las primeras horas |
| Mostrar autoría personal por descuido | Revisión de cada borrador contra la regla «solo Sukima-Labs»; lo comprueba una prueba de `tests/smoke.cjs` en el repo |
| Que la búsqueda en vivo se caiga con un pico de visitas | Revisar `/salud` por el camino público antes de cada lanzamiento; la búsqueda tiene límite de ritmo y caché propios; avisar a `maquina` si se espera un pico |
