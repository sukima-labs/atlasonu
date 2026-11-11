#!/usr/bin/env python3
"""T75 · Texto de cada recomendación del EPU, sacado de los informes del Grupo de Trabajo (ciclos 2 a 4).
Reutiliza seccion(), listas() y contar() de epu_recomendaciones.py: una recomendación es cada punto numerado NNN.M de
«Conclusions and/or recommendations», y un informe solo vale si esa numeración sale completa y seguida.

extraer(texto_en, texto_es=None) devuelve None si contar() no da cifra; si no, una lista con tantos elementos como dice
contar(), en el orden del informe, cada uno {n, en, por, es, revisar}:
  n       «116.1»: el prefijo de la lista y el número, con la errata de prefijo del original corregida igual que contar();
  en      el texto en inglés sin el número, sin saltos de línea de maquetación, sin cabeceras ni pies de página del PDF
          (símbolo GE.xx-xxxxx, número de página, «A/HRC/…» suelto, notas al pie) y sin los Estados del final. Si el punto
          agrupa varias recomendaciones («Ratify … (Senegal); consider … (Honduras)»), los Estados de en medio se quedan
          en el texto, porque dicen quién pidió cada parte;
  por     los Estados que la formularon, en el orden del texto (los de en medio y los del final), tal como vienen
          escritos; None si en el texto no se reconoce ningún paréntesis de Estados (no se adivina);
  es      el mismo punto en español («Conclusiones y/o recomendaciones»), sin los Estados del final; None para TODO el
          informe si no hay texto en español. Si su numeración no sale completa (falta un número o tiene una errata), solo
          llevan español los números que salen en su sitio con el siguiente detrás (así ningún texto se lleva el de otro), y
          ninguno si salen menos del 90 %;
  revisar True si el texto no termina en un paréntesis de Estados (el PDF descolocó palabras al final, falta un
          paréntesis en el original…) o si se rehízo el orden de las columnas del PDF (_reordenar): conviene mirar el documento.
No dice si el Estado la apoyó o tomó nota: el informe no lo escribe de forma inequívoca para cada número (va en párrafos
de introducción o en el adendo), y aquí no se supone. Sin red: solo lee los textos locales.
Uso: epu_recs.py [--dir DIR_TEXTOS] [SÍMBOLO]   (sin símbolo: mide la cobertura sobre los ciclos 2 a 4)"""
import difflib, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import epu_recomendaciones as E  # noqa: E402

