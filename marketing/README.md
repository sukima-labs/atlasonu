# Módulo de marketing y promoción de ATLAS ONU

Todo lo que hace falta para que ATLAS ONU llegue a quien lo necesita: análisis, plan, mensajes, ficha de cada canal, kit de prensa, borradores listos para publicar y medición. Está en el repositorio (público) para que cualquiera pueda ver cómo se promociona y reutilizar el método. Contenido propio bajo CC BY 4.0.

| Pieza | Qué es |
|---|---|
| [`ANALISIS.md`](ANALISIS.md) | Evaluación del proyecto: qué es, para quién, qué lo diferencia, competencia, DAFO y **línea base** de medición |
| [`PLAN.md`](PLAN.md) | Proyecto de promoción por fases, con objetivos, calendario, qué se hace con qué herramienta y qué necesita permiso |
| [`MENSAJES.md`](MENSAJES.md) | Propuesta de valor, mensajes por público, tono y lo que NO se dice |
| [`CANALES.md`](CANALES.md) | Ficha por canal: a quién llega, reglas, qué publicar, estado |
| [`kit_prensa/`](kit_prensa/) | Descripciones corta y larga, cifras actuales (se generan) y enlaces |
| [`contenidos/`](contenidos/) | Borradores listos para publicar (aún sin publicar mientras no figure en el registro) |
| [`metricas/`](metricas/) | Script de medición y la serie semanal (`registro.csv`) |
| [`REGISTRO.md`](REGISTRO.md) | Bitácora: qué se hizo, dónde, cuándo, con enlace y resultado |

## Reglas que no se rompen
1. **Gratis (0 €), abierto y privado**, como el resto del proyecto. Nada de anuncios de pago, listas de correo compradas, rastreadores ni píxeles. Medimos con lo que ya hay y con lo que GitHub da (ver `metricas/`).
2. **Autoría pública: solo «Sukima-Labs».** Ninguna cuenta, firma, nota de prensa ni borrador lleva el nombre de una persona. Las cuentas desde las que se publica son del proyecto, no personales.
3. **Nada de engaño.** Sin cuentas falsas, sin reseñas ni votos pedidos a amigos, sin hacerse pasar por usuarios, sin mensajes masivos. Cada comunidad tiene sus reglas de autopromoción y se leen antes de publicar (están resumidas en `CANALES.md`).
4. **Es una iniciativa independiente, no oficial.** Nunca se sugiere vínculo con la ONU ni con ninguna universidad. El aviso del README va en toda pieza que lo necesite.
5. **Solo se afirma lo que se puede comprobar.** Las cifras salen de `data/` con `marketing/cifras.py`; no se escriben a mano en los textos publicados. Si un número no se ha comprobado, no se publica.
6. **Publicar es un acto externo y no se deshace** (queda en cachés y buscadores). Un borrador pasa a publicado solo cuando la cuenta de Sukima-Labs y la pieza están aprobadas por quien lleva el proyecto, y se anota en `REGISTRO.md`.
7. **El producto sigue siendo de su fundador.** El marketing cuenta lo que ATLAS es; no cambia su rumbo. Lo que el análisis propone cambiar en el producto (p. ej. la imagen para compartir enlaces) va por tarea de la cola y PR, como cualquier cambio.

## Cómo se usa
```
python3 -I marketing/cifras.py              # regenera kit_prensa/CIFRAS.md desde data/
python3 -I marketing/metricas/medir.py      # añade una fila a metricas/registro.csv (necesita `gh` con sesión)
python3 -I marketing/metricas/medir.py --visitas-url http://127.0.0.1:8787/visitas   # con el contador de la web
```
Cada semana (lunes, con el flujo «Celular»): medir, anotar en `REGISTRO.md` lo publicado y lo aprendido, y ajustar `PLAN.md`.
