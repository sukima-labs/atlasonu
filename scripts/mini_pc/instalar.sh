#!/usr/bin/env bash
# Instala en el mini PC (Linux con systemd) la revisión automática de ATLAS ONU a las 12:00 y 00:00 (hora local); es la revisión principal y GitHub Actions queda como respaldo.
# Uso:  bash scripts/mini_pc/instalar.sh        (desde el clon dedicado, p. ej. ~/atlas-onu)
set -euo pipefail
DIR="$(cd "$(dirname "$0")/../.." && pwd)"
echo "Carpeta del proyecto: $DIR"
faltan=()
for c in git python3 node flock pdftotext; do command -v "$c" >/dev/null || faltan+=("$c"); done
if [ ${#faltan[@]} -gt 0 ]; then
  echo "Faltan programas: ${faltan[*]}"
  echo "En Debian/Ubuntu:  sudo apt install -y git python3 python3-pip nodejs util-linux poppler-utils"
  exit 1
fi
python3 -c "import openpyxl" 2>/dev/null || { echo "Falta openpyxl:  pip install --user openpyxl   (o: sudo apt install python3-openpyxl)"; exit 1; }
git -C "$DIR" ls-remote --exit-code origin main >/dev/null || { echo "No puedo leer el repositorio remoto (¿token o red?)"; exit 1; }
U="$HOME/.config/systemd/user"; mkdir -p "$U"
cat > "$U/atlas-onu.service" <<EOF
[Unit]
Description=ATLAS ONU: revisión de las fuentes oficiales
After=network-online.target
Wants=network-online.target
[Service]
Type=oneshot
Environment=ATLAS_DIR=$DIR
ExecStart=/usr/bin/env bash $DIR/scripts/mini_pc/actualizar_local.sh
TimeoutStartSec=45min
EOF
cat > "$U/atlas-onu.timer" <<'EOF'
[Unit]
Description=ATLAS ONU: revisión a las 12:00 y a las 00:00
[Timer]
OnCalendar=*-*-* 00:00:00
OnCalendar=*-*-* 12:00:00
Persistent=true
RandomizedDelaySec=120
[Install]
WantedBy=timers.target
EOF
cat > "$U/atlas-busqueda.service" <<EOF
[Unit]
Description=ATLAS ONU: servicio de búsqueda en vivo (solo 127.0.0.1)
[Service]
ExecStart=/usr/bin/python3 -I $DIR/scripts/mini_pc/busqueda_servicio.py
Restart=always
RestartSec=5
[Install]
WantedBy=default.target
EOF
cat > "$U/atlas-respaldo.service" <<EOF
[Unit]
Description=ATLAS ONU: copia de seguridad cifrada
[Service]
Type=oneshot
Environment=ATLAS_DIR=$DIR
ExecStart=/usr/bin/env bash $DIR/scripts/mini_pc/respaldo.sh
Nice=10
EOF
cat > "$U/atlas-respaldo.timer" <<'EOF'
[Unit]
Description=ATLAS ONU: copia cifrada cada domingo a las 03:00
[Timer]
OnCalendar=Sun *-*-* 03:00:00
Persistent=true
[Install]
WantedBy=timers.target
EOF
systemctl --user daemon-reload
systemctl --user enable --now atlas-onu.timer atlas-busqueda.service atlas-respaldo.timer
echo "Temporizador instalado. Próximas ejecuciones:"; systemctl --user list-timers atlas-onu.timer --no-pager || true
echo "Para que corra aunque nadie haya iniciado sesión:  sudo loginctl enable-linger $USER"
echo "Prueba ahora mismo:  systemctl --user start atlas-onu.service  (y mira: journalctl --user -u atlas-onu.service -f)"