# Nombres de Estados que formulan recomendaciones (miembros y observadores de la ONU), con las variantes que usan los
# informes de 2012 a hoy. Solo sirve para reconocer un paréntesis como «de Estados»; el nombre se devuelve tal como viene.
_ESTADOS_EN = """Afghanistan|Albania|Algeria|Andorra|Angola|Antigua and Barbuda|Argentina|Armenia|Australia|Austria|Azerbaijan|
Bahamas|Bahrain|Bangladesh|Barbados|Belarus|Belgium|Belize|Benin|Bhutan|Bolivia|Bolivia (Plurinational State of)|
Plurinational State of Bolivia|Bolivia (Plurinational Republic of)|Bosnia and Herzegovina|Botswana|Brazil|Brunei Darussalam|Brunei|Bulgaria|Burkina Faso|Burundi|
Cabo Verde|Cape Verde|Cambodia|Cameroon|Canada|Central African Republic|Chad|Chile|China|Colombia|Comoros|Congo|
Republic of the Congo|Costa Rica|Côte d'Ivoire|Cote d'Ivoire|Côte d’Ivoire|Croatia|Cuba|Cyprus|Czech Republic|Czechia|
Democratic People's Republic of Korea|Democratic People’s Republic of Korea|Democratic Republic of the Congo|Denmark|Djibouti|
Dominica|Dominican Republic|Ecuador|Egypt|El Salvador|Equatorial Guinea|Eritrea|Estonia|Eswatini|Swaziland|Ethiopia|Fiji|
Finland|France|Gabon|Gambia|Georgia|Germany|Ghana|Greece|Grenada|Guatemala|Guinea|Guinea-Bissau|Guyana|Haiti|Holy See|
Honduras|Hungary|Iceland|India|Indonesia|Iran|Iran (Islamic Republic of)|Islamic Republic of Iran|Iraq|Ireland|Israel|Italy|
Jamaica|Japan|Jordan|Kazakhstan|Kenya|Kiribati|Kuwait|Kyrgyzstan|Kyrgyz Republic|Lao People's Democratic Republic|
Lao People’s Democratic Republic|Latvia|Lebanon|Lesotho|Liberia|Libya|Libyan Arab Jamahiriya|Liechtenstein|Lithuania|
Luxembourg|Madagascar|Malawi|Malaysia|Maldives|Mali|Malta|Marshall Islands|Republic of the Marshall Islands|Mauritania|
Mauritius|Mexico|Micronesia|Micronesia (Federated States of)|Federated States of Micronesia|Monaco|Mongolia|Montenegro|
Morocco|Mozambique|Myanmar|Namibia|Nauru|Nepal|Netherlands|Netherlands (Kingdom of the)|Kingdom of the Netherlands|
New Zealand|Nicaragua|Niger|Nigeria|North Macedonia|Macedonia|The former Yugoslav Republic of Macedonia|Norway|Oman|Pakistan|
Palau|Panama|Papua New Guinea|Paraguay|Peru|Philippines|Poland|Portugal|Qatar|Republic of Korea|Korea|Republic of Moldova|
Moldova|Romania|Russian Federation|Russia|Rwanda|Saint Kitts and Nevis|Saint Lucia|Saint Vincent and the Grenadines|Samoa|
San Marino|Sao Tome and Principe|Saudi Arabia|Senegal|Serbia|Seychelles|Sierra Leone|Singapore|Slovakia|Slovenia|
Solomon Islands|Somalia|South Africa|South Sudan|Spain|Sri Lanka|State of Palestine|Palestine|Sudan|Suriname|Sweden|
Switzerland|Syrian Arab Republic|Syria|Tajikistan|Thailand|Timor-Leste|Togo|Tonga|Trinidad and Tobago|Tunisia|Turkey|
Türkiye|Turkmenistan|Tuvalu|Uganda|Ukraine|United Arab Emirates|United Kingdom of Great Britain and Northern Ireland|
United Kingdom|UK|United Republic of Tanzania|Tanzania|United States of America|United States|USA|Uruguay|Uzbekistan|Vanuatu|
Venezuela|Venezuela (Bolivarian Republic of)|Bolivarian Republic of Venezuela|Viet Nam|Vietnam|Yemen|Zambia|Zimbabwe"""


def _norma(x):
    x = x.replace('’', "'").replace(' ', ' ')
    x = re.sub(r'\s*\(\s*', ' (', x); x = re.sub(r'\s*\)', ')', x)
    x = re.sub(r'\s+', ' ', x).strip().lower()
    return re.sub(r'^the ', '', x)


_CONOCIDOS = {_norma(x) for x in _ESTADOS_EN.replace('\n', '').split('|')}
_LISTA = sorted(_CONOCIDOS)
_CACHE = {}


def es_estado(x):
    """¿Es un nombre de Estado? Exacto o con una errata pequeña del original («United Sates of America», «Holly See»)."""
    k = _norma(x)
    if k not in _CACHE:
        _CACHE[k] = k in _CONOCIDOS or (len(k) >= 6 and not re.search(r'\d', k)
                                         and bool(difflib.get_close_matches(k, _LISTA, n=1, cutoff=0.88)))
    return _CACHE[k]


# Cabeceras y pies de página del PDF: símbolo del documento, número de página («15», «13/19»), código GE.xx-xxxxx,
# código de barras, «Please recycle», «[English only]»
_PAGINA = re.compile(r'(?m)^[ \t]*(?:A/HRC/?[\w./]+|\d{1,3}(?:/\d{1,3})?|GE\.\d{2}-\d{4,6}(?:[ \t]*\([A-Z]\))?|\*\d{6,8}\*'
                     r'|Please recycle|\[?(?:English|Spanish|French|Inglés|Español) only\]?|\[?(?:Solo en|Únicamente en) \w+\]?)[ \t]*$')
_NOTA_EDITADO = re.compile(r'(?im)(?:^|[*\uf02a∗]+)[ \t]*(?:the )?(?:conclusions and(?:/or)? recommendations|las conclusiones y(?:/o)? recomendaciones)'
                           r'[^.]{0,60}?(?:not been edited|will not be edited|no han sido editadas|no se han editado|no fueron editadas|no (?:han sido|fueron|serán|han de ser) objeto de (?:revisión|edición) editorial|no se han revisado)\.?')
