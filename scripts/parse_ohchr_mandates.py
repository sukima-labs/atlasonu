#!/usr/bin/env python3
"""Convierte el índice oficial de mandatos de OHCHR (spinternet.ohchr.org) en JSON.
Uso: parse_ohchr_mandates.py <html> <TM|CM> <en|es> <salida.json> <fecha_consulta>
Fuente: https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type=TM|CM"""
import re, sys, json, html

def cells(row):
    return [re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', c))).strip()
            for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.S)]

SYM = re.compile(r'((?:E|A|S)/[A-Za-z0-9./()\-]+|\d{4}/\d+[A-Za-z/0-9]*|E/CN\.4/[A-Za-z0-9./()\-]+)')
def split_act(s):
    """'HRC resolution E/CN.4/2002/WP.2' -> (organo, simbolo)"""
    m = SYM.search(s)
    if not m: return s, ''
    return s[:m.start()].strip(), s[m.start():].strip()

def main(path, kind, lang, out, fecha):
    t = open(path, encoding='utf-8', errors='ignore').read()
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', t, re.S)
    recs, cur, mode = [], None, None
    for r in rows:
        c = cells(r)
        if len(c) >= 7 and c[1] and 'Title' not in c[1] and 'Título' not in c[1] and 'Mandate established' not in c[2]:
            title = c[1].split('➥')[0].strip()
            tag = c[1].split('➥')[1].strip() if '➥' in c[1] else ''
            ob, sy = split_act(c[3]); eb, es_ = split_act(c[5])
            holders = c[6]
            cur = {'tipo': 'Temático' if kind == 'TM' else 'País', 'titulo': title, 'etiqueta': tag,
                   'creado_anio': c[2], 'creado_por': ob, 'creado_simbolo': sy,
                   'prorrogado_anio': c[4], 'prorrogado_por': eb, 'prorrogado_simbolo': es_,
                   'titulares_texto': holders, 'observaciones': c[8] if len(c) > 8 else '',
                   'prorrogas_intermedias': [], 'idioma': lang}
            recs.append(cur)
        elif cur and len(c) >= 5 and re.fullmatch(r'\d{4}', c[3] or ''):
            ob, sy = split_act(c[4])
            cur['prorrogas_intermedias'].append({'anio': c[3], 'por': ob, 'simbolo': sy})
    json.dump({'fuente': f'https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type={kind}&lang={lang}',
               'consultado': fecha, 'n': len(recs), 'mandatos': recs}, open(out, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print(kind, lang, len(recs), 'mandatos ->', out)

if __name__ == '__main__':
    main(*sys.argv[1:6])
