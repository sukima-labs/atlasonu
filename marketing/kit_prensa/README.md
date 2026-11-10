# Kit de prensa

Para quien quiera escribir sobre ATLAS ONU o enlazarlo. Las cifras salen de [`CIFRAS.md`](CIFRAS.md) (generado desde `data/`; no se escriben a mano).

## Descripción en una línea (≤ 140 caracteres)
Atlas gratuito y sin rastreo para entender cómo protege la ONU los derechos humanos, con los documentos oficiales delante.

## Descripción corta (≈ 50 palabras)
ATLAS ONU es una plataforma académica independiente, en español y en cinco idiomas más, para encontrar y citar documentos del sistema de derechos humanos de la ONU: mandatos de relatores, tratados y comités, fichas de 196 países, historia y siglas. Cada dato enlaza a su fuente oficial. Gratuita, de código abierto y sin rastreo.

## Descripción larga
ATLAS ONU ordena el sistema de derechos humanos de las Naciones Unidas para quien no lo conoce y para quien necesita citarlo con rigor. Reúne los mandatos vigentes de relatores y grupos de trabajo, los actos jurídicos que los crearon y prorrogaron (contrastados uno a uno con la Biblioteca Digital de la ONU), los tratados y sus comités, la ficha de cada país (ratificaciones, Examen Periódico Universal, observaciones finales, visitas), una línea de tiempo de la historia y un diccionario de siglas.

Se puede escribir lo que se busca «como se habla», buscar dentro del texto de las resoluciones y de los documentos de cada país, y hacer una pregunta a los documentos: una IA redacta la respuesta solo con los párrafos encontrados y cita cada uno. Un mapa del mundo colorea a cada país según los tratados que ha aceptado, su mandato propio u otras capas.

Se revisa dos veces al día contra las fuentes oficiales y no se publica si los datos se degradan. Cumple las reglas medibles de accesibilidad WCAG 2.2 AA. El código es AGPL-3.0 y el contenido propio, CC BY 4.0; los documentos de la ONU no se relicencian.

**Aviso:** iniciativa académica independiente de Sukima-Labs. No es un producto oficial de Naciones Unidas ni de ninguna universidad.

## Enlaces
- Web: https://sukima-labs.github.io/atlasonu/
- Código: https://github.com/sukima-labs/atlasonu
- Cómo citar: `CITATION.cff` del repositorio
- Licencias: https://github.com/sukima-labs/atlasonu/blob/main/NOTICE.md

## Para qué sirve (casos concretos)
- Encontrar el mandato de relator que corresponde a una situación (tortura, desapariciones, vivienda, libertad de expresión…) y leer qué resoluciones lo crearon.
- Saber qué tratados ha ratificado un país y qué ha dicho de él cada comité.
- Localizar una resolución antigua aunque el símbolo esté mal escrito, y enlazar su PDF oficial.
- Citar en APA 7 una ficha, con descarga en Word.

## Material gráfico
Las capturas se generan con `tests/browser.cjs` (`ATLAS_CAPTURAS=1`, en `audit/`) y la marca está en `assets/marca/`. La imagen para compartir (1200×630) es la tarea T69.

## Contacto
Por el repositorio: https://github.com/sukima-labs/atlasonu/issues (no se publican correos personales).
