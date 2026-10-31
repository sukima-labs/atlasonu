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
3. Pasa las pruebas: `node tests/smoke.cjs`, `node tests/invariantes.cjs` y `node tests/browser.cjs` (Playwright).
4. Comprueba la pantalla a 390 px de ancho (celular) y en escritorio.

El trabajo pendiente está en [docs/COLA_DE_TAREAS.md](docs/COLA_DE_TAREAS.md).
