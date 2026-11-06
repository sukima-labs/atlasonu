# Copias de seguridad y recuperación (T45)

## Qué se copia y dónde
Cada domingo a las 03:00 (`atlas-respaldo.timer`, también al encender si estaba apagado) el mini PC crea `~/atlas-onu-respaldos/atlas-onu-AAAA-MM-DD.tar.age` y conserva las últimas 8. Contiene, **cifrado con `age`**:
- `repositorio.bundle`: todo el repositorio con todas las ramas (`git clone repositorio.bundle`).
- `extra/visitas/`: el contador de visitas (`~/.local/share/atlas-onu`).
- `extra/atlas-epu-privado/`: la copia privada de «Prepara tu EPU».

El cifrado usa una clave **pública** (`~/.config/atlas-onu/respaldo-publica.txt`). Sin la clave **privada** nadie abre la copia.

## Lo que hay que hacer una vez (sin esto la copia no protege del todo)
1. **Guardar la clave privada fuera del mini PC** (gestor de contraseñas o tu otro equipo): `~/.config/atlas-onu/respaldo-privada.txt`. Hoy está también en el mini PC para poder probar la restauración; cuando la tengas a salvo, bórrala de allí. Si la pierdes y se pierde el disco, las copias no se pueden abrir.
2. **Llevar las copias a otro dispositivo** (el disco del mini PC no cuenta como copia aparte): copia `~/atlas-onu-respaldos/` a un USB o a tu otro equipo de vez en cuando (por ejemplo con `scp` por Tailscale). Los archivos ya van cifrados, así que pueden viajar sin riesgo.

## Restaurar
```bash
age -d -i respaldo-privada.txt atlas-onu-AAAA-MM-DD.tar.age | tar -x     # saca repositorio.bundle y extra/
git clone repositorio.bundle ~/Documentos/atlas-onu
mkdir -p ~/.local/share/atlas-onu && cp -a extra/visitas/. ~/.local/share/atlas-onu/
cp -a extra/atlas-epu-privado ~/atlas-epu-privado
```
Después, apunta el clon al remoto (`git remote set-url origin https://github.com/sukima-labs/onu-arqueologia-documental.git`) y reinstala servicios y temporizadores: `bash scripts/mini_pc/instalar.sh` y `sudo loginctl enable-linger "$USER"` (detalles en `docs/MINI_PC.md`; el token de GitHub se crea de nuevo, no se copia).

## Funnel (búsqueda y contador desde fuera)
Desde el 06-11-2026 la búsqueda y el contador corren en `sk-atlas` (servicio `atlas-busqueda`, `127.0.0.1:8787`), publicados con Funnel en `https://sk-atlas.pig-mimosa.ts.net` (puerto 443). Solo lo cambian los socios: `tailscale funnel --bg http://127.0.0.1:8787` para activarlo y `tailscale funnel --https=443 off` para apagarlo. Se decide en T44 si sigue expuesto.

## Probar que la copia sirve
`age -d -i respaldo-privada.txt <archivo> | tar -tf -` debe listar `repositorio.bundle` y `extra/`. Hecho el 31-10-2026.

## Aviso
El 31-10-2026 la revisión de las 12:00 falló por «Could not resolve host: github.com» (red caída); la de las 00:00 y el respaldo de GitHub Actions la cubren. Si se repite varios días, mira `~/atlas-onu-logs/`.
