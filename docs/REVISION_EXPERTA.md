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
