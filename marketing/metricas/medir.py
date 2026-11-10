#!/usr/bin/env python3
"""Mide la audiencia de ATLAS ONU y añade una fila a marketing/metricas/registro.csv.

Solo usa agregados: estrellas, visitas del repo (GitHub las guarda 14 días, de ahí la serie semanal),
issues abiertos y el contador propio de la web (total y por país, sin identificadores).

  python3 -I marketing/metricas/medir.py [--visitas-url URL] [--sin-escribir]

Necesita `gh` con sesión. El contador se lee de --visitas-url (en sk-atlas: http://127.0.0.1:8787/visitas);
sin esa opción la columna queda vacía. No guarda IP, cookies ni nada de personas.
"""
import csv
import datetime
import json
import os
import subprocess
import sys
import urllib.request

REPO = "sukima-labs/atlasonu"
CAMPOS = ["fecha", "estrellas", "forks", "seguidores", "issues_abiertos",
          "repo_visitas_14d", "repo_personas_14d", "repo_clones_14d", "web_visitas_total"]
CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "registro.csv")


def gh(ruta):
    r = subprocess.run(["gh", "api", ruta], capture_output=True, text=True, timeout=60)
    if r.returncode:
        sys.exit("gh api %s falló: %s" % (ruta, r.stderr.strip()))
    return json.loads(r.stdout)


def contador(url):
    if not url:
        return ""
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.load(r).get("total", "")


def main(argv):
    url = argv[argv.index("--visitas-url") + 1] if "--visitas-url" in argv else ""
    repo = gh("repos/" + REPO)
    vistas = gh("repos/%s/traffic/views" % REPO)
    clones = gh("repos/%s/traffic/clones" % REPO)
    fila = {
        "fecha": datetime.date.today().isoformat(),
        "estrellas": repo["stargazers_count"],
        "forks": repo["forks_count"],
        "seguidores": repo["subscribers_count"],
        "issues_abiertos": repo["open_issues_count"],
        "repo_visitas_14d": vistas["count"],
        "repo_personas_14d": vistas["uniques"],
        "repo_clones_14d": clones["count"],
        "web_visitas_total": contador(url),
    }
    print(json.dumps(fila, ensure_ascii=False))
    if "--sin-escribir" in argv:
        return
    nuevo = not os.path.exists(CSV)
    with open(CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        if nuevo:
            w.writeheader()
        w.writerow(fila)


if __name__ == "__main__":
    main(sys.argv[1:])
