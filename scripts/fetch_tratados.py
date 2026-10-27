#!/usr/bin/env python3
"""Estado de ratificación de los 18 instrumentos de derechos humanos (9 tratados básicos y sus protocolos) por país,
desde la Colección de Tratados de la ONU (treaties.un.org, Capítulo IV). Salida: data/fuentes/tratados_untc.json
Uso: fetch_tratados.py <fecha>"""
import re, json, html, sys, unicodedata, urllib.request, concurrent.futures as cf
UA = {'User-Agent': 'ATLAS-ONU/1.0 (academic)'}
# id MTDSG, siglas, nombre en español (elaboración propia), ¿tratado básico?, ¿permite comunicaciones individuales?
T = [('IV-2', 'CERD', 'Convención Internacional sobre la Eliminación de Todas las Formas de Discriminación Racial', 1, 0),
     ('IV-3', 'PIDESC', 'Pacto Internacional de Derechos Económicos, Sociales y Culturales', 1, 0),
     ('IV-3-a', 'OP-PIDESC', 'Protocolo Facultativo del PIDESC (comunicaciones individuales e investigaciones)', 0, 1),
     ('IV-4', 'PIDCP', 'Pacto Internacional de Derechos Civiles y Políticos', 1, 0),
     ('IV-5', 'OP1-PIDCP', 'Primer Protocolo Facultativo del PIDCP (comunicaciones individuales)', 0, 1),
     ('IV-12', 'OP2-PIDCP', 'Segundo Protocolo Facultativo del PIDCP (abolición de la pena de muerte)', 0, 0),
     ('IV-8', 'CEDAW', 'Convención sobre la Eliminación de Todas las Formas de Discriminación contra la Mujer', 1, 0),
     ('IV-8-b', 'OP-CEDAW', 'Protocolo Facultativo de la CEDAW (comunicaciones individuales e investigaciones)', 0, 1),
     ('IV-9', 'CAT', 'Convención contra la Tortura y Otros Tratos o Penas Crueles, Inhumanos o Degradantes', 1, 0),
     ('IV-9-b', 'OPCAT', 'Protocolo Facultativo de la CAT (prevención: visitas a lugares de detención)', 0, 0),
     ('IV-11', 'CRC', 'Convención sobre los Derechos del Niño', 1, 0),
     ('IV-11-b', 'OP-CRC-AC', 'Protocolo Facultativo de la CRC relativo a la participación de niños en los conflictos armados', 0, 0),
     ('IV-11-c', 'OP-CRC-SC', 'Protocolo Facultativo de la CRC relativo a la venta de niños, la prostitución infantil y la pornografía infantil', 0, 0),
     ('IV-11-d', 'OP3-CRC', 'Protocolo Facultativo de la CRC relativo a un procedimiento de comunicaciones', 0, 1),
     ('IV-13', 'ICRMW', 'Convención Internacional sobre la Protección de los Derechos de Todos los Trabajadores Migratorios y de sus Familiares', 1, 0),
     ('IV-15', 'CRPD', 'Convención sobre los Derechos de las Personas con Discapacidad', 1, 0),
     ('IV-15-a', 'OP-CRPD', 'Protocolo Facultativo de la CRPD (comunicaciones individuales e investigaciones)', 0, 1),
     ('IV-16', 'CED', 'Convención Internacional para la Protección de Todas las Personas contra las Desapariciones Forzadas', 1, 0)]
