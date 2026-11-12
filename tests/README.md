# tests/

`smoke.cjs` (lógica), `invariantes.cjs` (coherencia de datos) y `browser.cjs` (Chromium real con Playwright). Se ejecutan en el CI en cada pull request.

`pwa.cjs` sirve la web por `http://localhost/atlasonu/` con un servidor mínimo y comprueba que es instalable (manifest e iconos), que el *service worker* se registra, que sin red se abre la portada con el aviso «Sin conexión: datos del …» y que, con red otra vez, llega lo nuevo y no la copia guardada. También va en el CI.
