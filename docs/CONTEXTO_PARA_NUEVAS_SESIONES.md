# Contexto para retomar el proyecto en una sesión nueva

Lee esto primero si abres una sesión de Claude Code (por ejemplo, en el mini PC) sobre este repositorio.

## Qué es
**ATLAS ONU – Arqueología documental**: plataforma académica, independiente y sin fines de lucro, sobre el sistema de derechos humanos de la ONU (mandatos de procedimientos especiales, tratados y comités, países, historia, siglas). Autor: Jeisson Arley Osorio Mesa, estudiante del Máster en Protección Internacional de los Derechos Humanos (Universidad de Alcalá). No es oficial de la ONU ni de la universidad.

- Sitio público: https://cataplum1414.github.io/onu-arqueologia-documental/ (GitHub Pages, rama `main`).
- Repositorio: `cataplum1414/onu-arqueologia-documental`. Flujo habitual: rama de trabajo → PR → fusión en `main`.

## Cómo está hecho
Sitio estático: `index.html` + `data/atlas-data.js` (generado) + archivos diferidos `data/paises/<ISO>.js` y `data/tratados/<id>.js`. Datos oficiales con Python (`scripts/`), pruebas con Node y Playwright.

| Qué | Dónde |
|---|---|
| Actualización completa de datos | `bash scripts/actualizar_datos.sh` (GitHub Actions a las 12:17 y 00:17 hora de España en invierno; opcional en el mini PC, `docs/MINI_PC.md`) |
| Reconstruir el catálogo | `python3 -I scripts/build_catalog.py data/fuentes/verificacion_simbolos.json <fecha>` |
| Pruebas | `node tests/smoke.cjs` · `node tests/invariantes.cjs` · `node tests/browser.cjs` (Playwright; `ATLAS_URL=<https>` para probar la web publicada) |
| Contenido propio (CC BY 4.0) | `data/siglas.json`, `data/sistema_onu.json`, `data/historia.json` |
| Textos literales de tratados | `scripts/fetch_tratados_texto.py` → `data/fuentes/tratados_texto.json` |

## Método y tareas pendientes
Ver `docs/COLA_DE_TAREAS.md`: una tarea por sesión, commit y push al terminar, y `/clear` antes de la siguiente.

## Reglas que no se rompen
1. **No inventar datos.** Una ruta sugerida no es un documento recuperado; una resolución no es el informe que la contiene; lo inferido se etiqueta.
2. **Todo lo oficial es de la ONU** y se atribuye y enlaza. Lo de elaboración propia se marca como tal.
3. **Las salvaguardas abortan sin publicar** si falla la red o los datos se degradan (`validar_datos.py`, pruebas de invariantes). No se saltan.
4. **No eludir bloqueos de bots** (por ejemplo, OHCHR bloquea clientes automáticos): no se simula un navegador; se enlaza al original.
5. **Privacidad:** no incluir en el repositorio grabaciones, transcripciones ni resúmenes de clases, ni datos personales de docentes u otras personas.
6. **Licencias:** código AGPL-3.0 con autoría visible obligatoria (`NOTICE.md`), contenido propio CC BY 4.0, datos de la ONU sin relicenciar (`docs/LICENCIA.md`).
7. **Pruebas antes de publicar**, y las cifras del README y de `audit/AUDITORIA.md` se mantienen al día.

## Estado
Pantallas: Panorama (portada), Explorar mandatos, Cómo funciona la ONU (mapa, familia de 41 entidades, ¿ante quién reclamo?, descifrador de símbolos), Su historia (línea de tiempo), Países (196 fichas con documentos oficiales), Tratados y comités (texto literal de 8 instrumentos), Siglas y acrónimos (145), Arqueología, Recuperar documentos, Otros mecanismos, Códigos, Selección de titulares, Alertas de verificación (con panel de exactitud de números), Fuentes y alcance.

## Pendiente (por orden de interés)
1. Índice de jurisprudencia: observaciones generales y dictámenes de los comités.
2. Recomendaciones del EPU por país (aceptadas / «tomó nota»).
3. ODS cruzados con tratados; sistemas regionales; Consejo de Seguridad y derechos humanos; financiación; composición del Consejo de Derechos Humanos.
4. Fragmentos literales de resoluciones con página; mandatos extinguidos.
5. Explicaciones en lenguaje sencillo revisadas por un especialista; accesibilidad con lector de pantalla y prueba en teléfonos reales.
6. Comunicaciones individuales de los relatores: la base de OHCHR no permite consulta automática; solo se enlaza.

## Cosas a vigilar
- La Biblioteca Digital de la ONU limita el ritmo de consultas: el verificador reintenta, y si fallan pocas consultas conserva lo ya verificado (aborta si pasan del 3 %).
- El contador de visitas es propio: lo sirve `atlas-busqueda.service` del mini PC (`/visita` suma, `/visitas` lee) y guarda solo total y cifra por país en `~/.local/share/atlas-onu/visitas.json` (sin IP ni cookies); no cuenta en pruebas, en copias locales ni con `?sinvisita`.
- Las capturas de `audit/` solo se regeneran con `ATLAS_CAPTURAS=1 node tests/browser.cjs`.
