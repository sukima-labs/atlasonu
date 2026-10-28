#!/usr/bin/env bash
# Sube la rama actual, abre el PR si no existe, espera al CI, fusiona en main y deja la carpeta limpia.
# Reintenta cada paso de red (el DNS del mini PC falla a ratos). Uso: bash scripts/subir_tarea.sh "Título del PR"
set -uo pipefail
cd "$(git rev-parse --show-toplevel)"
rama=$(git branch --show-current)
[ "$rama" = main ] && { echo "Estás en main: crea una rama de trabajo."; exit 1; }
titulo=${1:-$(git log -1 --format=%s)}
reintenta() { local n; for n in $(seq 1 30); do "$@" && return 0; echo "… reintento $n/30 ($*)" >&2; sleep 10; done; return 1; }
cuerpo=$'Cambio de la tarea en curso.\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)\n\nhttps://claude.ai/code/session_01A5rcF9XQ7TfRaELopyEoTW'
reintenta git push -q -u origin "$rama" || exit 1
gh pr view "$rama" --json number >/dev/null 2>&1 || reintenta gh pr create --title "$titulo" --body "$cuerpo" || exit 1
sleep 8
reintenta gh pr checks "$rama" --watch --fail-fast >/dev/null || { echo "El CI falló: no se fusiona."; exit 1; }
reintenta gh pr merge "$rama" --merge --delete-branch || exit 1
git checkout -q main && reintenta git pull -q
git branch -D "$rama" -q 2>/dev/null
echo "Hecho: $titulo fusionado en main."
