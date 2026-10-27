# ENTREGA INTEGRAL PARA CLAUDE — ATLAS ONU

Fecha: 27 de octubre de 2026.
Autor y titular del proyecto: Jeisson Arley Osorio Mesa.
Repositorio objetivo (ya creado y público): https://github.com/cataplum1414/onu-arqueologia-documental

## Qué incluye
- La versión HTML más reciente: 01_PROYECTO_Y_VERSIONES/ATLAS_ONU_publicacion/index.html
- Los archivos de datos, README, test y catálogo XLSX en ATLAS_ONU_publicacion/
- Versiones históricas ZIP, HTML y XLSX para recuperar cualquier trabajo previo.
- Scripts fuente de construcción/corrección y pruebas.
- Programa ONU 2026 y material de contexto académico separado.
- MANIFIESTO_SHA256.tsv para verificar integridad.

## Requisitos solicitados por el autor (NO confundir con funciones ya implementadas)
1. Plataforma real de consulta de los procedimientos especiales ONU accesible desde cualquier navegador, con interfaz profesional y UX para estudiantes y docentes.
2. Búsqueda sencilla por lenguaje natural y palabras comunes, con sinónimos ES/EN; búsqueda avanzada por fecha, tema, mandato, órgano, tipo, símbolo, región, estado y fuente.
3. Catálogo exhaustivo (no muestra) de relatores especiales, expertos independientes, grupos de trabajo; mandatos temáticos y por país, creación, renovación, cambios y cese, titulares, facultades y métodos.
4. Arqueología documental activa: desde una referencia o vínculo roto seguir el acto jurídico original, símbolo y órgano emisor, informe que reproduce la resolución, página exacta, variantes lingüísticas, repositorios oficiales y estado verificable. NO convertir rutas sugeridas en documentos recuperados sin corroboración.
5. Distinguir ECOSOC, antigua Comisión DDHH, Asamblea General, Consejo de DDHH, Consejo de Seguridad y codificaciones oficiales (E/CN.4, E/RES, A/RES, A/HRC/RES, A/HRC, S/RES...), resoluciones, informes, propuestas y decisiones.
6. Incluir resoluciones originales, su contenido explicado en lenguaje claro, naturaleza jurídica y efectos vinculantes o no según órgano y competencia. Jerarquía resolución -> mandato -> revisiones -> métodos -> informes/visitas/comunicaciones.
7. Sincronización con fuentes oficiales de ONU al abrir/reconectar, o recarga programada compatible con seguridad de navegadores; caché y marcas de fecha; ruta de actualización alternativa si no hay API/CORS o permiso.
8. Estadísticas, mapas geográficos con fuentes precisas, gráficos, comparaciones, cobertura, calidad y advertencias sobre denominadores y fechas.
9. Selección de relatores y expertos, cinco miembros grupo consultivo, preselección, entrevistas, recomendación, Presidencia y nombramiento.
10. Protección de la edición/autoria (mostrar © Jeisson Arley Osorio Mesa, repositorio público y licencia elegida por autor; publicar código no implica cesión de derechos).
11. Excel descargable y utilizable sin conexión, posible Power BI si aporta valor; HTML/Páginas GitHub para acceso desde PC y móvil.
12. Probar navegador real, accesibilidad básica, enlaces oficiales, búsqueda, fallos, carga, integridad de datos, y tests reproducibles. No declarar 99/100% sin evidencias.
13. Crear commits incrementales y publicar en repositorio, habilitar GitHub Pages, verificar URL pública real. No incorporar datos personales ni material de DignityOS.

## Estado REAL al momento de traspaso
- Hay prototipo HTML local y catálogo parcial (28 mandatos y 11 trazas en la versión 0.6) con búsquedas y recuperación guiada, NO arqueología automatizada general.
- No hay sincronización automática con la ONU, geodatos completos, catálogo exhaustivo ni auditoría jurídica completa.
- Algunas pruebas estáticas pasaron; prueba completa de navegación Chromium no quedó acreditada.
- Cuenta GitHub: cataplum1414; repo público existente. La integración de ChatGPT dio 403 `Resource not accessible by integration` al escribir y `list_installations` devolvió instalaciones vacías. NO se confirmó commit ni GitHub Pages.
- Claude deberá comprobar el repositorio actual antes de modificar, y realizar acciones solo con permiso y autenticación disponible.

## Guía para Claude
Lee primero el código en ATLAS_ONU_publicacion/index.html, README y tests/RESULTADOS.md. Audita frente a los 13 requisitos y plantea prioridades. Aplica las correcciones, ejecuta pruebas reales y documenta fallos. Busca documentos oficiales originales para referencias ambiguas, siempre diferenciando resolución de informe que la contiene. Publica con commits Git, comprueba URL pública y deja constancia de lo que no cumple. Mantén el proyecto gratuito, abierto a consulta y con control del código en manos del autor. Evita nuevas suscripciones.
