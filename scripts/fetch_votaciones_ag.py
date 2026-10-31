#!/usr/bin/env python3
"""Posición de cada país en las votaciones de la Asamblea General (puntos ideales, Bailey-Strezhnev-Voeten).
Fuente: Harvard Dataverse, doi:10.7910/DVN/LEJUQZ (licencia CC0 1.0). Se baja el CSV de estimaciones por país y año y se
escribe un archivo por país en data/votaciones/<ISO>.js (carga bajo demanda) y el resumen data/fuentes/votaciones_ag.json.
Escala: valores altos = cerca de EE. UU. y las democracias occidentales; bajos = cerca de la mayoría de países en desarrollo.
Si la descarga falla o cambia el formato, sale con 1 y NO toca los archivos anteriores."""
import csv, io, json, os, sys, urllib.request

UA = {"User-Agent": "ATLAS-ONU/1.0 (+https://github.com/cataplum1414/onu-arqueologia-documental)"}
DOI = "doi:10.7910/DVN/LEJUQZ"
BASE = "https://dataverse.harvard.edu/api/"


def pedir(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
        return r.read()


def main():
    meta = json.loads(pedir(BASE + "datasets/:persistentId/?persistentId=" + DOI))["data"]["latestVersion"]
    lic = (meta.get("license") or {}).get("rightsIdentifier")
    if lic != "CC0-1.0":
        print("La licencia ya no es CC0-1.0:", lic)
        return 1
    arch = [f for f in meta["files"] if f["label"].startswith("IdealpointestimatesFP") and f["label"].endswith(".csv")]
    if len(arch) != 1:
        print("No se localiza el CSV de estimaciones:", [f["label"] for f in meta["files"]])
        return 1
    f = arch[0]
    filas = list(csv.DictReader(io.StringIO(pedir(BASE + "access/datafile/%d" % f["dataFile"]["id"]).decode("utf-8"))))
    campos = ("iso3c", "year", "IdealPointFP", "Q5%FP", "Q95%FP", "NVotesFP")
    if not filas or any(c not in filas[0] for c in campos):
        print("Formato inesperado:", list(filas[0]) if filas else "vacío")
        return 1
    por = {}
    for r in filas:
        if r["iso3c"]:
            por.setdefault(r["iso3c"], []).append([int(r["year"]), round(float(r["IdealPointFP"]), 2), round(float(r["Q5%FP"]), 2),
                                                     round(float(r["Q95%FP"]), 2), int(r["NVotesFP"])])
    os.makedirs("data/votaciones", exist_ok=True)
    for iso, d in por.items():
        d.sort()
        with open("data/votaciones/%s.js" % iso, "w", encoding="utf-8") as o:
            o.write("window.PAIS_VOTOS=window.PAIS_VOTOS||{};window.PAIS_VOTOS['%s']=%s;" % (iso, json.dumps(d, separators=(",", ":"))))
    json.dump({"fuente": "Bailey, Strezhnev y Voeten, United Nations General Assembly Voting Data (puntos ideales), Harvard Dataverse",
               "doi": DOI, "licencia": "CC0 1.0", "version": "%s.%s" % (meta.get("versionNumber"), meta.get("versionMinorNumber")),
               "archivo": f["label"], "anios":
               [min(int(r["year"]) for r in filas), max(int(r["year"]) for r in filas)],
               "paises": sorted(por), "campos": ["año", "punto ideal", "q5", "q95", "votaciones"]},
              open("data/fuentes/votaciones_ag.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Votaciones AG: %d países, %d filas" % (len(por), len(filas)))
    return 0


sys.exit(main())
