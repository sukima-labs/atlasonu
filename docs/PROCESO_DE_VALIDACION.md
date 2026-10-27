# Proceso de validación de solicitudes

Cuando alguien busca algo que ATLAS ONU no tiene, puede abrir una *Solicitud de verificación* (Issue público en GitHub). **Nada entra al catálogo por haber sido pedido**: solo entra lo que se contrasta con una fuente oficial.

## Pasos
1. **Registrar.** La solicitud queda como Issue, con el texto buscado y dónde se buscó. Estado: *pendiente de verificación*.
2. **Buscar en la fuente primaria.**
   - Mandatos y titulares: índice oficial de OHCHR (`spinternet.ohchr.org`).
   - Resoluciones y documentos: búsqueda por símbolo exacto en la Biblioteca Digital de la ONU (`digitallibrary.un.org`).
3. **Comprobar el documento.** Leer la primera página del PDF y confirmar que el símbolo coincide; distinguir resolución, informe y borrador; si no hay archivo propio, localizar el informe de sesión que la contiene y sus páginas.
4. **Decidir y responder en el Issue** con una de estas conclusiones:
   - *Verificado y añadido* (con el enlace a la fuente).
   - *Existe pero con reservas* (se añade con su alerta).
   - *No verificable / no existe en fuentes oficiales* (se explica por qué; no se añade).
5. **Añadir por los scripts**, no a mano: la semilla entra en `scripts/build_mecanismos.py` (o el catálogo se regenera con `scripts/actualizar_datos.sh`), que aplica las mismas reglas de verificación y deja el estado a la vista. Se ejecutan las pruebas y se publica.

## Reglas
- Una ruta sugerida no es un documento recuperado.
- Una resolución no es el informe que la reproduce.
- Si una equivalencia es inferida, se marca como inferida.
- No se publican datos personales de quien solicita.
