# `sk-atlas`: ficha técnica del servicio de búsqueda y visitas

Complemento de `docs/PARA_PATRICIO.md`. Describe lo que hace el código; lo que depende del servidor (unidad systemd, usuario, rutas del contenedor) lo decides tú y conviene anotarlo en la documentación del servidor, no aquí.

## Qué hace el servicio
Código: `scripts/mini_pc/busqueda_servicio.py` (biblioteca estándar, sin dependencias). Servicio en `sk-atlas`: `atlas-busqueda`.

| Ruta | Método | Qué hace |
|---|---|---|
| `/salud` | GET | Comprobación de estado |
| `/buscar?q=<texto>[&ln=es\|en]` | GET | Consulta la Biblioteca Digital de la ONU y devuelve JSON con símbolo, título, fecha y enlaces a archivos |
| `/visitas?pais=XX` | GET | Lee el contador (total y del país) |
| `/visita?pais=XX` | GET | Suma una visita, **solo** si la cabecera `Origin` es `https://sukima-labs.github.io` |

## Variables de entorno
| Variable | Por defecto | Uso |
|---|---|---|
| `ATLAS_BUSQUEDA_PUERTO` | `8787` | Puerto local |
| `ATLAS_VISITAS_ARCHIVO` | `~/.local/share/atlas-onu/visitas.json` | Archivo del contador (en `sk-atlas`: `/var/lib/atlas/visitas.json`) |

## Límites incorporados (no hace falta replicarlos en el proxy)
- Escucha solo en `127.0.0.1`: sin Funnel o proxy, nadie de fuera llega.
- CORS: solo se acepta el origen `https://sukima-labs.github.io`.
- Hasta 20 consultas nuevas a la ONU por minuto (todas las visitas juntas); caché en memoria de 1 h y 500 entradas.
- Hasta 120 visitas sumadas por minuto en total.
- Escritura del contador atómica (archivo temporal y reemplazo).

## Exposición
Tailscale Funnel: `https://sk-atlas.pig-mimosa.ts.net` (443) → `http://127.0.0.1:8787`.
- Activar: `tailscale funnel --bg http://127.0.0.1:8787`
- Apagar: `tailscale funnel --https=443 off`

Si se apaga, la web sigue funcionando: la búsqueda en vivo y el contador dejan de responder y la página lo tolera (el catálogo propio sigue buscando).

## Privacidad: qué comprobar en el servidor
El código no guarda IP, cookies ni búsquedas. Comprueba que lo de alrededor tampoco: registros del proxy o del contenedor, y del propio Funnel. El contador debe contener solo `{"total": N, "paises": {"ES": M, ...}}`.

## Actualizar el servicio tras un cambio en `main`
1. Mira en GitHub qué cambió en `scripts/mini_pc/busqueda_servicio.py` (historial o PR).
2. Trae la versión de `main` al contenedor.
3. Reinicia `atlas-busqueda` y comprueba `/salud` y una búsqueda de prueba.
4. Si algo falla, vuelve a la versión anterior y abre un issue `infra`.

## Cuando algo no va
| Síntoma | Qué mirar |
|---|---|
| La web no cuenta visitas | `/visitas?pais=ES` responde; el Funnel está activo; el archivo del contador es escribible |
| La búsqueda en vivo no da resultados | `/salud`; los registros del servicio; si la ONU limita el ritmo, esperar (el servicio no reintenta a la fuerza) |
| Se perdió el contador | Restaurar `sk-atlas` desde la copia de las 02:00 (`docs/RECUPERACION.md`) |
| Falla la revisión diaria de datos | Pestaña Actions de GitHub; no es del servidor |

## Cómo pedir o avisar de algo
Issue en GitHub con la etiqueta `infra`: qué hace falta y por qué. El fundador te avisa.
