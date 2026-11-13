# Cómo contribuir a ATLAS ONU

Toda ayuda es bienvenida: correcciones, fuentes oficiales que falten, errores de catalogación y mejoras de uso.

## Reglas del proyecto
- **Gratis, abierto y privado:** sin servicios de pago, sin rastreo ni cookies de terceros, sin datos personales.
- **Fuente por cada dato.** Todo dato oficial lleva enlace al original; lo que es elaboración propia se marca como tal. No se inventa ni se traduce lo oficial.
- **Respeto a las fuentes:** solo rutas permitidas por `robots.txt`, ritmo lento, sin eludir bloqueos.
- **Licencias:** código AGPL-3.0 con autoría visible ([NOTICE](NOTICE.md)); contenido propio CC BY 4.0 ([LICENSE-CONTENIDO](LICENSE-CONTENIDO.md)).

## Cómo proponer un cambio
1. Abre una *issue* (hay plantilla para solicitar una verificación) o crea una rama y un *pull request*.
2. Si cambias datos, reconstruye el catálogo: `python3 -I scripts/build_catalog.py data/fuentes/verificacion_simbolos.json <fecha>`.
3. Pasa las pruebas: `node tests/smoke.cjs`, `node tests/invariantes.cjs`, `python3 -I tests/texto_completo_test.py` y `node tests/browser.cjs` (Playwright).
   Textos de la interfaz (T94, detalle en `docs/TRADUCCIONES.md`): el código se escribe solo en español. Un texto nuevo de `index.html` se añade a la plantilla con `python3 -I scripts/idiomas.py --nuevos` (los que dibuja el JavaScript, a mano en `idiomas/es.json`, con la clave igual al valor) y se regeneran los diccionarios con `python3 -I scripts/idiomas.py`. Las traducciones viven en `idiomas/en.json`, `fr.json`, `ar.json`, `zh.json` y `ru.json` y las rellena el modelo local de sk-atlas en una tanda semanal (T95); mientras falte una, ese texto se ve en español. `data/idiomas/*.js` se generan: no se editan a mano. `python3 -I scripts/idiomas_textos.py --comprobar` corre en la CI: falla si un texto de la página no está en la plantilla o una traducción cambia las etiquetas (`<b>`, `<a>`…) o las cifras (`{n}`), y solo avisa de lo que falta traducir. Los datos oficiales no se traducen.
4. Comprueba la pantalla a 390 px de ancho (celular) y en escritorio; `node tests/auditar_ux.cjs --comprobar` mide las metas (controles de 44 px, texto de 13 px, pantallas de unas 8 alturas). Contra la web publicada y la búsqueda real, `node tests/movil_real.cjs` emula tres teléfonos (toques, deslizar el menú, zoom 2×); corre también en Actions → «Celular», a mano y cada lunes.

## Licencia de tu aportación
Al abrir un *pull request* aceptas que tu aportación se publique bajo la licencia del repositorio (AGPL-3.0-only para el código, CC BY 4.0 para el contenido propio) y concedes al titular del proyecto, y a quien le suceda en sus derechos, una licencia perpetua, mundial, no exclusiva y gratuita para usarla, modificarla, distribuirla, sublicenciarla y relicenciarla, también con otros términos. Firma cada commit con `git commit -s` para certificar el [Developer Certificate of Origin](https://developercertificate.org/): que la escribiste tú o tienes derecho a aportarla con esta licencia.

El trabajo pendiente está en [docs/COLA_DE_TAREAS.md](docs/COLA_DE_TAREAS.md).
