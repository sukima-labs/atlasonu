# Texto completo de las resoluciones

La búsqueda de la portada busca también **dentro** de las resoluciones, no solo en su ficha. Devuelve el párrafo
donde aparece lo buscado, resaltado, con el símbolo, la lengua y el enlace al PDF oficial.

## Cómo funciona
1. `scripts/texto_completo.py descargar`: toma las rutas al texto ya verificadas (`data/fuentes/textos.json`, estado
   `TEXTO_DIRECTO`) y descarga el PDF oficial en español y en inglés. Prefiere la Biblioteca Digital
   (`digitallibrary.un.org`) y, si no hay, `documents.un.org`. Hace una pausa de 2 s entre descargas para no saturar
   a la ONU y no vuelve a bajar lo que ya tiene.
2. `extraer`: saca el texto con `pdftotext` (poppler, software libre).
3. `indexar`: trocea el texto en párrafos (quita cabeceras, números de página y guiones de corte) y lo guarda en un
   índice SQLite FTS5 que no distingue tildes. El índice se rehace entero en un fichero nuevo y se cambia de golpe,
   así que la búsqueda nunca ve uno a medias.
4. La búsqueda en vivo (`scripts/mini_pc/busqueda_servicio.py`) contesta `GET /texto?q=…[&ln=es|en]` leyendo ese
   índice; no sale a internet. Si todavía no hay índice, contesta 503 y la página no muestra la sección.

`python3 scripts/texto_completo.py todo` hace los tres pasos; `buscar "…"` prueba una consulta desde la terminal.

## Dónde vive
Nada de esto va al repositorio. PDF, textos e índice están en `ATLAS_TEXTOS_DIR`, por defecto
`~/.local/share/atlas-onu/textos` del usuario que corre el servicio. Las 377 resoluciones con PDF propio ocupan unos
40 MB.

## Límites
- Busca **palabras**, no ideas: «visita» no encuentra «visitas». La búsqueda por significado es el paso siguiente.
- Las 28 resoluciones que solo están reproducidas dentro de un informe de sesión aún no entran, porque hay que
  recortar sus páginas del informe.
- El texto sale del PDF tal cual: si el PDF es un escaneo sin capa de texto, ese documento no aparece.

## Pruebas
`python3 -I tests/texto_completo_test.py` (troceo, consultas raras, índice y la ruta `/texto`, sin red) y el bloque
«texto:» de `tests/browser.cjs` (resaltado, sin inyección de HTML, 390 px).
