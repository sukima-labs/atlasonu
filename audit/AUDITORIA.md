# Auditoría frente a los 13 requisitos (v0.6, 27-oct-2026)

Estados: ✅ cumple · 🟡 parcial · ❌ no implementado.

| # | Requisito | Estado | Evidencia / brecha |
|---|---|---|---|
| 1 | Plataforma web profesional, UX estudiantes | 🟡 | Interfaz limpia, responsive sin desbordamiento (390 px y 1366 px). Falta pulido y revisión de accesibilidad |
| 2 | Búsqueda simple ES/EN + avanzada | 🟡 | Palabras, sinónimos ES/EN, figura, origen, años, orden. Faltan símbolo, región, estado y fuente como filtros |
| 3 | Catálogo exhaustivo | ❌ | Solo 28 mandatos de muestra |
| 4 | Arqueología documental activa | 🟡 | 1 caso verificado (res. 20 (XXXVI) 1980, E/1980/13, pp. 180–181) y 11 trazas. Sin recuperación automática |
| 5 | Distinguir órganos y codificaciones | 🟡 | Hay sección "Códigos ONU"; cobertura por completar |
| 6 | Resoluciones, lenguaje claro, efectos jurídicos | ❌ | Sin texto de resoluciones ni jerarquía completa |
| 7 | Sincronización con fuentes oficiales | ❌ | No hay. Opción viable: actualización programada por GitHub Actions (evita CORS) |
| 8 | Estadísticas y mapas | 🟡 | KPIs y gráfico de la muestra; sin mapas |
| 9 | Selección de titulares | 🟡 | Secuencia descrita; sin datos por proceso |
| 10 | Autoría | ✅ | © y enlace al repo visibles. Licencia pendiente del autor |
| 11 | Excel offline, HTML Pages | 🟡 | Excel y HTML existen; Pages sin activar |
| 12 | Pruebas reales | 🟡 | `smoke.cjs` 14/14; `browser.cjs` 24/24 en Chromium, sin errores de consola. Sin pruebas de enlaces externos ni de accesibilidad |
| 13 | Commits y Pages verificado | 🟡 | Commits hechos; Pages y URL pública pendientes (requiere activarlo en Settings) |

## Reglas de rigor mantenidas
Una ruta sugerida no es un documento recuperado. Resolución ≠ informe que la reproduce. No se afirma cobertura mayor que la muestra.

## Prioridades siguientes
1. Activar GitHub Pages y verificar la URL pública.
2. Pasar los datos a JSON/CSV fuera del HTML y ampliar el catálogo por lotes con fuente verificable por fila.
3. Cargar resoluciones constitutivas (E/CN.4, A/HRC/RES) con cotejo contra docs.un.org / Biblioteca Digital.
4. Filtros por símbolo, región, estado; auditoría de enlaces externos.
5. Mapas con fuente precisa; sincronización programada; decisión de licencia.
