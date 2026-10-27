# Auditoría frente a los 13 requisitos (v0.7, 27-oct-2026, actualizada)

Estados: ✅ cumple · 🟡 parcial · ❌ no implementado.

| # | Requisito | Estado | Evidencia / brecha |
|---|---|---|---|
| 1 | Plataforma web profesional, UX | 🟡 | Responsive sin desbordamiento (390 y 1366 px), búsqueda guiada para novatos, 36 comprobaciones en Chromium. Falta revisión de accesibilidad con lector de pantalla |
| 2 | Búsqueda simple ES/EN + avanzada | 🟡 | Palabras (ES/EN), símbolos, alternativas, figura, modalidad, origen, años, verificación. Faltan filtros por región y fuente |
| 3 | Catálogo exhaustivo | 🟡 | 57 mandatos vigentes completos + 25 mecanismos conexos (10 órganos de tratados, EPU, 1235/1503, EMRIP, Foro Minorías, ACNUDH, 8 comisiones/misiones). Faltan mandatos extinguidos y el resto de comisiones de investigación |
| 4 | Arqueología documental activa | ✅/🟡 | Resolución localizada aunque el símbolo esté mal escrito; borrador→resolución; 374 PDF propios validados y 26 resoluciones antiguas ubicadas en su informe de sesión con páginas. Falta leer el texto de todas (solo 20 (XXXVI) leída) |
| 5 | Distinguir órganos y codificaciones | 🟡 | Cada acto lleva órgano, tipo y aviso (resolución / informe / borrador). Tabla «Códigos ONU» existente |
| 6 | Resoluciones, lenguaje claro, efectos jurídicos | ❌ | Sin texto explicado de las resoluciones |
| 7 | Sincronización con fuentes oficiales | 🟡 | `actualizar_datos.sh` + flujo mensual que abre un PR. El navegador no consulta la ONU en vivo (CORS); la ruta alternativa es el flujo programado |
| 8 | Estadísticas y mapas | 🟡 | KPIs y gráfico por tipo de figura; sin mapas |
| 9 | Selección de titulares | 🟡 | Secuencia del proceso; titulares actuales por mandato; sin datos históricos por proceso |
| 10 | Autoría | ✅ | © y enlace visibles; licencia pendiente del autor |
| 11 | Excel offline, HTML Pages | 🟡 | HTML sin conexión y Excel v0.7 (6 hojas); flujo `pages.yml` listo; pendiente activar Pages (un clic) |
| 12 | Pruebas reales | 🟡 | 33 de lógica + 36 en Chromium; auditoría de enlaces (571; 0 rotos; 459 no concluyentes por antirrobot); muestreo de PDF 30/30. Sin auditoría de accesibilidad |
| 13 | Commits y Pages verificado | 🟡 | Commits publicados; URL pública por verificar tras fusionar en `main` y activar Pages |

## Qué corrigió esta versión respecto a v0.6
Ver `DISCREPANCIAS_V06.md`: 16 de los 28 mandatos de v0.6 tenían datos desactualizados o erróneos (prórrogas, símbolos de creación). Además:
- La última «alerta» de v0.6 era una fila de metadatos mostrada como alerta vacía y contada.
- El motor de recuperación solo funcionaba para el caso de 1980; ahora usa un índice verificado.
- La verificación automática tenía falsos positivos (búsqueda aproximada, informes tomados por resoluciones); se corrigieron y se documentan en `scripts/verify_symbols.py`.

## Resultados de verificación (421 actos)
338 localizados exactos · 63 localizados con símbolo corregido (33 son borradores que remiten a la resolución adoptada) · 7 con título a cotejar · 1 es un informe, no resolución · 3 solo borrador · 4 sin registro · 5 sin símbolo en la fuente. Detalle por acto en las alertas de la plataforma.

## Documentos de apoyo
`DISCREPANCIAS_V06.md` · `ENLACES.md` · `muestreo_pdfs_registro.json` · `INVENTARIO.md`

## Prioridades siguientes
1. Verificar la URL pública tras activar Pages.
2. Redactar la explicación en lenguaje claro de las resoluciones constitutivas, leyendo cada texto (se hizo con 20 (XXXVI)).
3. Mandatos extinguidos y comisiones de investigación restantes, con fuente por fila.
4. Mapas; accesibilidad; decisión de licencia.
