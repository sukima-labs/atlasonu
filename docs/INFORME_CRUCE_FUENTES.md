# Cruce del catálogo con las fuentes oficiales (T4, 28-10-2026)

Se repite con `python3 -I scripts/cruzar_fuentes.py` (sale con error si aparece una diferencia).

## Lo que cuadra (comprobado contra las listas descargadas)
| Área | Fuente | En la fuente | En ATLAS |
|---|---|---|---|
| Mandatos temáticos | OHCHR (`ohchr_CM_es.json`) | 13 | 13 |
| Mandatos de país | OHCHR (`ohchr_TM_es.json`) | 44 | 44 |
| Países | base de OHCHR (`paises_ohchr.json`, sin la fila «Otros») | 196 | 196 |
| Tratados de derechos humanos | Colección de Tratados (`tratados_untc.json`) | 18 | 18 |
| Órganos de tratados | los 9 comités + el Subcomité para la Prevención de la Tortura | 10 | 10 (en «mecanismos») |

## Lo que falta (candidatos, **sin verificar**: no son datos del catálogo)
Salen de lo que ya sabe el proyecto, no de una fuente consultada hoy (OHCHR devuelve 403 a clientes automáticos). Cada uno necesita símbolo de la resolución creadora y enlace oficial antes de entrar.

| Tipo | Candidato | Tarea |
|---|---|---|
| Comisiones y misiones de investigación | las ya concluidas o de otras situaciones (hoy hay 6 COI y 2 misiones) | T6 |
| Mandatos extinguidos | los de la antigua Comisión de Derechos Humanos y los que el Consejo cerró | T5 |
| Mecanismos de investigación | mecanismos independientes de investigación (Siria, Myanmar) | T6 |
| Foros | foros anuales del Consejo (minorías ya está; faltan los otros) | T38 |
| Siglas | 241 (eran 145) frente a las que usan los documentos | T7 |

## Qué no se pudo cruzar
- **Siglas, historia y sistema de la ONU** son contenido propio: no hay lista oficial única con la que compararlas.
- **Documentos por país** (`docs`): la Biblioteca Digital limita `/search` en su `robots.txt`; ya se declaró en T22 punto 5.

## Conclusión
El núcleo vigente está completo y coincide con las fuentes. Los huecos reales son lo extinguido y las comisiones de investigación (T5, T6) y las siglas (T7).
