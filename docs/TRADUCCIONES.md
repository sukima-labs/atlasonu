# Traducciones de la interfaz (T94, T95)

La web está en los seis idiomas oficiales de la ONU. El **código se escribe solo en español**; las traducciones se
hacen aparte, en ficheros JSON, con un **modelo abierto que corre en el servidor del proyecto** (T95, #321), sin
servicios externos. Mientras falte una traducción, ese texto se ve en español.

## Dónde está cada cosa
| Fichero | Qué es | ¿Se edita? |
|---|---|---|
| `idiomas/es.json` | Plantilla: cada texto en español es a la vez su clave y su valor. | Sí: aquí entra todo texto nuevo. |
| `idiomas/en.json`, `fr.json`, `ar.json`, `zh.json`, `ru.json` | Traducciones (clave: el texto en español). | Las rellena `scripts/traducir_local.py`; una persona puede corregirlas a mano. |
| `idiomas/automaticas.json` | Textos traducidos por el modelo, pendientes de revisión por personas nativas (#262). | Al revisar uno, se quita de aquí. |
| `data/idiomas/<ln>.js` | Lo que carga la web. Se genera desde el JSON con `scripts/idiomas.py`. | **No**: se regenera. |

La web carga un `.js` con `<script>` y no el JSON con `fetch` para que la copia descargada siga funcionando abierta
como fichero, sin servidor. `assets/idiomas.js` (el motor) no cambia.

## Al cambiar un texto de la web
1. Escribe el texto en español en `index.html`.
2. `python3 -I scripts/idiomas.py --nuevos` añade a `idiomas/es.json` los textos nuevos de la página. Los que dibuja el
   JavaScript (con `{n}` para una cifra y `{fecha}` para una fecha) se añaden a mano, con la clave igual al valor.
3. **No traduzcas a mano al cambiar un texto** (decisión del 12-11-2026, #291): el PR lleva solo el español. Lo que
   falta lo traduce el modelo local en una **tanda** (un PR solo de traducciones, revisado por la CI). Mientras tanto
   ese texto se ve en español, que es lo previsto.
4. `python3 -I scripts/idiomas.py` regenera `data/idiomas/*.js`.
5. `python3 -I scripts/idiomas_textos.py --comprobar`: **falla** si un texto de la página no está en la plantilla o si una
   traducción cambia las etiquetas (`<b>`, `<a>`…) o las cifras (`{n}`, `{fecha}`); **avisa** de lo que falta traducir.

## Lo que hace la CI
- «Pruebas»: corre la comprobación de arriba. Si el PR solo cambió el JSON (un PR de Weblate), regenera los `.js` con un
  aviso y prueba la web con ellos.
- «Idiomas» (`.github/workflows/idiomas.yml`): cuando cambia `idiomas/` en `main`, regenera `data/idiomas/*.js`, los sube
  como `atlas-onu-bot` y pide a Pages que reconstruya la web.

## Traducción con el modelo local (T95, decidido el 13-11-2026)
- **Modelo:** Qwen3-4B-Instruct-2507 (Q4_K_M, licencia Apache 2.0) con llama.cpp, en sk-atlas. Elegido en una prueba con
  30 textos × 5 idiomas frente a Argos Translate (rompía el HTML en el 43 % de los textos) y Qwen3-8B (igual calidad, el
  doble de lento y de memoria). Resultados en #321.
- **`scripts/traducir_local.py`** traduce solo lo que falta. Cada traducción tiene que conservar las etiquetas y los
  marcadores, estar en el alfabeto del idioma (árabe, chino y ruso) y respetar el nombre «ATLAS ONU»; si no, se
  repite una vez diciéndole qué falló, y si vuelve a fallar se queda en español para la tanda de `atlas-rapido`.
  Prueba sin modelo: `tests/traducir_local_test.py`.
- Se corre como `atlas`, dentro de `atlas-trad.slice` y nunca a la vez que `atlas-textos` (la tarea programada la monta
  `maquina`). `--probar` enseña lo que haría sin escribir; `--max N` y `--idiomas en,fr` acotan.
- Lo traducido queda en `idiomas/automaticas.json` hasta que lo revise una persona nativa (#262). El árabe y el chino
  son lo más flojo del modelo.

## Weblate (descartado el 13-11-2026, #291)
No se usa: Sukima-Labs prefiere no depender de un servicio externo. Si algún día hay voluntarios que traduzcan, los
ficheros siguen siendo compatibles. Configuración que se usaría:
Proyecto en hosted.weblate.org (plan libre) con la cuenta de Sukima-Labs, o una instancia propia. Componente:
- Repositorio: `https://github.com/sukima-labs/atlasonu.git`, rama `main`; envío de cambios como **pull request**.
- Formato: «JSON file» (clave-valor simple). Máscara: `idiomas/*.json`. Plantilla monolingüe: `idiomas/es.json`
  (también como base de las traducciones nuevas). Idioma de origen: español.
- Comprobaciones recomendadas: «Marcas XML» y «Formato» activas; así Weblate avisa al traductor antes de que lo haga la CI.

Los PR de Weblate pasan por la CI como cualquier otro y se fusionan con ella en verde.
