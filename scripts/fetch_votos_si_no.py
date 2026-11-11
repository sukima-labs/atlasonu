#!/usr/bin/env python3
"""Votos sí / no / abstención de cada país en la Asamblea General de la ONU, por año (1946–2013).
Fuente: Harvard Dataverse, doi:10.7910/DVN/7UBUUI («United Nations General Assembly Voting, 1946-2013», fichero
un_rc_3.txt; licencia CC0 1.0). Trae, por cada votación nominal, el voto de cada Estado.
Escribe un archivo por país en data/votos_si_no/<ISO>.js (carga bajo demanda) y el resumen data/fuentes/votos_si_no.json.
Cada fila: [año, sí, no, abstención, ausente]. Los nombres históricos se suman al país actual (Birmania→Myanmar,
Zaire→R. D. del Congo…); las repúblicas soviéticas de Bielorrusia y Ucrania son países de pleno derecho en la ONU y
se cuentan aparte de la URSS. Si la descarga falla, la licencia cambia o el formato no es el esperado, sale con 1 y NO
toca los archivos anteriores."""
import csv, io, json, os, sys, urllib.request

UA = {"User-Agent": "ATLAS-ONU/1.0 (+https://github.com/sukima-labs/atlasonu)"}
DOI = "doi:10.7910/DVN/7UBUUI"
BASE = "https://dataverse.harvard.edu/api/"
ARCHIVO = "un_rc_3.txt"