DATE = re.compile(r'^(\d{1,2} [A-Z][a-z]{2} \d{4})\s*([A-Za-z]{0,2})$')
def norm(s): return re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFD', s.lower()).encode('ascii', 'ignore').decode())
def fetch(t):
    mt = t[0]
    u = f'https://treaties.un.org/Pages/ViewDetails.aspx?src=TREATY&mtdsg_no={mt}&chapter=4&clang=_en'
    h = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read().decode('utf-8', 'ignore')
    txt = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'<script.*?</script>|<style.*?</style>', '', h, flags=re.S))))
    m = re.search(r'((?:International|Convention|Optional Protocol|Second Optional Protocol)[^.]{5,170}?) (New York, \d{1,2} \w+ \d{4})(?: \d+)? Entry into force : (\d{1,2} \w+ \d{4})', txt)
    parts = {}
    for r in re.findall(r'<tr[^>]*>(.*?)</tr>', h, re.S):
        c = [re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', x))).strip() for x in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.S)]
        if len(c) != 3 or not c[0] or c[0].strip().lower() in ('participant', 'participants', 'state', 'states'): continue
        nm = re.sub(r'\s*\d+$', '', c[0]).strip()
        f, rt = c[1].strip(), DATE.match(c[2].strip())
        fm = DATE.match(f)
        if (f and not fm) or (c[2].strip() and not rt): continue
        if not f and not c[2].strip(): continue
        if nm in parts: continue   # la tabla de participantes va primero; las notas posteriores no deben pisarla
        parts[nm] = {'firma': fm.group(1) if fm else '', 'parte': rt.group(1) if rt else '', 'forma': (rt.group(2) if rt else '') or ('ratificación' if rt else '')}
    return {'mtdsg': mt, 'siglas': t[1], 'es': t[2], 'basico': bool(t[3]), 'comunicaciones_individuales': bool(t[4]), 'en': m.group(1).strip() if m else '',
            'adoptado': m.group(2).replace('New York, ', '') if m else '', 'en_vigor': m.group(3) if m else '', 'url': u, 'participantes': parts}
def main(fecha):
    with cf.ThreadPoolExecutor(4) as ex: res = list(ex.map(fetch, T))
    OH = json.load(open('data/fuentes/paises_ohchr.json', encoding='utf-8'))['paises']
    byn = {norm(p['en']): p['iso3'] for p in OH}
    ALIAS = {'boliviaplurinationalstateof': 'BOL', 'netherlandskingdomofthe': 'NLD', 'turkiye': 'TUR', 'czechia': 'CZE', 'unitedkingdomofgreatbritainandnorthernireland': 'GBR',
             'palestine': 'PSE', 'stateofpalestine': 'PSE', 'democraticpeoplesrepublicofkorea': 'PRK', 'laopeoplesdemocraticrepublic': 'LAO', 'congo': 'COG',
             'micronesiafederatedstatesof': 'FSM', 'venezuelabolivarianrepublicof': 'VEN', 'iranislamicrepublicof': 'IRN', 'republicofmoldova': 'MDA',
             'unitedrepublicoftanzania': 'TZA', 'syrianarabrepublic': 'SYR', 'russianfederation': 'RUS', 'republicofkorea': 'KOR', 'viet nam': 'VNM', 'vietnam': 'VNM',
             'bahamasthe': 'BHS', 'stkittsandnevis': 'KNA', 'stlucia': 'LCA', 'stvincentandthegrenadines': 'VCT', 'naoero': 'NRU', 'cotedivoire': 'CIV', 'bruneidarussalam': 'BRN', 'eswatini': 'SWZ', 'northmacedonia': 'MKD', 'capeverde': 'CPV', 'caboverde': 'CPV', 'timorleste': 'TLS'}
    iso = lambda n: ALIAS.get(norm(n)) or byn.get(norm(n))
    paises, sin = {}, set()
    for t in res:
        for n, d in t['participantes'].items():
            k = iso(n)
            if not k: sin.add(n); continue
            paises.setdefault(k, {})[t['mtdsg']] = d
        t['participantes'] = len(t['participantes'])
    json.dump({'fuente': 'https://treaties.un.org/Pages/Treaties.aspx?id=4&subid=A&clang=_en', 'consultado': fecha, 'tratados': res, 'paises': paises}, open('data/fuentes/tratados_untc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
    print(len(res), 'instrumentos;', len(paises), 'países con datos; nombres sin emparejar:', sorted(sin))
if __name__ == '__main__': main(sys.argv[1] if len(sys.argv) > 1 else '')
