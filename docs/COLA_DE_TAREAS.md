# Cola de tareas de ATLAS ONU

## Método de trabajo (decisión del fundador, 28-10-2026)
**Una tarea, una sesión.** Se hace la primera tarea pendiente de esta cola, se prueba, se hace commit y push (rama → PR → fusión en `main` cuando el CI esté en verde) y se marca aquí como hecha. Después el fundador escribe `/clear` y la sesión siguiente empieza por la tarea que toque. Así se gasta menos contexto.
Al empezar: leer `docs/CONTEXTO_PARA_NUEVAS_SESIONES.md` y esta cola. Las reglas de ese archivo no se rompen (no inventar datos, atribuir a la ONU, pruebas antes de publicar).

## Estado del entorno (28-10-2026)
- Sitio: https://cataplum1414.github.io/onu-arqueologia-documental/ — GitHub Pages publica desde `main` (antes estaba mal apuntado a otra rama).
- El mini PC ejecuta la revisión a las 12:00 y 00:00 (`atlas-onu.timer`) y el servicio de búsqueda en vivo (`atlas-busqueda.service`, puerto 8787), publicado con Tailscale Funnel en `https://dignityos.tailaa1f76.ts.net:10000`. DIGNITYOS usa 443 y 8443 solo en la red privada: no tocarlos. Apagar la exposición: `tailscale funnel --https=10000 off`.
- Búsqueda en vivo: desde un equipo con Tailscale activo Chrome puede pedir un permiso de red local y la consulta no responde; la página corta la espera a los 10 s. Pendiente de confirmar en el celular del fundador con Tailscale apagado.

## Tareas

| # | Tarea | Estado |
|---|---|---|
| T1 | Documentos marco de los procedimientos especiales: Código de conducta (A/HRC/RES/5/2), 5/1 y A/RES/60/251 | **hecha** (PR #30) |
| T2 | **Novedades y registro de actualizaciones.** Hoy el panel dice «Todavía no se ha detectado ningún cambio» porque `historial_cambios.json` está vacío (la fecha de revisión sí se actualiza). Añadir un registro visible de cada ejecución (quién la hizo, hora, qué revisó, resultado, duración) en `data/revisiones.json` y mostrarlo en la página, para dar visibilidad y fiabilidad | pendiente |
| T3 | **Noticias: frecuencia, importancia y archivo.** Hoy se actualizan en cada revisión (12:00 y 00:00) pero `data/noticias.js` se sobrescribe y lo viejo se pierde. Guardar un archivo en el repositorio (`data/noticias_archivo.json`), destacar lo más relevante para derechos humanos y mostrar la fecha de la última actualización | pendiente |
| T4 | **Cruzar el catálogo con las fuentes oficiales** y listar lo que falta (mandatos, tratados, comités, comisiones de investigación, siglas) con evidencia | pendiente |
| T5 | Mandatos y documentos extinguidos (empezar por los de la antigua Comisión de Derechos Humanos), con fuente por fila | pendiente |
| T6 | Comisiones de investigación restantes | pendiente |
| T7 | Ampliar siglas y acrónimos (hoy 145) | pendiente |
| T8 | Ampliar la historia (hoy 68 hechos; faltan descolonización por país, conferencias mundiales, hechos regionales) y contrastar con fuente primaria los de antes de 1945 | pendiente |
| T9 | Explicaciones en lenguaje claro de las resoluciones (hoy solo 20 (XXXVI)) | pendiente |
| T10 | Otros órganos de la ONU: Consejo de Seguridad, Asamblea General, ECOSOC, CIJ, agencias, ODS | pendiente |
| T11 | Mapas | pendiente |
| T12 | Confirmar la búsqueda en vivo desde el celular y, si no responde, valorar otra vía | pendiente |
| T13 | **El reto académico: catalogación cruzada.** Página pública «El reto» (¿se puede catalogar bien lo que el sistema de la ONU cataloga mal?) con el método, una lista de documentos mal catalogados que ATLAS sí encuentra (con enlace al registro y qué estaba mal: borrador por resolución, informe por resolución, símbolo distinto, etc.) y un marcador de casos resueltos y abiertos que se actualiza con la revisión. Sin nombres de personas: es un reto académico, no una apuesta con nombre (regla de privacidad) | pendiente |
| T14 | **ERROR (prioridad alta): el menú lateral del celular no baja.** En Android/Chrome el menú se corta en «Defensores · DIGNITYOS» y no se puede llegar a «Fuentes y alcance» ni al pie. Probable falta de desplazamiento vertical (`overflow-y:auto`) o de altura con `100dvh` en la barra lateral al abrirse como cajón. Hacerlo antes que T2 y probarlo en una pantalla de 360–412 px de ancho con la barra del navegador visible | pendiente |
| T15 | **Revisión de UX de todas las pantallas** (con ojo de experto, sin ser literal): que la página sea más interactiva y ayude más a quien navega, sobre todo en el celular. Punto de partida (captura de «Otros mecanismos» en Android): la tabla es más ancha que la pantalla y se corta la columna «Texto»; la columna «Acto de la ONU» queda tan estrecha que el texto se rompe palabra por palabra; se repite «Sin enlace directo verificado»; en celular conviene pasar de tabla a tarjetas. Revisar también: menús y orientación («dónde estoy»), buscador siempre a mano, filtros y orden, estados vacíos y de carga, tamaño táctil de botones, contraste, lenguaje claro y accesibilidad (teclado, lector de pantalla). Entregar primero un informe corto con lo encontrado y priorizado, y luego aplicarlo pantalla por pantalla, cada una con su commit | pendiente |