NOMBRES = {
 "AFGHANISTAN": "AFG", "ALBANIA": "ALB", "ALGERIA": "DZA", "ANDORRA": "AND", "ANGOLA": "AGO", "ANTIGUA AND BARBUDA": "ATG",
 "ARGENTINA": "ARG", "ARMENIA": "ARM", "AUSTRALIA": "AUS", "AUSTRIA": "AUT", "AZERBAIJAN": "AZE", "BAHAMAS": "BHS",
 "BAHRAIN": "BHR", "BANGLADESH": "BGD", "BARBADOS": "BRB", "BELARUS": "BLR", "BYELORUSSIAN SSR": "BLR", "BELGIUM": "BEL",
 "BELIZE": "BLZ", "BENIN": "BEN", "DAHOMEY": "BEN", "BHUTAN": "BTN", "BOLIVIA": "BOL",
 "BOLIVIA (PLURINATIONAL STATE OF)": "BOL", "BOSNIA": "BIH", "BOSNIA AND HERZEGOVINA": "BIH", "BOTSWANA": "BWA",
 "BRAZIL": "BRA", "BRUNEI DARUSSALAM": "BRN", "BULGARIA": "BGR", "BURKINA FASO": "BFA", "BURKINFASO": "BFA",
 "UPPER VOLTA": "BFA", "BURMA": "MMR", "MYANMAR": "MMR", "BURUNDI": "BDI", "CABO VERDE": "CPV", "CAPE VERDE": "CPV",
 "CAMBODIA": "KHM", "KAMPUCHEA": "KHM", "KHMER REPUBLIC": "KHM", "CAMEROON": "CMR", "UNITED REPUBLIC OF CAMEROON": "CMR",
 "CANADA": "CAN", "CENTRAL AFRICAN EMPIRE": "CAF", "CENTRAL AFRICAN REPUBLIC": "CAF", "CEYLON": "LKA", "SRI LANKA": "LKA",
 "CHAD": "TCD", "CHILE": "CHL", "COLOMBIA": "COL", "COMOROS": "COM", "CONGO": "COG", "CONGO (BRAZZAVILLE)": "COG",
 "CONGO (LEOPOLDVILLE)": "COD", "DEMOCRATIC REPUBLIC OF THE CONGO": "COD", "ZAIRE": "COD", "COSTA RICA": "CRI",
 "COTE D'IVOIRE": "CIV", "IVORY COAST": "CIV", "CROATIA": "HRV", "CUBA": "CUB", "CYPRUS": "CYP", "CZECH REPUBLIC": "CZE",
 "CZECHOSLOVAKIA": "CSK", "DEMOCRATIC PEOPLE'S REPUBLIC OF KOREA": "PRK", "DENMARK": "DNK", "DJIBOUTI": "DJI",
 "DOMINICA": "DMA", "DOMINICAN REPUBLIC": "DOM", "EAST-TIMOR": "TLS", "TIMOR-LESTE": "TLS", "ECUADOR": "ECU",
 "EGYPT": "EGY", "UNITED ARAB REPUBLIC": "EGY", "EL SALVADOR": "SLV", "EQUATORIAL GUINEA": "GNQ", "ERITREA": "ERI",
 "ESTONIA": "EST", "ETHIOPIA": "ETH", "FEDERATION OF MALAYA": "MYS", "MALAYSIA": "MYS", "FIJI": "FJI", "FINLAND": "FIN",
 "FRANCE": "FRA", "GABON": "GAB", "GAMBIA": "GMB", "GEORGIA": "GEO", "GERMAN DEMOCRATIC REPUBLIC": "DDR", "GERMANY": "DEU",
 "GERMANY, FEDERAL REPUBLIC OF": "DEU", "GHANA": "GHA", "GREECE": "GRC", "GRENADA": "GRD", "GUATEMALA": "GTM",
 "GUINEA": "GIN", "GUINEA-BISSAU": "GNB", "GUYANA": "GUY", "HAITI": "HTI", "HONDURAS": "HND", "HUNGARY": "HUN",
 "ICELAND": "ISL", "INDIA": "IND", "INDONESIA": "IDN", "IRAN": "IRN", "IRAN (ISLAMIC REPUBLIC OF)": "IRN", "IRAQ": "IRQ",
 "IRELAND": "IRL", "ISRAEL": "ISR", "ITALY": "ITA", "JAMAICA": "JAM", "JAPAN": "JPN", "JORDAN": "JOR", "KAZAKHSTAN": "KAZ",
 "KENYA": "KEN", "KIRIBATI": "KIR", "REPUBLIC OF KIRIBATI": "KIR", "KUWAIT": "KWT", "KYRGYZSTAN": "KGZ",
 "LAO PEOPLE'S DEMOCRATIC REPUBLIC": "LAO", "LAOS": "LAO", "LATVIA": "LVA", "LEBANON": "LBN", "LESOTHO": "LSO",
 "LIBERIA": "LBR", "LIBYA": "LBY", "LIBYAN ARAB JAMAHIRIYA": "LBY", "LIBYAN ARAB REPUBLIC": "LBY", "LIECHTENSTEIN": "LIE",
 "LITHUANIA": "LTU", "LUXEMBOURG": "LUX", "MADAGASCAR": "MDG", "MALAWI": "MWI", "MALDIVE ISLANDS": "MDV", "MALDIVES": "MDV",
 "MALI": "MLI", "MALTA": "MLT", "MARSHALL ISLANDS": "MHL", "MAURITANIA": "MRT", "MAURITIUS": "MUS", "MEXICO": "MEX",
 "MICRONESIA (FEDERATED STATES OF)": "FSM", "MOLDOVA": "MDA", "REPUBLIC OF MOLDOVA": "MDA", "MONACO": "MCO", "MONGOLIA": "MNG",
 "MONTENEGRO": "MNE", "MOROCCO": "MAR", "MOZAMBIQUE": "MOZ", "NAMIBIA": "NAM", "NAURU": "NRU", "NEPAL": "NPL",
 "NETHERLANDS": "NLD", "NEW ZEALAND": "NZL", "NICARAGUA": "NIC", "NIGER": "NER", "NIGERIA": "NGA", "NORWAY": "NOR",
 "OMAN": "OMN", "PAKISTAN": "PAK", "PALAU": "PLW", "PANAMA": "PAN", "PAPUA NEW GUINEA": "PNG", "PARAGUAY": "PRY",
 "PERU": "PER", "PHILIPPINE REPUBLIC": "PHL", "PHILIPPINES": "PHL", "POLAND": "POL", "PORTUGAL": "PRT", "QATAR": "QAT",
 "REPUBLIC OF KOREA": "KOR", "RHODESIA": "ZWE", "ZIMBABWE": "ZWE", "ROMANIA": "ROU", "RUSSIAN FEDERATION": "RUS",
 "USSR": "RUS", "RWANDA": "RWA", "SAINT CHRISTOPHER AND NEVIS": "KNA", "SAINT KITTS AND NEVIS": "KNA", "SAINT LUCIA": "LCA",
 "SAINT VINCENT AND THE GRENADINES": "VCT", "SAMOA": "WSM", "SAN MARINO": "SMR", "SAO TOME AND PRINCIPE": "STP",
 "SAUDI ARABIA": "SAU", "SENEGAL": "SEN", "SERBIA": "SRB", "SEYCHELLES": "SYC", "SIAM": "THA", "THAILAND": "THA",
 "SIERRA LEONE": "SLE", "SINGAPORE": "SGP", "SLOVAKIA": "SVK", "SLOVENIA": "SVN", "SOLOMON ISLANDS": "SLB", "SOMALIA": "SOM",
 "SOUTH AFRICA": "ZAF", "UNION OF SOUTH AFRICA": "ZAF", "SOUTH SUDAN": "SSD", "SOUTHERN YEMEN": "YMD", "SPAIN": "ESP",
 "SUDAN": "SDN", "SURINAME": "SUR", "SWAZILAND": "SWZ", "SWEDEN": "SWE", "SWITZERLAND": "CHE", "SYRIA": "SYR",
 "SYRIAN ARAB REPUBLIC": "SYR", "TAJIKISTAN": "TJK", "TANGANYIKA": "TZA", "ZANZIBAR": "TZA", "UNITED REPUBLIC OF TANZANIA": "TZA",
 "THE FORMER YUGOSLAV REPUBLIC OF MACEDONIA": "MKD", "TOGO": "TGO", "TONGA": "TON", "TRINIDAD AND TOBAGO": "TTO",
 "TUNISIA": "TUN", "TURKEY": "TUR", "TURKMENISTAN": "TKM", "TUVALU": "TUV", "UGANDA": "UGA", "UKRAINE": "UKR",
 "UKRAINIAN SSR": "UKR", "UNITED ARAB EMIRATES": "ARE", "UNITED KINGDOM": "GBR", "UNITED STATES": "USA", "URUGUAY": "URY",
 "UZBEKISTAN": "UZB", "VANUATU": "VUT", "VENEZUELA": "VEN", "VENEZUELA (BOLIVARIAN REPUBLIC OF)": "VEN", "VIET NAM": "VNM",
 "ZAMBIA": "ZMB",
}
VOTO = {"YES": 0, "NO": 1, "ABSTAIN": 2, "ABSENT": 3}