# párrafo siguiente («117. The following recommendations…», «139.»): corta la última recomendación de cada lista
_PARRAFO = re.compile(r'(?m)^[ \t]*(\d{2,3})\.(?!\d)[ \t]*(?=$|[A-ZÁÉÍÓÚÑ«“"])')
# llamada de nota pegada al texto: «(Tobago);1» al final de línea, «(Canada)4;» (no «131.47», que es un número de recomendación)
_LLAMADA = re.compile(r'(?m)(?<![\d][.,])(?<=[);.,a-z’”])(\d{1,2})(?=[ \t]*$)|(?<=\))(\d{1,2})(?=[;.,])')
_ASTERISCOS = re.compile(r'[*\uf02a∗]+')


def seccion_es(t):
    """Como E.seccion() pero en el texto en español: entre «Conclusiones y/o recomendaciones» y el párrafo final."""
    m = re.search(r'(?im)^[ \t]*(?:[IVX]+\.[ \t]*)?conclusiones y(?:/o)? recomendaciones[^\w\n.…]*$', t)   # el título del índice lleva puntos y no casa
    if not m: return None
    fin = re.search(r'(?i)todas las conclusiones y(?:/o)? recomendaciones (?:que figuran|contenidas|formuladas|recogidas)', t[m.end():])
    return t[m.end():m.end() + fin.start()] if fin else t[m.end():]


_PIE = re.compile(r'\d{1,3}(?:/\d{1,3})?|A/HRC/?[\w./]+|GE\.\d{2}-\d+.*|\*\d{6,8}\*')


def _quitar_notas(s, llamadas):
    """Quita los cuerpos de las notas al pie: desde una línea que es solo la llamada («1») hasta el número de página.
    Solo si esa llamada aparece pegada a una línea del texto: un número suelto cualquiera no se toca."""
    lineas, out, i = s.split('\n'), [], 0
    while i < len(lineas):
        l = lineas[i].strip()
        m = re.fullmatch(r'(\d{1,2})(?:[ \t]+\S.*)?', l)
        previa = next((x.strip() for x in reversed(out) if x.strip()), '')
        # la nota va después de un texto que ya cerró («…(Cuba);»), nunca justo tras el número de la recomendación
        if re.fullmatch(r'_{5,}', l):
            # la raya «_____» abre las notas al pie; pdftotext mezcla su texto con el pie de página y la cabecera de la
            # página siguiente, así que se quita hasta la última línea de pie o cabecera de las 14 siguientes (o hasta el final)
            pies = [j for j in range(i + 1, min(i + 15, len(lineas))) if _PIE.fullmatch(lineas[j].strip())]
            if pies: i = pies[-1] + 1; continue
            if len(lineas) - i <= 15: break
        if (previa[-1:] in (';', '.', ')', '”', ':') and ((m and m[1] in llamadas) or _ASTERISCOS.fullmatch(l))):
            j = i + 1
            while j < len(lineas) and j - i <= 40 and not _PIE.fullmatch(lineas[j].strip()):
                j += 1
            if j < len(lineas) and j - i <= 40 and j > i + 1:
                i = j; continue
        out.append(lineas[i]); i += 1
    return '\n'.join(out)


# cuerpo de nota al pie que copia la recomendación tal como se leyó en el diálogo («The recommendation as read during the
# interactive dialogue was: …», «La recomendación formulada durante el diálogo interactivo fue…»), con las llamadas sueltas
# que la preceden; llega hasta el pie de página (número, «A/HRC/…», «GE.…») o el final del trozo
_NOTA_DIALOGO = re.compile(r'(?ms)(?:^[ \t]*\d{1,2}[ \t]*\n\s*)*^[ \t]*(?:\d{1,2}[ \t]+)?(?:(?:The|La|Las) [Rr]|R)(?:ecommendations?|ecomendaci(?:ón|ones))\b'   # con mayúscula: no una línea partida de la recomendación
                           r'(?![^\n]*(?:below|examined|enjoy|a continuación|examinad|cuentan con|contaron con))'   # ni la frase que abre una lista
                           r'[^\n]{0,60}?(?:interactive dialogue|during the dialogue|diálogo interactivo|durante el diálogo|en el diálogo)'
                           r'.*?(?=^[ \t]*(?:\d{1,3}(?:/\d{1,3})?|A/HRC/[\w./]+|GE\.\d{2}-\d+.*)[ \t]*$|\Z)')


