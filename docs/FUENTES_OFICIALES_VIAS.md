# Fuentes oficiales de cada vía (T76 y T77)

Versión del 11-11-2026. Pedido de Jeisson (#205, #207): el asistente «Tengo un caso: ¿adónde acudo?» se construye sobre los **documentos oficiales** de la ONU, no sobre guías de terceros, y todo se explica en lenguaje claro para quien no es experta o experto.

## Regla de fuentes (de más a menos fuerte)
1. **El tratado y su protocolo facultativo** (qué derechos, quién puede quejarse, qué plazo fija el propio texto).
2. **El reglamento del comité** o los métodos de trabajo del procedimiento especial (plazos y requisitos de admisibilidad que el comité se da a sí mismo).
3. **Los formularios y notas de orientación del ACNUDH** (ohchr.org): qué datos pide cada vía.
4. **Fichas y manuales del ACNUDH** (p. ej. la Ficha informativa n.º 7): sirven de mapa, pero llevan **fecha** y pueden haber envejecido.
5. **Guías de terceros** (T77: FLAC, ISHR, IDHC, oficinas del ACNUDH…): solo orientan. **Nunca son la fuente de un dato** del asistente; sirven para saber qué preguntarse y para comprobar que no se nos escapó algo.

## Cómo se escribe cada dato (para quien no es experta)
Cada requisito o plazo lleva **cuatro campos**, y los cuatro serán obligatorios (se añadirá una prueba en la CI que rechace una fila a la que le falte uno):
- **En palabras simples:** una o dos frases, sin siglas sin explicar (p. ej. «Tienes que haber agotado primero los tribunales de tu país»).
- **Lo que dice la ONU:** la frase oficial, corta y entre comillas, en el idioma original.
- **Dónde lo dice:** documento, artículo o sección, y enlace (p. ej. «Ficha informativa n.º 7 Rev.2, 2013, sección del Comité de Derechos Humanos»).
- **Estado:** `leído en el original` (fecha de lectura) o `por verificar` (se ve en un resumen, no se ha leído el original). Un dato `por verificar` sale con aviso y no se usa en el asistente.

Más una página corta, **«Cómo funciona esto, explicado fácil»**: qué es un comité, qué es un procedimiento especial, qué quiere decir «agotar los recursos internos», qué es una «medida provisional», y por qué el plazo cambia de un comité a otro.

## Qué se pudo leer hoy y qué no (honestidad sobre el acceso)
- Las **páginas** de `ohchr.org` (HTML) devuelven **403** a las lecturas automáticas, aunque su `robots.txt` no las prohíbe. **No se esquiva**: se leen a mano o por la persona revisora.
- Los **PDF** de `ohchr.org/sites/default/files/…` **sí se descargan** (200): la Ficha informativa n.º 7 Rev.2 (2013) y el capítulo VIII del Manual para ONG se leyeron enteros hoy.
- `docs.un.org` no devuelve el PDF a una lectura automática; `tbinternet.ohchr.org` lo prohíbe en su `robots.txt`. Los **reglamentos vigentes de cada comité** están ahí, así que quedan `por verificar` hasta tener una vía legítima (a mano, o la Biblioteca Digital si publica el texto).

## Primera tabla leída en el original (Ficha informativa n.º 7 Rev.2, ACNUDH, 2013)
La ficha tiene **13 años**: sirve para el mapa y los plazos de los textos de tratado, pero **no cubre bien las vías nuevas** (la ficha dice que el mecanismo de quejas del Comité de Trabajadores Migratorios aún no estaba en vigor) y los reglamentos pueden haber cambiado desde entonces. Por eso cada fila queda `leído` solo **contra esa ficha** hasta cruzarlo con el reglamento vigente.

| Vía | Plazo que dice la ficha | Otros requisitos que cita |
|---|---|---|
| Comité de Derechos Humanos (PIDCP, Protocolo Facultativo) | **Sin plazo** en el Protocolo. El reglamento (regla 96 c) permite ver «abuso» pasados **5 años** del agotamiento de recursos internos o **3 años** tras otra vía internacional, salvo razones que lo justifiquen | Agotar recursos internos; el mismo asunto no puede estar en otra vía internacional; la ficha avisa de **retrasos de varios años** |
| Comité para la Eliminación de la Discriminación Racial (CERD, art. 14) | **6 meses** desde la decisión final de una autoridad nacional | El Estado debe haber reconocido la competencia del comité; admite quejas de grupos; otra vía internacional **no** la bloquea |
| Comité de Derechos Económicos, Sociales y Culturales (Protocolo Facultativo) | **1 año** desde agotar recursos internos, salvo que fuera imposible | Agotar recursos internos |
| Comité de los Derechos del Niño (Protocolo 3) | **1 año** desde agotar recursos internos, salvo que fuera imposible | Agotar recursos internos; el mismo asunto no puede estar ya examinado en otra vía |
| Comité contra la Tortura, CEDAW, Personas con Discapacidad, Desapariciones Forzadas, Trabajadores Migratorios | Sus tratados y protocolos **no fijan plazo** (leído el 12-11-2026, ver abajo); falta el reglamento de cada comité | Ver la base de reglas |

Todo lo demás de la ficha (formularios modelo para el Comité de Derechos Humanos, el de Tortura y el de Discriminación contra la Mujer) es la base del **borrador de campos** de la fase 4 opcional de T76.

## Base de reglas del asistente: `data/vias.js` (T76 fase 1, 12-11-2026)
Once vías: las quejas individuales ante los nueve comités que las reciben (la del CMW, marcada como que **aún no funciona**),
la **acción urgente** del Comité contra la Desaparición Forzada (art. 30) y las comunicaciones a los procedimientos
especiales. 57 requisitos con sus cuatro campos; **47 leídos en el original**, todos en el texto del tratado o protocolo:
- **Textos que ATLAS ya guarda** (`data/tratados/`: protocolos del PIDESC, la CEDAW, la CRC y la CRPD, y la Convención sobre
  desapariciones): la prueba `tests/vias_test.py` comprueba en la CI que cada cita está letra a letra en ese texto.
- **Leídos hoy en la Biblioteca Digital**, PDF en español escaneado (sin capa de texto; transcritos de la página):
  Protocolo Facultativo del PIDCP (`A/RES/2200 (XXI) A`, registro 660187, arts. 2, 3 y 5), CERD (`A/RES/2106 (XX) A`,
  registro 660429, art. 14), Convención contra la Tortura (`A/RES/39/46`, registro 74216, art. 22) y Convención sobre
  trabajadores migratorios (`A/RES/45/158`, registro 105636, art. 77). Descarga de uno en uno con 5 s de pausa.
- **Por verificar (10):** lo que solo está en el **reglamento** de cada comité (plazos del Comité de Derechos Humanos, la CAT,
  la CEDAW, la CRPD y la CED; medidas provisionales del Comité de Derechos Humanos y de la CAT) y las tres filas de los
  procedimientos especiales. Llevan `onu` vacío y no entran en el asistente.
- Qué Estados **aceptan** cada vía: para las que van por protocolo, la ratificación ya está en los datos de cada país; para
  las que van por **declaración** (CERD art. 14, CAT art. 22, CED art. 31, CMW art. 77), la lista sale de la misma Colección de Tratados
  (12-11-2026: 60, 69, 30 y 6 Estados). `scripts/fetch_tratados.py` lee el apartado de declaraciones de cada tratado; en la CAT y
  la CED separa la vía individual (arts. 22 y 31) de la vía entre Estados (arts. 21 y 32), y si el texto está en una nota al pie
  (Ucrania, CAT) lee la nota. Se renueva con la revisión diaria de datos.

En la web (12-11-2026): pantalla «Tengo un caso: ¿adónde acudo?» (menú, junto a «Tratados y comités»), con la tabla de
las once vías y los requisitos de cada una, y un **asistente paso a paso** que solo usa requisitos «leído en el original».
El tema del caso solo orienta (qué derechos protege cada tratado: la tortura lleva a la CAT y al Comité de Derechos Humanos,
la desaparición a la acción urgente y la queja de la CED…); no es un dato oficial y no sustituye leer el tratado.

## Procedimientos especiales (relatores y grupos de trabajo)
No son «quejas» con plazo y admisibilidad: se envían **comunicaciones** (alegaciones, acciones urgentes) y el relator decide si actúa. Para el asistente es la vía clave **cuando la víctima no puede agotar los recursos del país o el riesgo es inminente**. Contrastado el 12-11-2026 (pedido del grupo; el material de referencia orienta, la fuente de cada dato es la ONU):

| Dato | En palabras simples | Dónde lo dice | Estado |
|---|---|---|---|
| Garantías de las visitas | Durante una visita el Estado debe dar libertad de movimiento en todo el país, libertad de investigación (cárceles, autoridades, ONG, prensa, contacto confidencial con testigos y presos, documentos) y la seguridad de que nadie sufrirá amenazas ni castigo por hablar con el relator | Términos de referencia de las misiones, `E/CN.4/1998/45`, apéndice V (Biblioteca Digital, registro 247791) | `leído en el original` (12-11-2026) |
| Las visitas necesitan invitación | Solo se visita un país si el Estado invita | Mismo apéndice («the Government that invited them») | `leído en el original` (12-11-2026) |
| Invitaciones abiertas | Algunos Estados invitan de antemano a todos los mandatos temáticos | Lista de invitaciones permanentes del ACNUDH (la que usa la ficha de cada país) | `por verificar` en el original (la página da 403) |
| Quién puede escribir y qué debe tener la comunicación | La víctima, o un grupo u ONG de buena fe con conocimiento directo o fiable; describir los hechos, sin lenguaje abusivo, no basada solo en noticias de prensa, no manifiestamente infundada ni con motivación política | Código de conducta, `A/HRC/RES/5/2`, art. 9 | `por verificar` (la Biblioteca Digital no tiene el PDF en el registro 603044) |
| No hace falta agotar recursos internos ni que el Estado haya ratificado | Se puede escribir aunque el caso siga abierto en el país y aunque el Estado no sea parte de ningún tratado | Página «Comunicaciones» del ACNUDH | `por verificar` (la página da 403) |
| Llamamientos urgentes y destinatarios no estatales | Si hay riesgo inminente, el mandato puede escribir al Estado en horas o días; también escribe a empresas y otros actores no estatales | Página «Comunicaciones» del ACNUDH; informes anuales de comunicaciones (`A/HRC/…`) | `por verificar` |
| Suspensión de miembros del Consejo | La Asamblea puede suspender por dos tercios a un miembro que cometa violaciones graves y sistemáticas: Libia (resolución 65/265, 1-3-2011, devuelta por la 66/11, 18-11-2011) y Rusia (resolución ES-11/3, 7-4-2022) | `A/RES/60/251`, párr. 8, y las resoluciones citadas | `leído` solo el registro de la 66/11; el resto `por verificar` |

**Dos correcciones al material de referencia** (no se copiaron): Rusia **no se retiró por su cuenta**, la Asamblea la suspendió (`A/RES/ES-11/3`) y ella anunció después su salida; y su intento de volver fue en la elección del **10-10-2023** (periodo 2024–2026), no en 2024.

En la web (12-11-2026): fichas «Consejo de Derechos Humanos» y «Procedimientos especiales» de la pantalla del sistema ONU, la guía «¿Qué quieres conseguir?» y la línea de tiempo (primer mandato por país en 1967, mandatos de 1986, 1990 y 1991, suspensiones de Libia y Rusia, elección de 2023). Lo `por verificar` está dicho en la web solo de forma general y con el aviso de confirmar en el sitio oficial; **no entra en el asistente T76** hasta leerse en el original.

## Órganos de tratados: contraste del 12-11-2026 (segundo material de referencia)
El material del curso solo orientó; cada dato se leyó en la ONU. Fuente principal: **Folleto informativo n.º 30 (Rev.1), ACNUDH, 2012**, PDF en español de la Biblioteca de la ONU en Ginebra (`conf.unog.ch/ls-fts/…/FactSheet30 Rev1_S.pdf`), leído entero.

| Dato | En palabras simples | Dónde lo dice | Estado |
|---|---|---|---|
| Informe inicial y periódicos | Primer informe a más tardar 1 o 2 años después de la entrada en vigor; luego, por lo general, cada 4 o 5 años (no en la Convención sobre desapariciones) | Folleto 30, cap. II.A | `leído en el original` |
| Procedimiento simplificado | Lista de cuestiones previa (CAT, 2007): la respuesta del Estado es su informe periódico; no vale para el inicial | Folleto 30, cap. II.A.4 | `leído en el original` |
| Alerta temprana | Solo el CERD la tiene (desde 1993, sin que la Convención la prevea) | Folleto 30, cap. II.G | `leído en el original` |
| Controversias ante la Corte Internacional de Justicia | CEDAW art. 29, CED art. 42, CAT art. 30, CERD art. 22, CMW art. 92; se puede excluir al ratificar | Folleto 30, cap. II.I; texto de la CED (art. 42) en `data/tratados/IV-16.js` | `leído en el original` |
| Quejas individuales del CMW | No funcionan hasta que 10 Estados hagan la declaración del art. 77 | Folleto 30, nota 9; Colección de Tratados, IV-13 (12-11-2026: menos de 10) | `leído en el original` |
| Primeras quejas entre Estados | Qatar contra Arabia Saudí y contra los Emiratos (8-3-2018) y Palestina contra Israel (23-4-2018), ante el CERD. El Folleto de 2012 aún decía «nunca se ha utilizado» | Comunicados de la Oficina de la ONU en Ginebra (sesiones 99 y 100 del CERD, 2019); decisiones `CERD/C/99/3`, `CERD/C/99/5`, `CERD/C/100/5` | `por verificar` en las decisiones (vistas en resúmenes) |
| Investigación del CRC sobre Francia | Niños migrantes no acompañados: violaciones graves o sistemáticas | `CRC/C/FRA/IR/1` (3-10-2025, publicada el 16-10-2025) | `por verificar` en el original |
| Depositario | El Secretario General; la Colección de Tratados (cap. IV) guarda textos, reservas y objeciones | Folleto 30, glosario; cláusulas finales de cada tratado | `leído en el original` |

**Precisión al material:** las quejas individuales del CMW no fallan por falta de *ratificaciones* sino de *declaraciones* del art. 77 (hacen falta 10).

En la web: pestaña «Cómo supervisa» de cada comité (ciclo de informes, alerta temprana, controversias, CMW, ejemplo del CRC), ficha del tratado (depositario y recursos en español: Folleto 30, Índice Universal, panel de ratificaciones y base de datos de órganos de tratados) y línea de tiempo (1993, 2018 y 2025).

## Consejo de Seguridad: contraste del 12-11-2026 (pedido de Jeisson: «muy flojo»)
Solo fuentes de la ONU; nada del material del curso. La Carta se leyó en `un.org/es/about-us/un-charter` (capítulos V y VII). Las páginas `main.un.org/securitycouncil`, `press.un.org` y `docs.un.org` no se dejaron leer desde el servidor (devuelven una página vacía o solo JavaScript): lo que viene de ellas queda `por verificar` en el original.

| Dato | En palabras simples | Dónde lo dice | Estado |
|---|---|---|---|
| 15 miembros, 10 elegidos por 2 años, sin reelección inmediata | | Carta, art. 23 | `leído en el original` |
| Obligatoriedad | Los Estados miembros aceptan y cumplen sus decisiones | Carta, art. 25 | `leído en el original` |
| Votación y veto | 9 votos; en lo que no es de procedimiento, con el de los 5 permanentes | Carta, art. 27 | `leído en el original` |
| Participación de no miembros | Sin voto, si el asunto les afecta o son parte en la controversia | Carta, arts. 31 y 32 | `leído en el original` |
| Amenaza a la paz, sanciones y fuerza | | Carta, arts. 39, 41 y 42 | `leído en el original` |
| Reparto regional de los 10 elegidos | 5 África y Asia, 1 Europa Oriental, 2 América Latina y el Caribe, 2 Europa Occidental y otros | `A/RES/1991 (XVIII)` A | `por verificar` en el original |
| Presidencia mensual por orden alfabético inglés | | Reglamento provisional `S/96/Rev.7`, art. 18 | `por verificar` |
| Art. 2.7 no impide las medidas del Capítulo VII; art. 103 | | Carta, arts. 2.7 y 103 | `por verificar` en esta lectura (texto conocido de la Carta) |
| Remisiones a la Corte Penal Internacional | Darfur y Libia | `S/RES/1593 (2005)`, `S/RES/1970 (2011)`; Estatuto de Roma, art. 13 b | `por verificar` |
| Ombudsperson y Punto Focal | Vías para salir de una lista | `S/RES/1904 (2009)`, `S/RES/1730 (2006)` | `por verificar` |
| Excepción humanitaria en todas las sanciones | | `S/RES/2664 (2022)` | `por verificar` |
| Casos Kadi (fuera de la ONU) | El Tribunal de Justicia de la UE anuló la aplicación europea de una lista | Asuntos C-402/05 P y C-415/05 P (2008); C-584/10 P (2013) | `por verificar` en curia.europa.eu |
| Situaciones por país (12 fichas) | Comités 1718, 1591, 1970, 1533, 2206, 2653, 2713, 2140, 2127 y 1988; Malí (2374, terminado en 2023) y Siria (sin régimen) | Resoluciones citadas en cada ficha | `por verificar` una a una |

**Dos precisiones al pedido:** el Consejo de Seguridad **no remite situaciones al Consejo de Derechos Humanos** (son órganos separados; sí remite a la Corte Penal y crea comisiones de investigación). Y ante el Consejo **no hay *amicus curiae***: ese escrito existe ante la Corte Penal, una vez remitida la situación.

En la web: ficha «Consejo de Seguridad» de la pantalla del sistema ONU, apartado «Consejo de Seguridad» en la ficha de cada país y la opción «¿Y el Consejo de Seguridad?» de la guía «¿Qué quieres conseguir?». Lo `por verificar` no entra en el asistente T76 hasta leerse en el original.

## Pasos pendientes
1. Leer los **reglamentos vigentes** de los comités con vía de queja y rellenar las cinco filas `por verificar` de arriba (hace falta una vía legítima al texto: a mano o con la persona revisora).
2. Verificar a mano, en la página oficial del ACNUDH, los datos que se vieron en un buscador y no en el original: el **portal en línea** de envío a órganos de tratados y el **límite de 10.000 palabras** que citan resúmenes (aún sin comprobar en el original).
3. Escribir la página «Cómo funciona esto, explicado fácil» y los cuatro campos de cada fila (en español; luego EN/FR y lectura fácil).
4. Revisión externa (T53, `docs/REVISION_EXPERTA.md`): la tabla sale con franja «En pruebas» hasta que alguien la confirme por escrito.
