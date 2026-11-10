# Texto completo de las resoluciones

La búsqueda de la portada busca también **dentro** de los documentos, no solo en su ficha: las resoluciones y,
por país, las observaciones finales de los comités, los documentos del EPU y los informes de visita de los relatores. Devuelve el párrafo
donde aparece lo buscado, resaltado, con el símbolo, la lengua y el enlace al PDF oficial.

## Cómo funciona
1. `scripts/texto_completo.py descargar`: toma las rutas al texto ya verificadas (`data/fuentes/textos.json`, estado
   `TEXTO_DIRECTO`) y los documentos de cada país (`data/paises/<ISO>.js`), y descarga el PDF oficial en español y
   en inglés. Primero las resoluciones y después los documentos de país, de los más recientes a los más antiguos
   (hoy, unos 4.500 documentos y 7.900 PDF; la primera descarga tarda unas 11 horas). Además, desde T68 (c), los 740 informes del Grupo de Trabajo del EPU (`A/HRC/<sesión>/<n>`) y sus adiciones, de `data/fuentes/epu_informes.json` (unos 1.400 documentos más). Prefiere la Biblioteca Digital
   (`digitallibrary.un.org`) y, si no hay, `documents.un.org`. Respeta el `Crawl-Delay: 5` de su `robots.txt` (5 s entre descargas)
   y no vuelve a bajar lo que ya tiene.
2. `extraer`: saca el texto con `pdftotext` (poppler, software libre).
3. `indexar`: trocea el texto en párrafos (quita cabeceras, números de página y guiones de corte) y lo guarda en un
   índice SQLite FTS5 que no distingue tildes. El índice se rehace entero en un fichero nuevo y se cambia de golpe,
   así que la búsqueda nunca ve uno a medias.
4. La búsqueda en vivo (`scripts/mini_pc/busqueda_servicio.py`) contesta `GET /texto?q=…[&ln=es|en]` leyendo ese
   índice; no sale a internet. Si todavía no hay índice, contesta 503 y la página no muestra la sección.

`python3 scripts/texto_completo.py todo` hace los tres pasos y, mientras descarga, reindexa cada 300 PDF nuevos (la primera vez tarda horas y así la búsqueda va creciendo); `buscar "…"` prueba una consulta desde la terminal.

## Búsqueda por significado
Si el servicio corre con `/opt/atlas-venv` (fastembed y numpy) y el modelo está en `~/modelos`
(`ATLAS_MODELOS_DIR`), cada párrafo se guarda también como vector dentro del mismo índice. La búsqueda mezcla
palabras (BM25) y significado (coseno ≥ 0,5) por rango recíproco: «visitas sin previo aviso» encuentra «To conduct
country visits», en inglés. El modelo es `paraphrase-multilingual-MiniLM-L12-v2` (Apache-2.0), corre en local
en el procesador y no envía nada a terceros. Los vectores ya calculados se guardan en `vectores_cache.sqlite`, así
que reindexar solo calcula los párrafos nuevos. Sin ese entorno, todo funciona igual pero solo con palabras: eso es
lo que prueba la CI. La web marca con «por significado» los párrafos que no contienen las palabras buscadas.

## Dónde vive
Nada de esto va al repositorio. PDF, textos e índice están en `ATLAS_TEXTOS_DIR`, por defecto
`~/.local/share/atlas-onu/textos` del usuario que corre el servicio. Con todo descargado ocupa unos pocos GB.

## Límites
- Las 28 resoluciones que solo están reproducidas dentro de un informe de sesión aún no entran, porque hay que
  recortar sus páginas del informe.
- El texto sale del PDF tal cual: si el PDF es un escaneo sin capa de texto, ese documento no aparece.

## Pruebas
`python3 -I tests/texto_completo_test.py` (troceo, consultas raras, índice y la ruta `/texto`, sin red) y el bloque
«texto:» de `tests/browser.cjs` (resaltado, sin inyección de HTML, 390 px).

## Preguntar a los documentos (IA con citas)
Debajo de «Dentro de los textos» hay un botón **Preguntar a los documentos** (cuando lo escrito tiene al menos 8
letras). Al pulsarlo, `scripts/preguntar.py` toma los 8 párrafos más pertinentes (uno por documento) y le pide a un
modelo de OpenCode Go (`glm-5.3-flash`, cambiable con `ATLAS_MODELO_IA`) que responda **solo** con ellos y que cite
cada afirmación con `[n]`. Después se comprueba la respuesta: se quitan las citas a párrafos que no se le dieron y, si
no queda ninguna válida, no se muestra respuesta, solo los párrafos. Si los párrafos no bastan, el modelo lo dice.

- **Qué sale del servidor:** la pregunta y párrafos públicos de la ONU. Ni IP, ni cookies, ni identificadores. La web
  solo pregunta cuando la persona pulsa el botón, y antes le dice que la pregunta va a un servicio de IA externo.
- **Límites:** 10 preguntas nuevas por minuto en total; las repetidas salen de una caché de una hora. Solo se atiende
  si la petición viene de la página (`Origin`).
- **Clave:** `OPENCODE_GO_API_KEY`, fuera del repositorio (en el servidor, `/etc/atlas/opencode.env`). Sin clave,
  `/preguntar` contesta 503 y la web dice que ahora no se puede preguntar.
