# tests/

`smoke.cjs` (lógica), `invariantes.cjs` (coherencia de datos) y `browser.cjs` (Chromium real con Playwright). Se ejecutan en el CI en cada pull request.

`pwa.cjs` sirve la web por `http://localhost/atlasonu/` con un servidor mínimo y comprueba que es instalable (manifest e iconos), que el *service worker* se registra, que sin red se abre la portada con el aviso «Sin conexión: datos del …» y que, con red otra vez, llega lo nuevo y no la copia guardada. También va en el CI.

`componentes.cjs` monta en una pantalla de muestra (que solo existe dentro de la prueba, no en la web ni en el menú) los componentes de `docs/DISENO.md`: pastillas de estado con su fuente, comparador de varios países, asistente paso a paso, línea de tiempo compacta y ficha de delegación. Comprueba, en los dos modos y a 390 y 1280 px, que axe no encuentra incumplimientos, que nada se sale de la pantalla, que la primera columna del comparador se queda fija al deslizar, el asistente con el teclado (aviso si no se elige, foco en cada pregunta, «Atrás», resumen), que «Imprimir la ficha» saca solo la ficha en una hoja y que en inglés todo sale traducido. Con `CAPTURAS=<carpeta>` guarda una captura de cada componente. También va en el CI.
