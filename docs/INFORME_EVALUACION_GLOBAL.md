# Evaluación global de ATLAS ONU (T23, 28-10-2026)

Auditoría con las cifras reales del repositorio (catálogo, datos, `index.html`, pruebas). Las pruebas pasan: 132 de lógica y 12 invariantes. No se inventa nada: cada hueco indica su evidencia y la tarea que lo cubre.

## Qué hay hoy
57 mandatos (421 actos, 401 localizados) · 33 mecanismos conexos · 196 fichas de país · 18 tratados (texto literal de 8) · 241 siglas · 116 hechos de historia (los anteriores a 1945 aún sin contrastar con fuente primaria) · 41 entidades del sistema · 862 entradas en el índice de actos · 79 alertas de verificación.

## Huecos por área (más grave primero)

| # | Hueco | Evidencia | Tarea |
|---|---|---|---|
| 1 | **Comunicaciones de los relatores**: solo cifras por país; el texto de cada una y su respuesta no se pueden traer | `robots.txt` de `spcommreports.ohchr.org` y `tbinternet.ohchr.org` dice `Disallow: /`; solo 10 de 35 informes conjuntos A/HRC pasan la validación | T22 (resto) |
| 2 | **Accesibilidad sin auditar**: sin enlace «saltar al contenido», solo 5 reglas `:focus`, 7 `aria-live`, ninguna prueba con lector de pantalla ni contraste medido | `grep` sobre `index.html` (0 «skip»; 5 `:focus`; 1 `alt=`) | T27 + T34 |
| 3 | **Mandatos extinguidos y comisiones de investigación**: el catálogo solo tiene lo vigente | `audit/AUDITORIA.md` requisito 3 (🟡) | T5, T6 |
| 4 | **Cómo funciona la ONU incompleto**: 41 entidades y 6 pasos del ciclo; faltan votación, presupuesto, elección de miembros, reformas, Consejo de Seguridad y derechos humanos | `data/sistema_onu.json` | T21, T10 |
| 5 | **Resoluciones sin explicar en lenguaje claro** (solo 20 (XXXVI)) | `audit/AUDITORIA.md` requisito 6 (❌) | T9 |
| 6 | **Documentos básicos comunes (HRI/CORE) y jurisprudencia** (observaciones generales, dictámenes) sin indexar | `CONTEXTO_PARA_NUEVAS_SESIONES.md`, pendiente 1 | T20, T35 |
| 7 | **EPU**: se cuenta el número de documentos por país, pero no las recomendaciones (aceptadas / «tomó nota») | campo `docs.epu` de cada país es un número | T36 |
| 8 | **Sin mapas** (ni de calor) | requisito 8 de la auditoría | T11, T24 |
| 9 | **Idiomas**: solo español; datos oficiales en inglés | `<html lang="es">`, sin selector | T26, T27 |
| 10 | **Buscador**: faltan filtros por región y por fuente | requisito 2 de la auditoría | T15 |
| 11 | **Siglas (241) e historia (116)** cortas frente a lo que cubre la ONU | `data/siglas.json`, `data/historia.json` | T7, T8 |
| 12 | **Búsqueda en vivo sin confirmar desde un celular real**; varias correcciones de menú (T14, T17, T19, T28) también esperan confirmación en celular real | cola de tareas | T12 |
| 13 | **Registro de revisiones casi vacío**: `data/revisiones.json` tiene 1 entrada (la inicial); la primera ejecución real tras T2 aún no aparece | `data/revisiones.json` | vigilar (T34) |

## Calidad y frescura de los datos
Buena: las salvaguardas abortan si falla la red, las cifras de comunicaciones se validan contra el total de cada informe y se descarta lo que no cuadra. Riesgos: la verificación de símbolos y `fetch_docs_pais.py` usan `/search` de la Biblioteca Digital, que su `robots.txt` desaconseja (T22 punto 5); el limitador de ritmo puede degradar la verificación.

## Comparación con las fuentes oficiales
ATLAS cruza OHCHR, Biblioteca Digital y Colección de Tratados. Lo que las fuentes ofrecen y ATLAS aún no refleja: texto de las comunicaciones, recomendaciones del EPU, jurisprudencia de los comités, documentos básicos comunes, mandatos históricos. Contrastar el catálogo completo con las fuentes sigue en T4.

## Orden propuesto
Lo ya previsto en las oleadas se mantiene; se añade: **T34** (accesibilidad básica de salto, foco y lector de pantalla, antes de T27), **T35** (jurisprudencia de los comités), **T36** (recomendaciones del EPU). Las tres entran en la oleada 2.
