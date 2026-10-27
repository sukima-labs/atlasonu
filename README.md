# ATLAS ONU — Arqueología documental de Naciones Unidas

Plataforma académica independiente para investigar los procedimientos especiales de la ONU y recuperar sus documentos originales **con verificación contra la fuente oficial**.

**Autor:** Jeisson Arley Osorio Mesa, estudiante del Máster en Protección Internacional de los Derechos Humanos (Universidad de Alcalá, España) · © 2026. **Licencias:** código bajo [MIT](LICENSE); contenido propio bajo [CC BY 4.0](LICENSE-CONTENIDO.md); los datos y textos de la ONU no se relicencian (ver [análisis](docs/LICENCIA.md)).
**Aviso:** iniciativa académica independiente. No es un producto oficial de Naciones Unidas ni de la Universidad de Alcalá.

## Se actualiza sola
Cada día (04:17 UTC) un flujo de GitHub Actions (`.github/workflows/actualizar-datos.yml`) vuelve a consultar las fuentes oficiales —índice de mandatos y visitas de OHCHR, y Biblioteca Digital de la ONU—, verifica de nuevo cada símbolo, detecta qué cambió y, **solo si los datos no se degradan**, lo publica. La plataforma muestra la fecha de la última revisión, las novedades detectadas y avisa si hay datos más recientes que los de la copia abierta.
- **Salvaguardas:** un fallo de red aborta sin publicar; si caen los actos localizados, los textos o los mandatos, no se publica (`scripts/validar_datos.py`); las pruebas de invariantes deben pasar (`tests/invariantes.cjs`).
- **Sin ruido:** si no cambió nada, solo se actualiza `data/estado.json` (sello de última revisión).
- **A mano:** `bash scripts/actualizar_datos.sh`.
- **Límite:** el navegador no puede consultar la ONU en directo (las fuentes no lo permiten); por eso la actualización la hace GitHub y la página la lee.

## Qué hace la versión 0.7
- **57 mandatos vigentes** (44 temáticos y 13 por país) tomados del índice oficial de OHCHR, con titulares actuales.
- **421 actos jurídicos** (creación, prórrogas) contrastados uno a uno con la Biblioteca Digital de la ONU: 401 localizados, 20 con reservas explicadas.
- **Ruta al texto de las 400 resoluciones localizadas:** 374 con PDF propio (comprobado leyendo su primera página; muestreo del registro 30/30) y 26 antiguas reproducidas en un informe de sesión, con páginas (p. ej. `E/CN.4/RES/1985/33` → `E/1985/22`, pp. 71–72).
- **25 mecanismos conexos** verificados: los 10 órganos de tratados (datos de la diapositiva del curso de la UAH), EPU, procedimientos 1235 y 1503, EMRIP, Foro de Minorías, ACNUDH y 8 comisiones de investigación / misiones.
- **Búsqueda inteligente** en la portada: entiende sinónimos ES/EN («desaparecidos», «comida», «niños migrantes»), corrige erratas («tortrua») y muestra, mientras escribes, mandatos, resoluciones y mecanismos relacionados con acceso directo a la ficha o al texto.
- **Ficha de cada país (196):** al elegir un país se ve su perfil completo: grupo regional, invitación permanente y visitas, **estado de ratificación de los 18 instrumentos de derechos humanos** (Colección de Tratados de la ONU), mandato propio, 10 subtemas para ver qué relatores pueden actuar, comisiones y titulares con esa nacionalidad, y enlaces a las bases oficiales de comunicaciones y visitas.
- **Países (antes):** sección con buscador y listado de 62 países (mandato específico, comisiones/misiones y titulares con esa nacionalidad). Al elegir un país muestra además los 44 mandatos temáticos que pueden dirigirle comunicaciones, filtrables por tema; también se puede indicar el país en la búsqueda guiada. Filtro por país en el explorador y tarjeta de país en la búsqueda inteligente.
- **Grupos regionales de la ONU** (África, Asia-Pacífico, Europa Oriental, América Latina y el Caribe, Europa Occidental y otros, más «Otro»): botones en Países, filtro en el explorador y etiqueta en cada ficha. La clasificación de cada país procede de la base oficial de comunicaciones de OHCHR (`data/fuentes/regiones_ohchr.json`), no es nuestra.
- **Búsqueda guiada** para quien no conoce la ONU, filtro de verificación, Excel descargable (`data/atlas-onu-catalogo-v07.xlsx`).
- **Arqueología documental real:** una resolución se localiza aunque el símbolo esté mal escrito (`A/HRC/54/26`, `E/CN.4/1991/42`, `20 (XXXVI)`), un borrador `L.` se traduce a la resolución adoptada y la ficha enlaza el registro y los PDF en español e inglés.
- **Distingue resolución, informe y borrador.** Si un símbolo existe pero es un informe, lo dice. Si una equivalencia es inferida, lo dice.
- **Un caso con texto leído:** la resolución 20 (XXXVI) de 1980 (Grupo de Trabajo sobre Desapariciones) está reproducida en E/1980/13, pp. 180–181; se leyó el PDF (`data/evidencias.json`).

## Abrir
Abrir `index.html` en cualquier navegador (también sin conexión: los datos van en `data/atlas-data.js`).
**Web pública (activa):** https://cataplum1414.github.io/onu-arqueologia-documental/ (Settings → Pages → *Build and deployment* → Source: **Deploy from a branch** → Branch: `main`, carpeta `/ (root)` → Save; tarda ~1 minuto).