def _reordenar(s):
    """Recomendación que pdftotext sacó en desorden por las columnas del PDF: la línea que cierra con el paréntesis de los Estados
    no es la última y detrás quedan trozos sueltos del texto («Continue implementing / framework, 2023–2037 (Cuba); / the /
    national / development / planning», «(Iraq); / Review legislation…», «Leste); / Strengthen the measures… (Timor-»). Se pone
    esa línea al final: lo de antes + lo de detrás + la línea del paréntesis. Si lo de detrás es una frase cerrada («On 5 May 2017,
    … withdrawn by the delegation of Qatar.», «request of the Independent Expert … gender identity.”»), es el cuerpo de una nota al
    pie partida por el salto de página y se quita. Si no está claro, el texto queda tal cual (y con «revisar»)."""
    L = [l.strip() for l in s.split('\n') if l.strip()]
    if len(L) < 2 or re.search(r'\)[ \t]*[;.,]?$', L[-1]): return s
    i = next((k for k in range(len(L) - 2, -1, -1) if re.search(r'\)[ \t]*[;.,]?$', L[k])), None)
    if i is None: return s
    cola = ' '.join(L[i + 1:])
    abre = cola.count('(') - cola.count(')')
    partido = abre > 0 and L[i].count(')') - L[i].count('(') == abre   # «(Timor-» … «Leste);»: el Estado se partió en dos líneas
    if not partido and ('(' in cola or ')' in cola): return s
    if not partido and re.search(r'[.”"]$', cola) and len(cola) > 25:
        return '\n'.join(L[:i + 1])   # cuerpo de una nota al pie
    solo_estado = i == 0 and (L[0].startswith('(') or '(' not in L[0])   # «(Iraq);» o «Leste);» delante de todo el texto
    if not (partido or solo_estado or re.match(r'[a-z]', cola)): return s   # «(Senegal);\nConsider…»: otra parte del punto
    return '\n'.join(L[:i] + L[i + 1:] + [L[i]])


def _limpiar(s, llamadas, reordenar=True):
    s = s.replace('\f', '\n')
    s = _NOTA_DIALOGO.sub('', s)
    s = _quitar_notas(s, llamadas)
    s = _NOTA_EDITADO.sub('', s)
    s = _PAGINA.sub('', s)
    if llamadas:
        alt = '|'.join(sorted(llamadas, key=len, reverse=True))
        s = re.sub(r'(?m)(?<![\d][.,])(?<=[);.,a-z’”])(?:' + alt + r')(?=[ \t]*$)|(?<=\))(?:' + alt + r')(?=[;.,])', '', s)
    s = re.sub(r'(?m)(?<=\))[ \t]+\d{1,2}(?=[ \t]*[;.,]?[ \t]*$)', '', s)   # «(México) 1;»: llamada de nota separada
    s = _ASTERISCOS.sub(lambda m: '' if len(m[0]) > 1 or m[0] != '*' else m[0], s)   # «**», «∗∗»: marcas de nota
    s = re.sub(r'[ \t]*\n[ \t]*', '\n', s.strip())
    if reordenar: s = _reordenar(s)
    s = re.sub(r'(?<=\w)-\n(?=\w)', '-', s)     # «health-\ncare»: el guion es del original
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'\(\s+', '(', s); s = re.sub(r'\s+\)', ')', s)
    return s.strip()


def _trozos(s):
    """[(n, texto limpio, dudoso)] por recomendación, en el orden de listas(); None si la numeración no es completa y seguida."""
    ls, saltos = E.listas(s)
    if not ls or saltos: return None
    return _cortar(s, [(pre, k, p) for pre, _, ks in ls for k, p in ks], ls[0][0])   # p: dónde empieza el número «116.1»


def _trozos_parcial(s, orden):
    """Para el español cuando su numeración no sale completa (falta un número, una errata): {n: (texto, dudoso)} solo de los
    números de `orden` (los del inglés) que salen en su sitio y cuyo siguiente número del inglés también sale justo detrás, para que
    ningún texto se lleve el de una recomendación perdida. None si salen menos del 90 % (el texto no se parece lo bastante)."""
    idx, pos, ult, todos = {n: i for i, n in enumerate(orden)}, [], -1, []
    for m in re.finditer(r'(?m)(?:^|(?<=;))[ \t]*(\d{2,3})\.(\d{1,3})\.?(?=[ \t]|$)', s):
        i = idx.get(f'{m[1]}.{m[2]}')
        todos.append(m.start(1))
        if i is not None and i > ult: pos.append((int(m[1]), int(m[2]), m.start(1))); ult = i
    if not pos or len(pos) < 0.9 * len(orden): return None
    tr = _cortar(s, pos, pos[0][0])
    out = {}
    for j, (n, t, dudoso) in enumerate(tr):
        sig = tr[j + 1][0] if j + 1 < len(tr) else None
        otro = next((x for x in todos if x > pos[j][2]), None)   # entre los dos no puede haber otro número suelto
        if sig is None and n == orden[-1] and otro is None: out[n] = (t, dudoso)
        elif sig is not None and idx[sig] == idx[n] + 1 and otro == pos[j + 1][2]: out[n] = (t, dudoso)
    return out


