#!/usr/bin/env bash
# Revisión de las fuentes oficiales (se ejecuta cada día en GitHub Actions; también a mano).
# Solo reescribe los datos si el contenido cambió; si los datos se degradan o falla la red, ABORTA sin publicar nada.
set -euo pipefail
cd "$(dirname "$0")/.."
INICIO=$(date +%s)
HOY=$(date -u +%F)
PREV=$(mktemp); cp data/catalogo.json "$PREV"
FP=$(python3 -I -c "import json;print(json.load(open('data/catalogo.json',encoding='utf-8'))['consultado'])")
TMP=$(mktemp -d)
VER=data/fuentes/verificacion_simbolos.json
# T56 (#313, decidido por Patricio el 12-11-2026): spinternet.ohchr.org y spcommreports.ohchr.org dicen «Disallow: /» en su
# robots.txt. No se leen solos: se conservan los datos anteriores (con su fecha) hasta tener permiso por escrito del
# ACNUDH. OHCHR_SP=si los vuelve a leer, solo a mano y con ese permiso.
OHCHR_SP="${OHCHR_SP:-no}"
if [ "$OHCHR_SP" = si ]; then
  python3 -I scripts/fetch_regiones.py "$FP"
  python3 -I scripts/fetch_paises.py "$FP"
else echo "Comunicaciones por región y visitas por país: omitido (T56, #313: el robots.txt del ACNUDH lo prohíbe)."; fi
python3 -I scripts/fetch_tratados.py "$FP"
python3 -I scripts/fetch_tratados_texto.py
# T56: la Biblioteca Digital prohíbe /search en robots.txt. Desactivado por defecto; solo se usa con BIBLIOTECA_SEARCH=si.
BIBLIOTECA_SEARCH="${BIBLIOTECA_SEARCH:-no}"
# Documentos por país y jurisprudencia ya no buscan (T56): conservan lo anotado y solo bajan los registros (/record/N)
# que se añadan a mano a data/fuentes/registros_biblioteca.json. Sin números nuevos, no usan la red.
python3 -I scripts/fetch_docs_pais.py
MARCO=conservado
echo "Documentos marco: tres documentos fijos; se refrescan a mano con fetch_documentos_marco.py (registros anotados)."
COMUNICACIONES=ok
python3 -I scripts/fetch_comunicaciones_cifras.py || { COMUNICACIONES=conservado; echo "Cifras de comunicaciones: no se pudieron actualizar; se conservan las anteriores."; }
echo "pausa de 60 s para no saturar la Biblioteca Digital"; sleep 60
if [ "$OHCHR_SP" = si ]; then for t in TM CM; do for l in en es; do
  curl -fsS -m 90 -L "https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type=$t&lang=$l" -o "$TMP/spin_${t}_$l.html"
  python3 -I scripts/parse_ohchr_mandates.py "$TMP/spin_${t}_$l.html" $t $l "data/fuentes/ohchr_${t}_$l.json" "$FP"
done; done; else echo "Lista de mandatos: omitida (T56, #313); se conserva la de la última lectura."; fi
python3 -I scripts/verify_symbols.py data/fuentes/ohchr_TM_en.json data/fuentes/ohchr_CM_en.json "$VER"
python3 -I scripts/build_mecanismos.py > /dev/null
python3 -I scripts/build_catalog.py "$VER" "$FP" > /dev/null
python3 -I scripts/resolve_texts.py data/catalogo.json data/fuentes/textos.json
python3 -I scripts/build_catalog.py "$VER" "$FP" > /dev/null
python3 -I scripts/validar_datos.py "$PREV" data/catalogo.json
if cmp -s "$PREV" data/catalogo.json; then CAMBIO=0; else CAMBIO=1; fi
if [ "$CAMBIO" = 1 ]; then
  python3 -I scripts/_fechar_fuentes.py "$HOY"
  python3 -I scripts/build_catalog.py "$VER" "$HOY" > /dev/null
  python3 -I scripts/detectar_cambios.py "$PREV" data/catalogo.json "$HOY"
  python3 -I scripts/exportar_excel.py
fi
JURISPRUDENCIA=conservado
JURISPRUDENCIA=ok; python3 -I scripts/fetch_jurisprudencia.py || { JURISPRUDENCIA=conservado; echo "Jurisprudencia: no se pudo actualizar; se conserva la anterior."; }
NOTICIAS=ok
python3 -I scripts/fetch_noticias.py || { NOTICIAS=conservado; echo "Noticias: no se pudieron actualizar; se conservan las anteriores."; }
python3 -I scripts/escribir_estado.py data/catalogo.json "$CAMBIO"
python3 -I scripts/generar_feed_cambios.py
node tests/invariantes.cjs
python3 -I scripts/registrar_revision.py "$INICIO" "$CAMBIO" "$MARCO" "$NOTICIAS"
echo "Revisión terminada. Cambios en los datos: $CAMBIO"
