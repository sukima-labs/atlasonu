# Revisión por personas expertas y calidad de datos

Proceso para que las traducciones (T26), el contenido infantil (T33), el lenguaje claro (T9) y la exactitud de los datos tengan una revisión registrada. Versión del 31-10-2026.

## Quién revisa (pendiente de decisión del fundador)
Hace falta al menos una persona revisora con formación en derechos humanos o en el idioma del texto, distinta del autor. Se anota aquí su rol, nunca datos personales de contacto. Hasta que el fundador lo decida, la revisión la hace el autor y se marca como «sin revisión externa».

## Cómo se registra
Cada cambio de contenido sensible (traducción, texto infantil, explicación en lenguaje claro) se hace en una PR y la descripción incluye:
- qué revisó la persona y con qué fuente;
- qué cambió tras la revisión;
- la fecha.

Sin esa línea la PR no se fusiona.

## Muestreo periódico de exactitud (mensual)
1. Elegir 20 actos al azar de `data/catalogo.json` (semilla con el mes, p. ej. `2026-11`, para poder repetirlo).
2. Para cada acto, comprobar que el símbolo, el título y la fecha coinciden con el registro de la Biblioteca Digital.
3. Anotar cada error: acto, campo, valor en la plataforma, valor en la fuente, y la fecha de corrección.
4. Los enlaces «no concluyentes» (antirrobot) se revisan a mano y se anota el resultado.

## Límites
- El muestreo no sustituye la auditoría de enlaces semanal (`enlaces.yml`).
- Si `documents.un.org` no devuelve el PDF, el acto queda «sin verificar» y no se corrige por inferencia.

## Revisión externa del asistente «Tengo un caso» (T76) y las guías (T77)
Decisión de Jeisson (11-11-2026, #205): las tres partes del plan quedan completas. El nombre sigue siendo «Tengo un caso: ¿adónde acudo?»; se empieza por la tabla verificada contra fuentes oficiales y el asistente va encima; y **la revisión por una persona u organización entra en el plan**. Como no se nombró ninguna, esta es la propuesta de cómo buscarla. **No se ha contactado a nadie**: escribir a una organización es un acto externo y lo aprueba Patricio.

**Qué se le pide (poco y acotado).** Que lea la tabla de vías (requisitos, plazos, diferencias de acceso entre comités, tiempos) y el flujo de preguntas con tres casos de ejemplo, y diga qué está mal o es engañoso. No firma el producto ni se responsabiliza de él, no recibe casos y no se publica su nombre sin su permiso.

**Quién podría hacerlo** (de más a menos probable que acepte, todas por comprobar):
1. Clínicas jurídicas de derechos humanos de universidades (docentes y estudiantes supervisados): suelen aceptar revisiones acotadas y trabajan en español.
2. ONG que ya orientan a víctimas ante la ONU o el sistema interamericano (p. ej. CEJIL, Dejusticia, IDHC) y ONG que acompañan a ONG pequeñas ante los mecanismos (p. ej. ISHR). Los nombres son puntos de partida, no contactos hechos ni acuerdos.
3. Personas expertas a título individual: antiguos miembros de comités o de la secretaría de un órgano de tratados, o profesoras de derecho internacional de los derechos humanos.

**Cómo buscarla.** (a) Redactar una carta corta en español con el alcance de arriba y un enlace a la versión «en pruebas»; (b) Patricio la envía o la aprueba, desde la cuenta del proyecto; (c) se prueba con 3 a 5 destinatarios, de distintos tipos, porque la mayoría no contesta; (d) cada contacto y su respuesta se anotan en `marketing/REGISTRO.md` sin datos personales de contacto; (e) si Jeisson o Patricio conocen a alguien, se pone primero.

**Mientras no haya revisión: «en pruebas».** El asistente y la tabla salen con una franja visible «En pruebas: aún sin revisión externa; verifica en el sitio oficial» (en los seis idiomas, y también en el resumen imprimible). Los dos avisos de siempre siguen: no es asesoría legal y no se guarda el caso. Con la franja puesta se puede publicar la fase 1; la franja solo se quita cuando la persona u organización revisora lo confirma por escrito y el PR lo registra con la línea de la sección «Cómo se registra». El **borrador de queja** (fase 4, opcional) no sale sin esa revisión. Si pasados tres meses desde la primera carta nadie ha contestado, se vuelve a preguntar a Jeisson y a Patricio; la franja se queda.