def _cortar(s, pos, primero):
    llamadas = {a or b for a, b in _LLAMADA.findall(s)}
    out = []
    for i, (pre, k, p) in enumerate(pos):
        ini = re.compile(r'\d{2,3}\.\d{1,3}\.?').match(s, p).end()
        fin = pos[i + 1][2] if i + 1 < len(pos) else len(s)
        t = s[ini:fin]
        dudoso = False
        for p in _PARRAFO.finditer(t):
            if primero - 1 <= int(p[1]) <= primero + 8:
                if t[:p.start()].strip():
                    t = t[:p.start()]
                else:   # «113.7 / 114. / Extend a standing invitation… (Hungary). / Congo considers…»: el PDF puso el
                    # número del párrafo siguiente antes del texto; se toma hasta el primer «(…).» de final de línea
                    resto = t[p.end():]
                    c = re.search(r'\)[ \t]*[.;]?[ \t]*$', resto, re.M)
                    t, dudoso = (resto[:c.end()] if c else ''), True
                break
        limpio = _limpiar(t, llamadas)
        out.append((f'{pre}.{k}', limpio, dudoso or limpio != _limpiar(t, llamadas, False)))   # reordenado: se avisa igual
    return out


def _grupos(t):
    """[(inicio, fin, contenido)] de los paréntesis de primer nivel, respetando los anidados («(Venezuela (Bolivarian Republic of))»)."""
    out, prof, ini = [], 0, None
    for i, c in enumerate(t):
        if c == '(':
            if prof == 0: ini = i
            prof += 1
        elif c == ')' and prof:
            prof -= 1
            if prof == 0: out.append((ini, i + 1, t[ini + 1:i]))
    return out


def _nombres(g):
    """«Brazil; Chile», «Brazil, Chile and Peru» → nombres, sin partir los paréntesis («Bolivia (Plurinational State of)»)."""
    out, prof, cur = [], 0, ''
    for c in g:
        if c == '(': prof += 1
        elif c == ')': prof -= 1
        if c in ';,' and prof == 0: out.append(cur); cur = ''
        else: cur += c
    out.append(cur)
    res = []
    for x in out:
        x = re.sub(r'^(?:and|y)\s+', '', x.strip())
        x = re.sub(r'\s+\d$', '', x)            # llamada de nota: «Denmark 2»
        if x: res.append(x)
    # «Namibia and Togo»: se parte por «and» solo si cada lado es un Estado y el conjunto no lo es («Trinidad and Tobago»)
    final = []
    for x in res:
        partes = re.split(r'\s+and\s+', x)
        if len(partes) > 1 and not es_estado(x) and all(es_estado(p) for p in partes): final += partes
        else: final.append(x)
    return final


def _de_estados(g):
    ns = _nombres(g)
    return ns if ns and all(es_estado(x) for x in ns) else None


def _separar(t):
    """(texto sin los Estados del final, Estados en orden o None, nº de paréntesis de Estados quitados del final, ¿termina limpio?)."""
    gs, por, fin_txt, quitados = _grupos(t), [], len(t), 0
    cola = re.compile(r'[\s;.,:]*$')
    # paréntesis del final («(Holy See) (Italy).»): de atrás adelante mientras solo haya separadores detrás
    j = len(gs) - 1
    while j >= 0 and cola.fullmatch(t[gs[j][1]:fin_txt]) and _de_estados(gs[j][2]):
        fin_txt = gs[j][0]; quitados += 1; j -= 1
    finales = [x for a, b, g in gs[j + 1:] for x in _de_estados(g)]
    for a, b, g in gs[:j + 1]:
        ns = _de_estados(g)
        if ns: por += ns
    por += finales
    por = list(dict.fromkeys(por))   # «Ratify the ICESCR (Romania, … Poland, …) / … (Poland)»: cada Estado una vez
    cuerpo = re.sub(r'[\s;,]+$', '', t[:fin_txt]).rstrip()
    if not quitados:   # «(Peru); 6»: llamada de nota suelta al final, tras el paréntesis
        t2 = re.sub(r'(?<=[;.)])\s+\d{1,2}$', '', t)
        if t2 != t: return _separar(t2)
    cuerpo = re.sub(r'\s+(?:and|y)$', '', cuerpo)
    return cuerpo, (por or None), quitados, quitados > 0


