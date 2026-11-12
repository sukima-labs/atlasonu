# Traducciones de la interfaz (T94)

La web está en los seis idiomas oficiales de la ONU. El **código se escribe solo en español**; las traducciones se
hacen aparte, en ficheros que puede editar [Weblate](https://weblate.org) (libre y gratuito para proyectos abiertos),
donde ayudan personas que no programan. Mientras falte una traducción, ese texto se ve en español.

## Dónde está cada cosa
| Fichero | Qué es | ¿Se edita? |
|---|---|---|
| `idiomas/es.json` | Plantilla: cada texto en español es a la vez su clave y su valor. | Sí: aquí entra todo texto nuevo. |
| `idiomas/en.json`, `fr.json`, `ar.json`, `zh.json`, `ru.json` | Traducciones (clave: el texto en español). | En Weblate (o a mano). |
| `data/idiomas/<ln>.js` | Lo que carga la web. Se genera desde el JSON con `scripts/idiomas.py`. | **No**: se regenera. |

La web carga un `.js` con `<script>` y no el JSON con `fetch` para que la copia descargada siga funcionando abierta
como fichero, sin servidor. `assets/idiomas.js` (el motor) no cambia.

## Al cambiar un texto de la web
1. Escribe el texto en español en `index.html`.
2. `python3 -I scripts/idiomas.py --nuevos` añade a `idiomas/es.json` los textos nuevos de la página. Los que dibuja el
   JavaScript (con `{n}` para una cifra y `{fecha}` para una fecha) se añaden a mano, con la clave igual al valor.
3. Si sabes la traducción, ponla en `idiomas/<ln>.json`; si no, déjala para Weblate.
4. `python3 -I scripts/idiomas.py` regenera `data/idiomas/*.js`.
5. `python3 -I scripts/idiomas_textos.py --comprobar`: **falla** si un texto de la página no está en la plantilla o si una
   traducción cambia las etiquetas (`<b>`, `<a>`…) o las cifras (`{n}`, `{fecha}`); **avisa** de lo que falta traducir.

## Lo que hace la CI
- «Pruebas»: corre la comprobación de arriba. Si el PR solo cambió el JSON (un PR de Weblate), regenera los `.js` con un
  aviso y prueba la web con ellos.
- «Idiomas» (`.github/workflows/idiomas.yml`): cuando cambia `idiomas/` en `main`, regenera `data/idiomas/*.js`, los sube
  como `atlas-onu-bot` y pide a Pages que reconstruya la web.

## Conectar Weblate
Proyecto en hosted.weblate.org (plan libre) con la cuenta de Sukima-Labs, o una instancia propia. Componente:
- Repositorio: `https://github.com/sukima-labs/atlasonu.git`, rama `main`; envío de cambios como **pull request**.
- Formato: «JSON file» (clave-valor simple). Máscara: `idiomas/*.json`. Plantilla monolingüe: `idiomas/es.json`
  (también como base de las traducciones nuevas). Idioma de origen: español.
- Comprobaciones recomendadas: «Marcas XML» y «Formato» activas; así Weblate avisa al traductor antes de que lo haga la CI.

Los PR de Weblate pasan por la CI como cualquier otro y se fusionan con ella en verde.
