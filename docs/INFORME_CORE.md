# Documentos básicos comunes («core documents», HRI/CORE) — informe de T20 (29-10-2026)

## Qué son
Cada Estado parte en los tratados de derechos humanos presenta **un documento básico común**: la parte general que sirve de base para todos sus informes a los comités (territorio, población, marco constitucional y jurídico, cómo se protegen los derechos, estadísticas). Se actualiza de vez en cuando y evita repetir esos datos en cada informe. Símbolo en la Biblioteca Digital: `HRI/CORE/<ISO3>/<año>` (los antiguos, `HRI/CORE/1/Add.<n>`). Las pautas para prepararlos están en `HRI/GEN/2/Rev.6`. *(Descripción de conocimiento general; el símbolo exacto de cada país no se ha podido comprobar hoy, ver abajo.)*

## Qué se comprobó hoy (con User-Agent honesto)
| Ruta | Resultado |
|---|---|
| `digitallibrary.un.org/robots.txt` | `Disallow: /search`, `Crawl-Delay: 5` |
| `digitallibrary.un.org/record/<id>` | 202 sin contenido (igual que en T39) |
| `www.ohchr.org/en/treaty-bodies/common-core-documents` | 403 a clientes automáticos |
| `tbinternet.ohchr.org/robots.txt` | `Disallow: /` (ya registrado en T22) |

No hay hoy ruta permitida que devuelva la lista de documentos básicos por país. En el repositorio no hay ningún `HRI/CORE` indexado (`data/fuentes/docs_paises.json`: 0).

## Opciones
1. **Importación manual:** el fundador descarga a mano la lista (ACNUDH/Biblioteca Digital) y se importa con enlace al original. Fiable, pero depende de una persona.
2. **Reintentar `/record/<id>`** más adelante si la Biblioteca Digital deja de responder 202 (hay que tener los identificadores).
3. **Solo enlazar:** en cada ficha de país, un enlace a la base oficial pidiendo filtrar por país, con la explicación de qué es el documento (como se hizo con las comunicaciones en T18).
4. **No usar `/search`**: `fetch_jurisprudencia.py` y `fetch_docs_pais.py` ya lo usan y su robots lo desaconseja (pendiente de revisar en T22); no se amplía ese uso.

## Otros «documentos básicos» que faltan (por confirmar con el fundador)
Pautas armonizadas de presentación de informes (`HRI/GEN/2/Rev.6`), documentos específicos de cada tratado y observaciones generales anteriores (`HRI/GEN/1/Rev.`, ya anotado en T35).

## Recomendación
Hacer la opción 3 ahora (rápida, sin riesgo, aplica la lista de comprobación de interfaz) y dejar la 1 como mejora si el fundador aporta la lista. Decisión del fundador antes de implementar.