def _quitar_finales(t, k, nombres=None):
    """Quita del final del texto en español los k últimos paréntesis (los mismos que eran Estados en inglés) o, con
    `nombres`, los paréntesis del final cuyos nombres están todos en ese conjunto. Devuelve (texto, contenidos quitados)."""
    quitados = []
    while k is None or len(quitados) < k:
        t2 = re.sub(r'[\s;.,]+$', '', t)
        gs = _grupos(t2)
        if not gs or gs[-1][1] != len(t2): break
        if nombres is not None and not all(_norma(x) in nombres for x in _nombres(gs[-1][2]) or ['']): break
        quitados.insert(0, gs[-1][2]); t = t2[:gs[-1][0]].rstrip()
    if quitados: t = re.sub(r'\s+(?:y|e)$', '', re.sub(r'[\s;,]+$', '', t))
    return t, quitados


def extraer(texto_en, texto_es=None):
    if E.contar(texto_en)[0] is None: return None
    tr = _trozos(E.seccion(texto_en))
    if tr is None: return None
    res, quit = [], []
    for n, t, dudoso in tr:
        cuerpo, por, k, limpio = _separar(t)
        res.append({'n': n, 'en': cuerpo, 'por': por, 'es': None, 'revisar': dudoso or not limpio})
        quit.append(k)
    if texto_es:
        s = seccion_es(texto_es)
        tes = _trozos(s) if s else None
        if s and not (tes and [x[0] for x in tes] == [r['n'] for r in res]):   # numeración incompleta: solo los números seguros
            par = _trozos_parcial(s, [r['n'] for r in res])
            tes = [(r['n'],) + par[r['n']] if par and r['n'] in par else (r['n'], None, False) for r in res] if par else None
        if tes and [x[0] for x in tes] == [r['n'] for r in res]:
            nombres_es = set()   # cómo escribe este informe en español los Estados que en inglés se reconocieron
            for r, k, (_, t, _) in zip(res, quit, tes):
                if k and t is not None:
                    r['es'], q = _quitar_finales(t, k)
                    nombres_es |= {_norma(x) for g in q for x in _nombres(g)}
            for r, k, (_, t, _) in zip(res, quit, tes):
                if not k and t is not None: r['es'] = _quitar_finales(t, None, nombres_es)[0]
    return res


def main():
    d = E.DIR
    args = sys.argv[1:]
    if '--dir' in args:
        i = args.index('--dir'); d = args[i + 1]; del args[i:i + 2]
    leer = lambda p: open(p, encoding='utf-8', errors='ignore').read() if os.path.exists(p) else None
    if args:
        sl = E.slug(args[0])
        print(json.dumps(extraer(leer(os.path.join(d, 'txt', f'{sl}-en.txt')) or '', leer(os.path.join(d, 'txt', f'{sl}-es.txt'))),
                         ensure_ascii=False, indent=1))
        return
    inf = json.load(open(os.path.join(E.RAIZ, 'data/fuentes/epu_informes.json'), encoding='utf-8'))
    c = dict(informes=0, sin_texto=0, con_lista=0, recs=0, con_es=0, es_alineado=0, revisar=0, sin_por=0)
    for iso, lista in sorted(inf['paises'].items()):
        for f in lista:
            if E.ciclo(f['d']) == 1: continue
            c['informes'] += 1
            sl = E.slug(f['s'])
            te, ts = leer(os.path.join(d, 'txt', f'{sl}-en.txt')), leer(os.path.join(d, 'txt', f'{sl}-es.txt'))
            if te is None: c['sin_texto'] += 1; continue
            r = extraer(te, ts)
            if r is None: continue
            c['con_lista'] += 1; c['recs'] += len(r)
            c['con_es'] += ts is not None
            c['es_alineado'] += bool(r) and r[0]['es'] is not None
            c['revisar'] += sum(x['revisar'] for x in r); c['sin_por'] += sum(x['por'] is None for x in r)
    print(json.dumps(c, ensure_ascii=False))


if __name__ == '__main__': main()
