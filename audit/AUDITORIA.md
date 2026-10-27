# Auditoría frente a los 13 requisitos (v0.7, 27-oct-2026)

Estados: ✅ cumple · 🟡 parcial · ❌ no implementado.

| # | Requisito | Estado | Evidencia / brecha |
|---|---|---|---|
| 1 | Plataforma web profesional, UX | 🟡 | Interfaz responsive sin desbordamiento (390 y 1366 px), 32 comprobaciones en Chromium. Falta revisión de accesibilidad y búsqueda guiada para novatos |
| 2 | Búsqueda simple ES/EN + avanzada | 🟡 | Palabras (ES/EN), símbolos, figura, modalidad, origen, años. Faltan filtros por región, estado y fuente |
| 3 | Catálogo exhaustivo | 🟡 | **57 mandatos vigentes completos** (índice OHCHR). Faltan mandatos extinguidos, órganos de tratados, comisiones de investigación |
| 4 | Arqueología documental activa | 🟡 | 421 actos contrastados; borrador→resolución; corrección de símbolos; PDF ES/EN. Un caso con texto leído (1980). Falta leer el texto de los demás actos |
| 5 | Distinguir órganos y codificaciones | 🟡 | Cada acto lleva órgano, tipo y aviso (resolución / informe / borrador). Tabla «Códigos ONU» existente |
| 6 | Resoluciones, lenguaje claro, efectos jurídicos | ❌ | Sin texto explicado de las resoluciones |
| 7 | Sincronización con fuentes oficiales | 🟡 | `actualizar_datos.sh` + flujo mensual que abre un PR. El navegador no consulta la ONU en vivo (CORS) |
| 8 | Estadísticas y mapas | 🟡 | KPIs y gráfico por tipo de figura; sin mapas |
| 9 | Selección de titulares | 🟡 | Secuencia del proceso; titulares actuales por mandato; sin datos históricos por proceso |
| 10 | Autoría | ✅ | © y enlace visibles; licencia pendiente del autor |
| 11 | Excel offline, HTML Pages | 🟡 | HTML funciona sin conexión; Excel es del piloto y no incluye el catálogo nuevo |
| 12 | Pruebas reales | 🟡 | 26 de lógica + 32 en Chromium. Sin auditoría automática de enlaces externos ni de accesibilidad |
| 13 | Commits y Pages verificado | 🟡 | Commits publicados; Pages no activado, sin URL pública verificada |

## Qué corrigió esta versión respecto a v0.6
Ver `DISCREPANCIAS_V06.md`: 16 de los 28 mandatos de v0.6 tenían datos desactualizados o erróneos (prórrogas, símbolos de creación). Además:
- La última «alerta» de v0.6 era una fila de metadatos mostrada como alerta vacía y contada.
- El motor de recuperación solo funcionaba para el caso de 1980; ahora usa un índice verificado.
- La verificación automática tenía falsos positivos (búsqueda aproximada, informes tomados por resoluciones); se corrigieron y se documentan en `scripts/verify_symbols.py`.

## Resultados de verificación (421 actos)
338 localizados exactos · 63 localizados con símbolo corregido (33 son borradores que remiten a la resolución adoptada) · 7 con título a cotejar · 1 es un informe, no resolución · 3 solo borrador · 4 sin registro · 5 sin símbolo en la fuente. Detalle por acto en las alertas de la plataforma.

## Prioridades siguientes
1. Activar GitHub Pages y verificar la URL pública.
2. Leer el texto de las resoluciones constitutivas (como se hizo con 20 (XXXVI)) y redactar su explicación en lenguaje claro.
3. Añadir mandatos históricos/extinguidos y órganos de tratados con fuente por fila.
4. Mapas; accesibilidad; auditoría de enlaces; licencia.