## Estructura
| Ruta | Contenido |
|---|---|
| `index.html` | Aplicación |
| `data/` | `catalogo.json` y `atlas-data.js` (generados), `fuentes/` (descargas oficiales y verificación), `evidencias.json`, Excel del piloto |
| `scripts/` | Descarga, normalización, verificación y construcción (`actualizar_datos.sh` ejecuta todo) |
| `tests/` | `smoke.cjs` (114 pruebas de lógica, `invariantes.cjs`: 11) y `browser.cjs` (Chromium real, 147 comprobaciones, escritorio y móvil) |
| `audit/` | Auditoría contra los 13 requisitos, discrepancias respecto a v0.6, inventario, manifiesto de integridad |
| `docs/` | Traspaso original |
| `archive/` | Versiones previas sin modificar |

## Reproducir
```
bash scripts/actualizar_datos.sh        # regenera datos (necesita red)
cd tests && node smoke.cjs               # lógica
npm i playwright && node tests/browser.cjs   # navegador real   # con ATLAS_CAPTURAS=1 regenera las capturas de audit/
```

## Si la página no abre
Si falla la descarga de datos o el navegador no es compatible, la página muestra un aviso con instrucciones (recarga sin caché, ventana privada, otra red, copia sin conexión) en lugar de quedarse en blanco. Los datos se cargan con un parámetro de versión que cambia cada 5 minutos para evitar que el navegador mezcle una página antigua con datos nuevos.

## Qué hacer si falta algo
Cuando una búsqueda no da resultado, la plataforma ofrece **Solicitar verificación**: abre un formulario público de GitHub ya rellenado con lo buscado. Nada se añade al catálogo por haberse pedido; solo entra lo que se contrasta con una fuente oficial. Proceso: [`docs/PROCESO_DE_VALIDACION.md`](docs/PROCESO_DE_VALIDACION.md).

## Procedencia de la información
Ver en la plataforma «Fuentes y alcance → Qué es dato oficial y qué es elaboración propia». Resumen: mandatos, símbolos y titulares vienen de OHCHR; títulos, fechas y PDF, de la Biblioteca Digital ONU; el diccionario de sinónimos, los nombres de países en español y los avisos son elaboración propia y no sustituyen la fuente.

## Límites (ver `audit/AUDITORIA.md`)
Solo mandatos **vigentes**: faltan los extinguidos. Las comisiones de investigación listadas son una selección verificada, no el universo. No hay mapas. Las explicaciones en lenguaje claro de cada resolución no están redactadas. «Localizado» significa que existe un registro con ese símbolo exacto; no sustituye leer el texto.


## Documentos oficiales por país

Cada ficha de país carga, bajo demanda (`data/paises/<ISO>.js`), las observaciones finales de los comités de tratados, los documentos del Examen Periódico Universal y los informes de misiones de procedimientos especiales, todos obtenidos de la Biblioteca Digital de la ONU con coincidencia exacta de materia (`scripts/fetch_docs_pais.py`) y refrescados a diario. Las comunicaciones individuales de los relatores no son automatizables y se enlazan a la base oficial.

## Cómo funciona la ONU y Tratados y comités

- **Cómo funciona la ONU** (`sistema`): mapa clicable de los órganos principales, el Consejo de Derechos Humanos y lo que cuelga de él; la **familia de la ONU** (41 entidades: Secretaría, fondos y programas, organismos especializados, comisiones regionales, organizaciones relacionadas) con sus conexiones a comités y mandatos; una guía «¿ante quién reclamo?» y un descifrador de símbolos documentales. Datos de elaboración propia en `data/sistema_onu.json` (declarado como no oficial).
- **Tratados y comités** (`tratados`): los nueve tratados principales, su comité, los procedimientos de supervisión (informes, comunicaciones individuales, investigaciones, etc., con el artículo de cada uno), los **Estados parte** (de la Colección de Tratados, con enlace a cada ficha de país) y el **texto literal** artículo por artículo cuando la copia oficial tiene texto digital fiable.
- **Texto literal**: `scripts/fetch_tratados_texto.py` lo toma del anexo de la resolución de la Asamblea General (solo textos digitales, de 1999 en adelante) y, para la CEDAW, de la página de la ONU contrastada palabra a palabra con la copia depositaria (18 erratas evidentes corregidas y listadas). Cada instrumento se valida (numeración 1..N y número de artículos). Los tratados anteriores, cuyo único ejemplar digital es un escaneo con errores de reconocimiento, **no se transcriben**: se enlazan al original.

## Siglas y acrónimos

Diccionario con 145 entradas (`data/siglas.json`, elaboración propia sobre fuentes oficiales): cada sigla se da en **inglés y en español**, con qué es, sinónimos y abreviaturas españolas de uso académico, y un botón al lugar del tablero donde se profundiza. El buscador tolera erratas («cedau»), guiones («OP-CEDAW») y palabras del nombre («examen periódico»), y descifra símbolos documentales. También alimenta la búsqueda inteligente del Panorama.

## Créditos y uso

Los datos oficiales son de las Naciones Unidas y proceden de sus sitios públicos (OHCHR, Biblioteca Digital, Colección de Tratados). Solo se leen metadatos públicos y se citan textos de tratados con su fuente; cada dato enlaza al documento oficial. Proyecto académico, independiente y sin fines de lucro. Lo que es elaboración propia está marcado como tal.

## Licencia

Código: **MIT** (`LICENSE`). Contenido propio (siglas, cuadros, explicaciones, documentación): **CC BY 4.0** (`LICENSE-CONTENIDO.md`). Los documentos, símbolos, títulos, textos de tratados y datos de ratificación son de las Naciones Unidas y no se relicencian. El análisis de por qué esta combinación está en `docs/LICENCIA.md`. Cómo citar: `CITATION.cff`.
