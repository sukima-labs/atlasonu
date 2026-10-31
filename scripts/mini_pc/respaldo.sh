#!/usr/bin/env bash
# Copia de seguridad cifrada de ATLAS ONU en el mini PC: repositorio completo (git bundle), contador de visitas y la copia privada de EPU.
# Cifra con `age` y una clave PÚBLICA (la privada no vive en este equipo: sin ella nadie puede abrir la copia, ni siquiera quien robe el disco).
# Uso:  bash scripts/mini_pc/respaldo.sh        Variables: ATLAS_DIR, ATLAS_RESPALDOS, ATLAS_RESPALDO_CLAVE
set -euo pipefail
DIR="${ATLAS_DIR:-$HOME/Documentos/atlas-onu}"
OUT="${ATLAS_RESPALDOS:-$HOME/atlas-onu-respaldos}"
CLAVE="${ATLAS_RESPALDO_CLAVE:-$HOME/.config/atlas-onu/respaldo-publica.txt}"
GUARDAR=8
[ -s "$CLAVE" ] || { echo "Falta la clave pública $CLAVE (ver docs/RECUPERACION.md, paso 1)"; exit 1; }
command -v age >/dev/null || { echo "Falta age:  sudo apt install -y age"; exit 1; }
mkdir -p "$OUT"; chmod 700 "$OUT"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
git -C "$DIR" bundle create "$T/repositorio.bundle" --all >/dev/null 2>&1
git -C "$DIR" bundle verify "$T/repositorio.bundle" >/dev/null 2>&1 || { echo "El bundle no verifica: aborto"; exit 1; }
mkdir "$T/extra"
[ -d "$HOME/.local/share/atlas-onu" ] && cp -a "$HOME/.local/share/atlas-onu" "$T/extra/visitas"
[ -d "$HOME/atlas-epu-privado" ] && cp -a "$HOME/atlas-epu-privado" "$T/extra/atlas-epu-privado"
F="$OUT/atlas-onu-$(date +%F).tar.age"
tar -C "$T" -cf - repositorio.bundle extra | age -R "$CLAVE" -o "$F.tmp"
mv "$F.tmp" "$F"; chmod 600 "$F"
ls -1t "$OUT"/atlas-onu-*.tar.age | tail -n +$((GUARDAR+1)) | xargs -r rm -f
echo "Copia lista: $F ($(du -h "$F" | cut -f1)); se guardan las últimas $GUARDAR."
