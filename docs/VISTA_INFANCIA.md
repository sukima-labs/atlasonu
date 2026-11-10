# Vista para niños y niñas: enfoque (T33)

Informe previo, 10-11-2026. Hasta que el fundador decida lo marcado como **Decide el fundador** y una persona
experta revise los textos, **no se publica nada**: la vista se prepara en una rama y no entra en el menú.

## Para quién
- **Propuesta: de 8 a 12 años**, que ya leen solos y usan el celular de casa o de la escuela. Por debajo de 8 años
  hace falta un adulto que lea con el niño, y eso pide otro formato (audio, más imagen).
- **También para quien acompaña**: madres, padres y docentes. Una nota corta al pie: «Cómo usar esta página en clase».
- **Decide el fundador:** la franja de edad, y si después se hace una segunda para adolescentes (13–17).

## Tono
- Frases de menos de 15 palabras, una idea por frase, «tú» y nunca siglas sin explicar.
- No se infantiliza: los derechos se explican como son, sin cuentos que cambien su sentido.
- Lenguaje inclusivo sin desdoblar cada palabra («niños y niñas» en los títulos; «la infancia», «cada niño o niña»).

## Contenido (primera versión)
1. **¿Qué es un derecho?** Algo que te corresponde por ser persona, no un premio.
2. **¿Qué hace la ONU?** Un lugar donde casi todos los países del mundo se ponen de acuerdo en normas, y personas
   expertas que vigilan que se cumplan (aquí entra, muy simple, lo que hace ATLAS: relatores y comités).
3. **La Convención sobre los Derechos del Niño, artículo por artículo.** Sus 41 artículos de derechos (del 1 al 41),
   cada uno en 1–2 frases **escritas por el proyecto**, con enlace al texto oficial de la ONU
   ([Colección de Tratados de la ONU](https://treaties.un.org/Pages/ViewDetails.aspx?src=TREATY&mtdsg_no=IV-11&chapter=4&clang=_en),
   con el estado de ratificación; el texto en español está también en la web de OHCHR, que no deja comprobar sus
   enlaces de forma automática).
   Agrupados en 6 temas con dibujo propio: quién soy (nombre, identidad), mi familia, mi salud, aprender y jugar,
   protección, que me escuchen.
4. **Mi país y la Convención.** De la ficha de país, solo dos datos verificados: cuándo la ratificó y cuándo le
   revisó el Comité de los Derechos del Niño, con su fuente.
5. **Preguntas y juegos.** Un cuestionario de «¿verdadero o falso?» y «une cada derecho con su dibujo». Funciona
   sin conexión y no guarda nada fuera del propio aparato.
6. **¿Y si a mí no se me respetan?** «Habla con una persona adulta de confianza», y un enlace a la red mundial de
   líneas de ayuda a la infancia ([Child Helpline International](https://childhelplineinternational.org/helplines/)),
   que tiene el número de cada país. No se ponen números a mano: cambian y un número equivocado es peligroso.

## Temas duros sin falsear nada
- Guerra, trabajo infantil, abuso o tráfico se nombran (la Convención los nombra: arts. 19, 32, 34–38), **sin
  imágenes ni casos concretos**, en una frase neutra y siempre junto a «qué protege la ley» y «a quién pedir ayuda».
- No se muestran noticias, comunicaciones de relatores ni situaciones de países concretos: eso sigue en la versión
  normal.
- Cada texto lo revisa antes de publicarse una persona experta en infancia o en educación. **Decide el fundador:**
  quién (puede ser la misma persona revisora de T53).

## Privacidad (máxima)
- Sin cuentas, formularios, cookies, contador de visitas, búsqueda en vivo ni «Pregúntale a ATLAS» (IA) en esta
  vista: la página no se conecta a ningún servicio y funciona igual sin conexión.
- Los juegos guardan el progreso solo en el aparato (`localStorage`) y se puede borrar con un botón.

## Fuentes para menores: qué se puede usar
| Fuente | Licencia | Uso en ATLAS |
|---|---|---|
| Texto oficial de la Convención (ONU/OHCHR) | Texto de un tratado, reproducible citando la fuente | Se cita y se enlaza |
| Versión para niños de UNICEF | Sin licencia abierta: reproducirla pide permiso escrito | Solo enlace, como «para leer más» |
| Versiones adaptadas de Save the Children (6–8 y 9–11 años) y póster de Plan International | Sin licencia abierta visible; Plan avisa de que no es texto oficial | Solo enlace |
| Textos de ATLAS | Elaboración propia, CC BY 4.0 | Se escriben y se marcan «Explicado por ATLAS, no es texto oficial» |

## Interfaz
- Botones de al menos 48 px, letra de 18 px como mínimo, navegación de un solo nivel (inicio → tema → derecho).
- Ilustraciones propias en SVG, guardadas en el repositorio (`assets/infancia/`), sin fuentes ni imágenes externas.
- La prueba de accesibilidad de T27 (`tests/accesibilidad.cjs`) cubre también esta vista. Español primero; inglés
  y francés con el mismo diccionario de T26.

## Plan
1. **Decisiones del fundador** (issue en GitHub): edad, nombre de la vista, persona revisora, y si entra en el menú
   o va en una dirección propia (`…/atlasonu/#infancia`).
2. Rama con los textos de los 41 artículos y las pantallas 1–3, **sin publicar**; la persona experta revisa sobre la
   vista previa.
3. Con la revisión hecha: juegos, «Mi país» y publicación.
