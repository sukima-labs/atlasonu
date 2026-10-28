#!/usr/bin/env bash
# Revisión de las fuentes oficiales desde el mini PC. Misma lógica que el flujo de GitHub Actions
# (scripts/actualizar_datos.sh): si algo falla o los datos se degradan, ABORTA sin publicar nada.
# Pensado para ejecutarse desde un clon DEDICADO (no edites a mano en esa carpeta).
set -euo pipefail
DIR="${ATLAS_DIR:-$HOME/atlas-onu}"
LOGS="${ATLAS_LOGS:-$HOME/atlas-onu-logs}"
mkdir -p "$LOGS"
exec > >(tee -a "$LOGS/revision-$(date +%F).log") 2>&1
echo "=== $(date '+%F %T %Z') · revisión desde el mini PC ==="
exec 9>"$LOGS/.lock"
flock -n 9 || { echo "Ya hay una revisión en curso: salgo."; exit 0; }
cd "$DIR"
git fetch -q origin main
git checkout -q main
git reset -q --hard origin/main        # siempre se parte de lo ya publicado
ATLAS_EJECUTOR="Mini PC (atlas-onu-minipc)" bash scripts/actualizar_datos.sh
git config user.name  "atlas-onu-minipc"
git config user.email "atlas-onu-minipc@users.noreply.github.com"
git add data
if git diff --cached --quiet; then echo "Nada que publicar."; exit 0; fi
if git diff --cached --name-only | grep -qvE '^data/(estado.json|noticias.js|revisiones.json)$'; then
  MSG="Actualización automática (mini PC): cambios en los datos oficiales ($(date -u +%F))"
else
  MSG="Revisión de fuentes (mini PC): sin cambios ($(date -u +%F))"
fi
git commit -q -m "$MSG"
if git push -q origin main; then
  echo "Publicado: $MSG"
else
  echo "El push fue rechazado (otra revisión publicó antes): descarto lo local y salgo sin error."
  git fetch -q origin main && git reset -q --hard origin/main
fi
