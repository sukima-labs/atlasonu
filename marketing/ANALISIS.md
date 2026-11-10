# Análisis de ATLAS ONU para su promoción (11-11-2026)

Hecho con el repositorio, la web publicada abierta en un navegador real, la API de GitHub y búsquedas web. Lo que no se pudo comprobar se dice como tal.

## 1. Qué es, en una frase
Un atlas en español, gratuito y sin rastreo, para entender cómo protege la ONU los derechos humanos **con el documento oficial delante**: cada dato enlaza a su fuente y lo que es elaboración propia está marcado como tal.

## 2. Lo que hay hoy (cifras de `data/`, ver `kit_prensa/CIFRAS.md`)
57 mandatos vigentes de relatores y grupos de trabajo · 422 actos jurídicos (403 localizados en la Biblioteca Digital) · 196 fichas de país · 18 tratados · 33 mecanismos conexos · 241 siglas · 116 hechos de historia · 41 entidades de la ONU · 6 idiomas · búsqueda en el texto completo de las resoluciones y de los documentos de cada país · «Preguntar a los documentos» (IA que solo redacta con párrafos encontrados y cita cada uno) · mapa del mundo con capas · accesibilidad WCAG 2.2 AA medida · se actualiza dos veces al día con salvaguardas.

Es un producto grande y cuidado (CI en verde, pruebas de navegador y de celular, auditoría de accesibilidad). **El problema no es el producto: es que nadie sabe que existe.**

## 3. Línea base (medida el 11-11-2026)
| Indicador | Valor | Cómo se midió |
|---|---|---|
| Estrellas / forks / seguidores del repo | 0 / 0 / 0 | `gh repo view` |
| Visitas al repo, últimos 14 días | 91, **3 personas distintas** | API de tráfico de GitHub (solo cuenta el repo, no la web) |
| Visitas totales de la web (contador propio) | 57 | `/visitas` del servicio de búsqueda |
| Resultados web para «ATLAS ONU» + «arqueología documental» + Sukima-Labs | **ninguno** | búsqueda web |
| Enlaces entrantes conocidos | 0 | búsqueda web (no hay herramienta de backlinks gratuita fiable) |
| Imagen al compartir un enlace | **no había** (`twitter:card=summary`, sin `og:image`); puesta en T69 | `index.html` |
| `sitemap.xml` / `robots.txt` | no / no (añadidos en T69) | la web publicada devolvía 404 |
| Salud del repo en GitHub | 75 % | `community/profile` (tiene README, licencia, código de conducta, guía de contribución y plantillas; Discussions está desactivado) |

Las 91 visitas al repo se concentran en cuatro días de octubre y noviembre (27, 33, 15 y 16 visitas) y las hacen 3 personas: es casi seguro el propio equipo. Los 5.768 clones de 14 días probablemente son automatización (la CI, la revisión diaria y las sesiones de trabajo clonan el repo; no se ha podido desglosar), no audiencia. Tratamos la audiencia externa real como **cero**.

## 4. Para quién es (por orden de prioridad)
1. **Estudiantes y docentes de derecho internacional, derechos humanos y relaciones internacionales en español** (España y América Latina). Necesitan citar documentos de la ONU sin perderse en su catalogación. El producto trae cita APA, descargas y «lectura fácil».
2. **Organizaciones de derechos humanos, personas defensoras y periodistas en español.** Quieren saber a qué relator acudir y qué dijo la ONU de su país. Valen la búsqueda guiada («¿ante quién reclamo?») y la ficha de país.
3. **Documentalistas, bibliotecas y quien investiga el sistema ONU.** Valoran la verificación contra la fuente y la «arqueología» de símbolos antiguos.
4. **Comunidad de datos abiertos y software libre** (AGPL, sitio estático, sin rastreo). No son usuarios finales, pero dan visibilidad, estrellas y contribuciones.

## 5. Competencia y alternativas
| Alternativa | Qué hace bien | Qué no cubre | Cómo nos posicionamos |
|---|---|---|---|
| **Universal Human Rights Index (OHCHR)** | Oficial; recomendaciones por país, tema y ODS | Interfaz densa, centrada en recomendaciones, sin guía para no expertos | Complemento: explicamos y enlazamos; no competimos con lo oficial |
| **UN Human Rights Database (UNHRDB)**, proyecto independiente y abierto | Búsqueda por párrafo en observaciones generales, jurisprudencia e informes temáticos; exporta a Zotero/BibTeX; servidor MCP | En inglés y orientada a juristas; no tiene mandatos, países ni historia explicados | Hermano en espíritu: nosotros somos **español primero, para quien empieza, con el contexto institucional** |
| **RightDocs** y buscadores de la Biblioteca Digital / Refworld | Cobertura documental amplia | Cada uno resuelve una parte; no conectan resolución, mandato y país | «Todo conectado con la fuente delante» |
| **Búsqueda web + Wikipedia** | Lo primero que se usa | Sin verificación contra el documento; a menudo desactualizada | Rigor: «localizado» significa que existe ese símbolo exacto |

