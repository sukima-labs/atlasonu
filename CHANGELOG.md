# Registro de cambios

## 0.7 · 31-10-2026
Versión actual. Cambios desde la auditoría de seguridad y mantenimiento (ver `docs/COLA_DE_TAREAS.md` para el detalle de cada tarea):

- **Copias de seguridad cifradas** semanales y plan de recuperación (T45, `docs/RECUPERACION.md`).
- **Permisos del repositorio:** cambio revertido que quitaba los bloqueos de force-push (T43, PR 97).
- **Mantenimiento:** scripts de prototipo retirados de `scripts/`, `archive/` sacado del repositorio (copia fuera), campo `huella` quitado, enlaces a la web pública antigua quitados (T46, PR 99).
- **Auditoría y documentación al día:** `audit/AUDITORIA.md`, `docs/INFORME_EVALUACION_GLOBAL.md` y `docs/OPERACION.md` (T47).
- **Skill `trabajar-cola`** para el modo continuo de la cola (PR 100).
- **Fichas citables:** cita APA 7 y descarga en Word (`.docx`) en la ficha de cada mandato y de cada país (T59).
- **Descargas:** pantalla «Descargas» con licencia, CSV de mandatos, JSON de países y archivos del repositorio (T60).

## Sin versión aún · desde el 08-11-2026
- **Mapa del mundo con capas** (pantalla nueva): cada país se colorea por tratados básicos aceptados, un tratado concreto, invitación permanente, mandato propio o comisión de investigación; al tocarlo se llega a su ficha. SVG propio con contornos de dominio público (Natural Earth), sin servicios externos; lista con los mismos datos, zoom y traducciones a los cinco idiomas (T11/T24, `docs/MAPAS.md`).
- **Mapa: dos capas más** (T68): conflictos armados por año (UCDP/PRIO, CC BY 4.0, 1946–2025) y comunicaciones de los relatores recibidas por cada país (cifras oficiales de 2019 a 2022). Sin cambios de servicios; `data/conflictos.js` se carga solo al elegir la capa (`docs/MAPAS.md`).
- **Mapa: recomendaciones del EPU por ciclo** (T68 c): cuántas recomendaciones recibió cada país en su Examen Periódico Universal, con selector de ciclo (2.º, 3.º y 4.º). Contadas de los informes del Grupo de Trabajo (740 informes de 193 países, bajados de la Biblioteca Digital de la ONU): 528 de 550 informes de los ciclos 2 a 4 tienen cifra; los otros 22 (erratas del original o formato distinto) salen «sin cifra» en vez de un número dudoso. `data/epu.js`, `tests/epu_recomendaciones_test.py`.
- **Imprimir una pantalla** (T58): al imprimir o guardar en PDF sale solo la pantalla abierta, en claro y sin menú ni botones (antes salían las 20 pantallas juntas sobre fondo oscuro: de 63 a 74 hojas; ahora de 2 a 11). `tests/impresion.cjs`, en la CI.
- **Abrir una pantalla por su enlace** (`#relatores`, `#noticias`, `#mapa`): antes, `#relatores` caía en Panorama.
- **Comparador de dos países** en la pantalla Países: 28 aspectos lado a lado y «Solo lo que cambia» (T61).
- **Línea de tiempo por país** en cada ficha: tratados, invitación, mandato o comisiones, observaciones finales, EPU y visitas por años, con filtros y orden (T62).
- **Glosario de siglas al tocar:** las siglas del texto salen subrayadas y al tocarlas muestran su significado en español e inglés (T63).
- **Relatores y relatoras:** pantalla nueva con quién ejerce hoy cada mandato, su nacionalidad y enlaces al mandato y a las fichas de país; buscador y filtros (T40).
- **Accesibilidad WCAG 2.2 AA:** cada control tiene nombre, los enlaces del texto van subrayados y los enlaces miden al menos 24 px para el dedo; una prueba con axe-core revisa todas las pantallas del menú en cada cambio (T27, `docs/ACCESIBILIDAD.md`).
- **Lectura fácil** en Inicio, Mandatos, Cómo funciona la ONU y Países: un bloque desplegable con frases cortas, en español, inglés y francés (T65).
- **Árabe, chino y ruso** en la interfaz: ya están los seis idiomas oficiales de la ONU; el árabe se lee de derecha a izquierda (T66).
- **Traducciones más completas:** las frases de la ficha de país con su nombre dentro y las explicaciones con la fecha de los datos se traducen enteras, y las fechas de ratificación se escriben al modo de cada idioma (T67).

## Anteriores
- Versiones previas a 0.7 están en el historial de git.
