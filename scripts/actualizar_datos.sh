#!/usr/bin/env bash
# Regenera el catálogo desde las fuentes oficiales. Uso: bash scripts/actualizar_datos.sh
set -euo pipefail
cd "$(dirname "$0")/.."
FECHA=$(date +%F); TMP=$(mktemp -d)
for t in TM CM; do for l in en es; do
  curl -fsS -m 90 -L "https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type=$t&lang=$l" -o "$TMP/spin_${t}_$l.html"
  python3 -I scripts/parse_ohchr_mandates.py "$TMP/spin_${t}_$l.html" $t $l "data/fuentes/ohchr_${t}_$l.json" "$FECHA"
done; done
python3 -I scripts/verify_symbols.py data/fuentes/ohchr_TM_en.json data/fuentes/ohchr_CM_en.json data/fuentes/verificacion_simbolos.json
python3 -I scripts/build_catalog.py data/fuentes/verificacion_simbolos.json "$FECHA"
(cd tests && node smoke.cjs)
