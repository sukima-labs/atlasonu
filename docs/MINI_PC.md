# Revisión automática desde un mini PC (opcional)

## ¿Hace falta?

**No es imprescindible.** La página es estática y ya se actualiza sola: un flujo gratuito de GitHub Actions revisa las fuentes oficiales **a mediodía y a medianoche (hora de España)**, valida los datos y publica solo si todo está bien. No hay servidor que mantener.

El mini PC sirve como **respaldo**: si GitHub se retrasa o la Biblioteca Digital de la ONU limita las consultas desde los servidores de GitHub, el mini PC (que sale por tu conexión doméstica) repite la revisión 23 minutos después. Si ya la hizo GitHub, el mini PC ve que no hay nada nuevo y no publica.

> Un «backend» propio (un servidor con API) no aporta nada aquí y añadiría riesgos de seguridad: lo que hace falta es una **tarea programada**, que es lo que se instala.

## Requisitos

- Mini PC con Linux (Debian/Ubuntu o similar) con `systemd`, encendido y con internet a las 12:40 y 00:40. Desactiva la suspensión.
- Hora correcta: `timedatectl` debe mostrar tu zona (por ejemplo `Europe/Madrid`).
- Programas: `git python3 nodejs poppler-utils util-linux` y `openpyxl` de Python.

```bash
sudo apt install -y git python3 python3-openpyxl nodejs poppler-utils util-linux
```

## Pasos

1. **Crea un token de GitHub solo para este repositorio** (GitHub → Settings → Developer settings → Fine-grained tokens → *Generate new token*): repositorio `cataplum1414/onu-arqueologia-documental`, permiso **Contents: Read and write**, caducidad de 90 días. Cópialo; no lo compartas ni lo subas al repositorio.
2. **Clona en una carpeta dedicada** (no edites nada ahí a mano, porque cada revisión la deja idéntica a lo publicado):
   ```bash
   git clone https://TU_USUARIO:TU_TOKEN@github.com/cataplum1414/onu-arqueologia-documental.git ~/atlas-onu
   ```
3. **Instala el temporizador:**
   ```bash
   cd ~/atlas-onu && bash scripts/mini_pc/instalar.sh
   sudo loginctl enable-linger "$USER"     # para que corra aunque no haya sesión abierta
   ```
4. **Prueba ahora mismo** (tarda unos 8–10 minutos):
   ```bash
   systemctl --user start atlas-onu.service
   journalctl --user -u atlas-onu.service -f
   ```
5. **Comprueba el calendario:** `systemctl --user list-timers atlas-onu.timer`.

## Cómo saber si funciona

- Registros: `~/atlas-onu-logs/revision-AAAA-MM-DD.log`.
- En GitHub, los commits del mini PC aparecen como «Actualización automática (mini PC)» o «Revisión de fuentes (mini PC): sin cambios».
- Si algo falla o los datos se degradan, **no se publica nada** (las mismas salvaguardas que en GitHub: `scripts/validar_datos.py` y las pruebas de invariantes).

## Seguridad

- El token solo debe poder escribir en este repositorio y caducar. Si el mini PC se pierde, revócalo en GitHub.
- No guardes el token en el repositorio ni en capturas.
- Para desinstalar: `systemctl --user disable --now atlas-onu.timer` y borra `~/.config/systemd/user/atlas-onu.*`.

## Alternativa: «runner» propio de GitHub

También puedes registrar el mini PC como *self-hosted runner* (Settings → Actions → Runners) y hacer que el mismo flujo corra allí. Es más cómodo de gestionar, pero si el mini PC está apagado la tarea espera sin ejecutarse, por eso aquí se prefiere el temporizador como respaldo del flujo en la nube.
