#!/bin/bash
# T95 · Tanda semanal de traducciones en sk-atlas. La lanza un temporizador de `maquina` como `atlas`, dentro de
# atlas-trad.slice y nunca a la vez que atlas-textos. Trabaja en su propio clon (no en /opt/atlas ni en /root/atlas):
# lo pone igual que origin/main, traduce lo que falta con scripts/traducir_local.py y, si hay algo nuevo, sube la rama
# trad-AAAA-MM-DD y abre un PR. Lo fusiona atlas con la CI en verde. Autoría pública: Sukima-Labs.
# Necesita GH_TOKEN (token de grano fino, solo sukima-labs/atlasonu: contents y pull requests), de /etc/atlas/github-trad.env.
set -euo pipefail
CLON="${ATLAS_TRAD_CLON:-/var/lib/atlas/trad/atlasonu}"
REPO="sukima-labs/atlasonu"
: "${GH_TOKEN:?falta GH_TOKEN (/etc/atlas/github-trad.env)}"
export GH_TOKEN GIT_TERMINAL_PROMPT=0
GH="${ATLAS_GH:-$(command -v gh || echo /usr/bin/gh)}"
# El token va por un ayudante de credenciales que lo lee del entorno: nunca en la URL ni en la línea de órdenes.
CRED='credential.helper=!f() { echo username=x-access-token; echo "password=$GH_TOKEN"; }; f'

# Si la tanda anterior sigue sin fusionar, no se abre otra con las mismas traducciones.
abiertos=$("$GH" pr list --repo "$REPO" --state open --json headRefName --jq '[.[] | select(.headRefName | startswith("trad-"))] | length')
if [ "$abiertos" != 0 ]; then echo "Hay una tanda de traducciones sin fusionar: no se abre otra."; exit 0; fi

[ -d "$CLON/.git" ] || git clone -q "https://github.com/$REPO.git" "$CLON"
cd "$CLON"
git fetch -q origin main
git checkout -q -B main origin/main
git reset -q --hard origin/main
git clean -qfdx -- idiomas data/idiomas

salida=$(python3 -I scripts/traducir_local.py)
echo "$salida" | tail -n 1
if git diff --quiet -- idiomas data/idiomas && [ -z "$(git ls-files --others --exclude-standard -- idiomas)" ]; then
  echo "Nada nuevo que subir."; exit 0
fi

rama="trad-$(date +%F)"
git checkout -q -B "$rama"
git add -- idiomas/*.json data/idiomas/*.js
export GIT_AUTHOR_NAME="Sukima-Labs" GIT_AUTHOR_EMAIL="atlas@sukima-labs.invalid" GIT_COMMITTER_NAME="Sukima-Labs" GIT_COMMITTER_EMAIL="atlas@sukima-labs.invalid"
git commit -q -m "Traducciones: tanda del $(date +%d-%m-%Y) con el modelo local (T95)"
git -c "$CRED" push -q origin "HEAD:refs/heads/$rama"
resumen=$(echo "$salida" | tail -n 1)
"$GH" pr create --repo "$REPO" --base main --head "$rama" --title "Traducciones: tanda del $(date +%d-%m-%Y) (T95)" --body "Refs #321

Tanda automática de \`scripts/traducir_tanda.sh\` en sk-atlas: textos nuevos de \`idiomas/es.json\` traducidos a en, fr, ar, zh y ru con el modelo local (Qwen3-4B).

$resumen

Lo traducido queda en \`idiomas/automaticas.json\` para la revisión por personas nativas (#262). Lo que no pasó la comprobación sigue en español."