def iso_de(nombre, anio):
    """Casos donde el mismo nombre es otro país según el año (China, Yemen, Yugoslavia)."""
    if nombre == "CHINA":
        return "TWN" if anio <= 1970 else "CHN"   # hasta 1971 ocupaba el asiento la República de China (Taiwán)
    if nombre == "YEMEN":
        return "YAR" if anio < 1990 else "YEM"
    if nombre == "YUGOSLAVIA":
        return "YUG" if anio <= 1991 else "SCG"
    return NOMBRES.get(nombre)


def pedir(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
        return r.read()


def main():
    meta = json.loads(pedir(BASE + "datasets/:persistentId/?persistentId=" + DOI))["data"]["latestVersion"]
    lic = (meta.get("license") or {}).get("rightsIdentifier")
    if lic != "CC0-1.0":
        print("La licencia ya no es CC0-1.0:", lic)
        return 1
    arch = [f for f in meta["files"] if f["label"] == ARCHIVO]
    if len(arch) != 1:
        print("No se localiza", ARCHIVO, [f["label"] for f in meta["files"]])
        return 1
    texto = pedir(BASE + "access/datafile/%d" % arch[0]["dataFile"]["id"]).decode("utf-8", errors="replace")
    filas = list(csv.reader(io.StringIO(texto), delimiter=";"))
    cab = [c.strip() for c in filas[0]]
    if len(cab) < 200 or cab[7] != "year" or "UNITED STATES" not in cab:
        print("Formato inesperado:", cab[:14])
        return 1
    desconocidos = sorted(n for n in cab[13:] if n not in NOMBRES and n not in ("CHINA", "YEMEN", "YUGOSLAVIA"))
    if desconocidos:
        print("Países sin código ISO (añádelos a NOMBRES):", desconocidos)
        return 1
    por = {}
    for f in filas[1:]:
        if len(f) != len(cab):
            continue
        anio = int(f[7])
        for n, v in zip(cab[13:], f[13:]):
            k = VOTO.get(v.strip())
            if k is None:
                continue
            iso = iso_de(n, anio)
            fila = por.setdefault(iso, {}).setdefault(anio, [0, 0, 0, 0])
            fila[k] += 1
    os.makedirs("data/votos_si_no", exist_ok=True)
    for iso, anios in por.items():
        d = [[a] + v for a, v in sorted(anios.items())]
        with open("data/votos_si_no/%s.js" % iso, "w", encoding="utf-8") as o:
            o.write("window.PAIS_SINO=window.PAIS_SINO||{};window.PAIS_SINO['%s']=%s;" % (iso, json.dumps(d, separators=(",", ":"))))
    ult = max(a for d in por.values() for a in d)
    json.dump({"fuente": "United Nations General Assembly Voting, 1946-2013 (votos nominales de cada Estado), Harvard Dataverse",
               "doi": DOI, "licencia": "CC0 1.0", "archivo": ARCHIVO, "anios": [min(a for d in por.values() for a in d), ult],
               "paises": sorted(por), "campos": ["año", "sí", "no", "abstención", "ausente"]},
              open("data/fuentes/votos_si_no.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Votos sí/no/abstención: %d países, hasta %d" % (len(por), ult))
    return 0


sys.exit(main())