Hueco claro: **no hay una puerta de entrada en español, gratuita y verificable al sistema de derechos humanos de la ONU.** Nadie ocupa «mandatos de relatores explicados en español con los documentos enlazados».

## 6. DAFO
| Fortalezas | Debilidades |
|---|---|
| Producto completo, probado y accesible; 6 idiomas; abierto; sin rastreo | **Cero audiencia y cero presencia** en la web; nombre genérico («Atlas») con muchas colisiones |
| Propuesta honesta y fácil de verificar (cada dato con su fuente) | Sin imagen al compartir, sin sitemap, navegación por `#` (los buscadores no indexan cada sección) |
| Cadencia de actualización (2 veces al día) que da noticias propias | Traducciones sin revisar por personas nativas; el contador visible muestra cifras muy bajas (57) |
| Cita APA, CITATION.cff, descargas CSV/JSON/Word: reutilizable en trabajos | Sin cuentas sociales del proyecto, sin lista de correo, sin Discussions |
| **Oportunidades** | **Amenazas** |
| Hueco en español; docencia y másteres de DDHH; ONG hispanohablantes | Un proyecto sin respaldo institucional pesa poco para docentes (hay que darle credenciales) |
| Directorios que aceptan herramientas (p. ej. el catálogo de herramientas de seguimiento de la Academia de Ginebra) | Que se confunda con un producto oficial de la ONU (por eso el aviso) |
| Historia de ingeniería interesante (verificación, accesibilidad, IA con citas) para Hacker News y comunidades de datos abiertos | Riesgo de reputación si una cifra o traducción es errónea en una pieza promocional |
| Fechas con gancho: 10 de diciembre (Derechos Humanos), sesiones del Consejo de DDHH (marzo, junio, septiembre) | Las plataformas castigan la autopromoción; hay que aportar antes de pedir |

## 7. Lo que hay que arreglar en el propio producto antes de hacer ruido
Son cambios de la cola (los decide su fundador); sin ellos, cada enlace compartido pierde fuerza:
1. **Imagen para compartir (1200×630)** y `twitter:card=summary_large_image` con `og:image` y `og:image:alt` (el `canonical` ya existe). Hoy un enlace en una red sale casi desnudo. **Hecho en T69 (11-11-2026).**
2. **`sitemap.xml` y `robots.txt`** (hechos en T69), y **enlaces profundos que sobrevivan al compartir** (`#mapa`, `#paises`… ya existen; falta una prueba y documentarlos). El Pages no puede indexar `#`, así que la vía de descubrimiento web son las páginas estáticas de aterrizaje (ver `PLAN.md`, fase 1).
3. **README en inglés** (resumen de 10 líneas) para directorios y Hacker News; el producto sí tiene 6 idiomas, el repo no lo dice.
4. **El contador de visitas** (issue #159 «se rompió el contador») es prueba social: si se muestra con cifras bajas, resta. Decidir con su fundador si se muestra el total o solo «desde tu país».
5. Activar **GitHub Discussions** y fijar un issue «Qué quieres hacer con ATLAS» para recoger casos de uso reales. Esto es configuración del repo (cambia ajustes), se le pide al fundador.
6. **DOI en Zenodo** (integración gratuita con GitHub): da cita académica estable. Requiere activar la integración en la cuenta propietaria.

## 8. Lo que no sabemos aún (y cómo se averigua)
- Quién usaría esto de verdad y para qué: **entrevistas cortas** con 5–10 docentes y personas de ONG (ver `PLAN.md`, fase 2) y la pregunta abierta en Discussions.
- Qué palabra usa la gente al buscar («relatores especiales ONU», «procedimientos especiales», «mandatos»): investigación de términos en el navegador, sin herramientas de pago.
- Cuánto tráfico llega de cada canal: la web no tiene analítica (es un principio). Se estima con el contador y con lo que da GitHub; ver la nota de medición en `PLAN.md`.
