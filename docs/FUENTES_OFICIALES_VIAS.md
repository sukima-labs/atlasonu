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
| Comité contra la Tortura, CEDAW, Personas con Discapacidad, Desapariciones Forzadas, Trabajadores Migratorios | **Por verificar** (no se extrajo plazo en esta pasada) | Por verificar |

Todo lo demás de la ficha (formularios modelo para el Comité de Derechos Humanos, el de Tortura y el de Discriminación contra la Mujer) es la base del **borrador de campos** de la fase 4 opcional de T76.

## Procedimientos especiales (relatores y grupos de trabajo)
No son «quejas» con plazo y admisibilidad: se envían **comunicaciones** (alegaciones, acciones urgentes) y el relator decide si actúa. Hay que leer: los **métodos de trabajo** y el **Código de conducta** (resolución 5/2 del Consejo de Derechos Humanos) y la página oficial de envío de información. Todo `por verificar` (la página da 403).

## Pasos pendientes
1. Leer los **reglamentos vigentes** de los comités con vía de queja y rellenar las cinco filas `por verificar` de arriba (hace falta una vía legítima al texto: a mano o con la persona revisora).
2. Verificar a mano, en la página oficial del ACNUDH, los datos que se vieron en un buscador y no en el original: el **portal en línea** de envío a órganos de tratados y el **límite de 10.000 palabras** que citan resúmenes (aún sin comprobar en el original).
3. Escribir la página «Cómo funciona esto, explicado fácil» y los cuatro campos de cada fila (en español; luego EN/FR y lectura fácil).
4. Revisión externa (T53, `docs/REVISION_EXPERTA.md`): la tabla sale con franja «En pruebas» hasta que alguien la confirme por escrito.
