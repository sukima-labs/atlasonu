#!/usr/bin/env python3
"""T75 · Qué respondió el Estado a cada recomendación del Examen Periódico Universal: «apoyada» o «tomó nota».
Se lee de dos sitios, y solo lo que está escrito de forma inequívoca para ESE número:
  1. El informe del Grupo de Trabajo (A/HRC/<sesión>/<n>): cada lista numerada de «Conclusions and/or recommendations» va
     precedida de una frase («… have been examined by X and enjoy the support of X:», «… have been noted by X:», «… did not enjoy
     the support of X:», «… will be examined by X, which will provide responses …:»). Cada número toma la respuesta de su lista.
  2. El adendo (…/Add.1), para las que «se examinarán»: listas con números («X supports the following recommendations: 116.1,
     116.5 and 116.30», «Accepted: 125.6, 125.8 …», «Recommendations 115.1–115.20 are supported») o tablas (número y, en la línea
     siguiente, «Supported» / «Noted» / «Rejected» …).
«Accepted»/«Supported»/«enjoy the support» -> apoyada; «Noted»/«takes note»/«Not supported»/«Rejected»/«did not enjoy» -> tomó nota.
«Partially supported»/«accepted in part» -> null (no se fuerza). Un número con dos respuestas distintas -> null. Texto libre sin
números, números sin prefijo («1, 2, 3») o una frase que no dice cuál es la respuesta -> null. Nada se deduce por el tema.
Mejor null que un dato falso: el que lo muestre enlaza el documento donde está la respuesta.
Uso: epu_respuestas.py [--dir DIR_TEXTOS] [--auditoria FICHERO.json]   (mide la cobertura sobre los ciclos 2 a 4; no escribe datos)"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import epu_recomendaciones as R  # noqa: E402

APOYADA, NOTA = 'apoyada', 'tomó nota'
_PARCIAL = re.compile(r'\bpartial\w*|\bin part\b|\bpartly\b|\bAIP\b|\b(?:first|second|third|fourth|other|one|some|certain)\s+parts?\b|\bin principle\b'
                      r'|\b(?:accept|support)\w*,?\s+in\s+respect\s+of\b|\bonly\s+in\s+respect\s+of\b|\bto\s+the\s+extent\b|\binsofar\b'
                      r'|\bthe\s+notion\b', re.I)   # «noted only in respect of the phrase…», «cannot accept …, to the extent that…»   # «138.32 is accepted in respect of the continuation of…»
# lo negativo va primero y se come su frase entera: «did not enjoy the support» no debe dejar suelto «the support»
_NEG = re.compile(r'''(?ix)
    (?:\b(?:not|cannot|can\s?not|unable\s+to|fail(?:s|ed)?\s+to)|n[’']t)\s+(?:\w+\s+){0,3}?(?:accept\w*|support\w*|approv\w*|enjoy\w*(?:\s+\S+){0,2}?\s+support\b|enjoy\w*)
  | \bnot\s+in\s+a\s+position\s+to\s+(?:accept|support)\w*
  | \breject\w*
  | \bt(?:ake|akes|aken|aking|ook)\s+(?:\w+\s+){0,2}?note\b
  | \bnote\s+(?:has|have)\s+been\s+taken\b
  | \b(?:we|I)\s+(?:\w+\s+)?note\s+(?=(?:the\s+)?(?:following|recommendations?|\d))
  | \bnoted\b | \bnotes\s+(?:the\s+)?(?=following|\d|recommendation|remaining)
  | \bwill\s+not\s+be\s+considered\b''')
_POS = re.compile(r'(?i)\baccept\w*|\bsupport\w*|\benjoy\w*\s+(?:the|its)\s+support|\bapproved\b')
_PEND = re.compile(r'(?i)will\s+(?:be\s+(?:further\s+)?examined|examine|provide\s+(?:its\s+)?respon|respond|be\s+included)|respon\w+\s+will\s+be\s+provided')


def clase(x):
    """'apoyada', 'tomó nota', 'parcial', 'mixta' (dice las dos cosas) o None (no dice qué)."""
    if _PARCIAL.search(x): return 'parcial'
    neg = bool(_NEG.search(x))
    pos = bool(_POS.search(_NEG.sub(' ', x)))
    if neg and pos: return 'mixta'
    return NOTA if neg else APOYADA if pos else None


def _limpia(x): return re.sub(r'\s+', ' ', x).strip()


_LISTA_SIGUE = re.compile(r'(?i)\bfollowing\b|\bbelow\b|\bas follows\b|\blisted\b')


def clase_cabecera(cl):
    """Como clase(), pero en una cabecera que dice las dos cosas y solo una presenta la lista que sigue («Colombia accepts 223 and,
    therefore, takes note of the following eight recommendations», «ACCEPTS 7 … and NOTES the 9 that are listed as follows»):
    vale la de la última parte, si solo esa habla de «the following» / «below» / «as follows»."""
    c = clase(cl)
    if c != 'mixta': return c
    partes = re.split(r'(?i),?\s+and\s*,?\s+|;\s*', cl)
    if len(partes) < 2 or not _LISTA_SIGUE.search(partes[-1]) or any(_LISTA_SIGUE.search(x) for x in partes[:-1]): return c
    u = clase(partes[-1])
    return u if u in (APOYADA, NOTA) else c


def del_informe(texto):
    """{número: 'apoyada' | 'tomó nota' | 'pendiente' | None} según la frase que introduce cada lista del informe."""
    s = R.seccion(texto)
    if s is None: return {}
    ls, _ = R.listas(s)
    salida = {}
    for pre, ini, ks in ls:
        cab = list(re.finditer(r'(?m)^[ \t]*' + str(pre) + r'\.(?!\d)', s[:ini]))   # «138.» puede ir solo en su línea
        frase = _limpia(s[cab[-1].end():ini]) if cab else ''
        if not frase or len(frase) > 900 or re.search(r'\b\d{2,3}\.\d{1,3}\b', frase):
            c = None   # la frase no está donde debe (PDF con columnas desordenadas): no se sabe
        elif _PEND.search(frase):
            c = 'pendiente'
        else:
            c = clase(frase)
            if c not in (APOYADA, NOTA): c = None   # «X considers that … are already implemented» no dice «support»
        for k, _ in ks: salida[f'{pre}.{k}'] = c
    return salida


# --- adendo -------------------------------------------------------------------------------------------------------------
_NUM = re.compile(r'(?<![\d.,/])(\d{2,3})\.(\d{1,3})(?![\d]|\.\d)')
_CONT = re.compile(r'[ \t]*(?:(,)|[-–—‑]|\bto\b)[ \t]*(\d{1,3})(?![\d]|\.\d)')                # 117.84, 85, 86 · 80.15–16
# entre números de una misma lista; el salto de línea a secas solo une si el número va solo en su línea (en una tabla,
# «140.230–140.261\n140.262 The recommendation is supported» son dos celdas distintas)
_SEP = re.compile(r'^\s*(?:(?:[,;&]|\band\b|\bor\b|\([^()\n]{0,60}\))\s*)+$', re.I)
_RANGO = re.compile(r'^\s*(?:[-–—‑]|\bto\b|\bthrough\b|\buntil\b)\s*$', re.I)                    # 116.1–116.20, 116.1 to 116.20
_FIN_CLAUSULA = re.compile(r'[.;:!?](?=\s|$)|\n[ \t]*\n|\n[ \t]*\(?[a-z]{1,3}[.)]?[ \t]*\n')
_PASADO = re.compile(r'(?i)\b(?:previously|initially|earlier|formerly|first cycle|second cycle|third cycle|previous (?:cycle|review))\b')
# después del número, solo valen etiquetas en participio o tercera persona («Supported», «accepts the recommendation»): el texto de
# la recomendación copiado en una tabla empieza por un imperativo («Support…», «Accept…») y no es una respuesta
_POS_ESTRICTO = re.compile(r'(?i)\b(?:accepted|supported|accepts|supports|enjoys?\s+(?:the|its)\s+support)\b')


def _solo_en_linea(a, ini, fin):
    """¿El número va solo en su línea («133.1\\n133.6\\n133.7»)? Entonces es una lista en columna; si detrás va texto
    («140.262 The recommendation is supported»), empieza otra fila."""
    return not a[fin:a.find('\n', fin) if '\n' in a[fin:] else len(a)].strip(' \t.,;')


def _corridas(a, validos):
    """Grupos de números seguidos (una lista «116.1, 116.5 and 116.30», un rango «116.1–116.20» o «80.15–16», «117.84, 85, 86»)
    en el texto del adendo: [(ini, fin, [nums])]. Solo cuentan los números de `validos` (los del informe)."""
    toks = []
    for m in _NUM.finditer(a):
        p, k = int(m[1]), int(m[2])
        if f'{p}.{k}' not in validos: continue
        nums, fin = [f'{p}.{k}'], m.end()
        while True:   # continuación sin prefijo, solo si es creciente y existe
            c = _CONT.match(a, fin)
            if not c: break
            k2 = int(c[2])
            if k2 <= k or f'{p}.{k2}' not in validos: break
            if c[1]: nums.append(f'{p}.{k2}')
            elif all(f'{p}.{j}' in validos for j in range(k + 1, k2 + 1)): nums.extend(f'{p}.{j}' for j in range(k + 1, k2 + 1))
            else: break
            k, fin = k2, c.end()
        toks.append((m.start(), fin, nums))
    out, expl, ult = [], [], 0   # expl: la corrida se unió con separadores escritos («;», «,», «and»); ult: dónde empieza su último número
    for ini, fin, nums in toks:
        if out:
            i0, f0, ns0 = out[-1]
            gap = a[f0:ini]
            if _RANGO.match(gap) and ns0 is not None:
                p0, k0 = map(int, ns0[-1].split('.'))
                p1, k1 = map(int, nums[0].split('.'))
                if p0 == p1 and k0 < k1 and all(f'{p0}.{k}' in validos for k in range(k0, k1 + 1)):
                    out[-1] = (i0, fin, ns0 + [f'{p0}.{k}' for k in range(k0 + 1, k1)] + nums); continue
                out[-1] = (i0, f0, None)   # rango raro: la corrida no vale
            elif _SEP.match(gap) or (not gap.strip() and ('\n' not in gap or (
                    _solo_en_linea(a, ini, fin) and not expl[-1]
                    and (gap.count('\n') == 1 or not a[a.rfind('\n', 0, ult) + 1:ult].strip())))):
                # una lista que separa con «;» y acaba la línea sin él («134.104; 134.105\n134.106»): lo de abajo es otra fila;
                # tras una línea en blanco solo sigue una columna de números sueltos, no «See 186.1\n\n186.14.»
                out[-1] = (i0, fin, ns0 + nums if ns0 is not None else None); expl[-1] = expl[-1] or bool(gap.strip()); ult = ini
                continue
        out.append((ini, fin, nums)); expl.append(False); ult = ini
    return [c for c in out if c[2]]


def _clausulas(x):
    """[(cláusula, signo que la cierra)], sin las vacías ni los ordinales sueltos («(a)», «4.»)."""
    out, i = [], 0
    for m in list(_FIN_CLAUSULA.finditer(x)) + [None]:
        c = re.sub(r'^[•▪◦·●]\s*', '', _limpia(x[i:m.start()] if m else x[i:]))   # «• 149.127»: la viñeta no es una cláusula
        if c and not re.fullmatch(r'\(?[a-zA-Z]{1,3}[.)]?|\d+\.?', c): out.append((c, m[0].strip() if m else ''))
        if m: i = m.end()
    return out


_PUENTE = re.compile(r'(?i)^(?:\(?\w{1,3}[.)]\s*)?(?:these |the following |the |of )?recommendations?(?: (?:are|is|include|nos?\.?|numbers?))?[ (]*$')


def _cabecera(cl, cierre, fuerte=False):
    """¿La cláusula presenta la lista que va detrás? Sí si acaba en «:», si es una etiqueta corta («(a) Accepted»), si termina en
    «recommendation(s)» («The Philippines notes recommendation 131.12») o habla de «the following». No si habla de la anterior
    («The recommendation is therefore irrelevant and is rejected.» y, en la línea siguiente, la recomendación 124.3)."""
    if re.search(r'(?i)\b(?:this|that|said|the)\s+recommendation\b(?!s)', cl) and not re.search(r'(?i)\bfollowing\b|recommendations?$', cl):
        return False
    if cierre == '.' and re.search(r'(?i)\b(?:this|that|said|the)\s+recommendation$', cl):
        return False   # «108.8 / Seychelles accepts the recommendation.»: es la respuesta de la fila de antes, no la cabecera de la siguiente
    cl = re.sub(r'\s*\(\d+\)$', '', cl)   # «Recommendations accepted by the Government (22)»: el recuento no cuenta
    if re.match(r'(?:(?:[IVX]+|[A-Z]|\d+)\.\s*)?(?:Recommendations?|RECOMMENDATIONS?)\b', cl) and len(cl) <= 120: return True
    return cierre == ':' or (len(cl) <= 40 and not fuerte) or bool(re.search(r'(?i)recommendations?(?: nos?\.?| numbers?)?$|\bfollowing\b', cl))


def _antes(a, desde, ini, fuerte=False):
    """Respuesta que da la cabecera inmediatamente anterior a la lista («X supports the following recommendations:», «(a) Accepted.»)."""
    cls = _clausulas(a[max(desde, ini - 600):ini])
    for j in range(len(cls) - 1, max(-1, len(cls) - 4), -1):
        cl, cierre = cls[j]
        if _PASADO.search(cl): return None
        c = clase_cabecera(cl) if _cabecera(cl, cierre, fuerte) else None
        if c:
            if j == 0 and desde and ini - desde <= 600 and not _cabecera(cl, cierre, True):
                w = a[desde:ini]
                antes = w[:w.find(cl.split()[0])] if cl.split()[0] in w else w
                if re.fullmatch(r'[\s.,;:–—\-]*', antes) and not re.fullmatch(r'\s*[.;][ \t]*\n[ \t]*\n\s*', antes):
                    # (salvo si la lista de antes se cerró con «.» y una línea en blanco: «….\n\nNoted\n133.8, …»)
                    return None   # «116.5; Noted 116.6; …»: una etiqueta pegada a dos listas puede ser de la de antes o de la de después
                    # (con «(b) Noted.» o un número de párrafo delante, es la cabecera de la siguiente)
            if j and len(cls[j - 1][0]) <= 40 and clase(cls[j - 1][0]) in (APOYADA, NOTA) and clase(cls[j - 1][0]) != c:
                return 'mixta'   # dos columnas seguidas: «Recommendations Supported» «Recommendations Noted» y luego los números
            return c
        if not _PUENTE.match(cl): return None   # solo se salta un puente vacío («These recommendations are:», «(a) Recommendations»)
    return None


def _despues_verbo(a, fin):
    """«… and 116.30 are supported.» / «Recommendation 125.74 is not accepted.» / «145.1, 146.27 accepted as implemented:»: verbo
    o participio en minúscula justo detrás del número."""
    m = re.match(r'[ \t]*,?[ \t]*\n?[ \t]*((?:are|is|were|was|have|has|enjoy|enjoys|will|shall|cannot|can|do|does|accepted|supported|noted|rejected|not)\b[^.;:\n]{0,80})', a[fin:fin + 160])
    if not m or _PASADO.search(m[1]): return None
    return clase(m[1])


_TITULO = re.compile(r'(?m)^[ \t]*(?:(?:[IVX]+|[A-Z]|\d+)\.[ \t]*)?(?:Recommendations?|RECOMMENDATIONS?|Responses?)\b[^.:;\d\n]{0,90}(?:\(\d+\))?[ \t]*$')


def _titulos(a):
    """[(pos, respuesta)] de los títulos de apartado («Recommendations that are accepted», «III. Recommendations noted by …»): una
    línea corta, en mayúscula, sin cifras, después de un punto o de una línea en blanco y sin frase que siga en minúscula."""
    out = []
    for m in _TITULO.finditer(a):
        antes = a[:m.start()].rstrip(' \t')
        if antes and not antes.endswith('\n'): continue
        ult = antes.rstrip().rsplit('\n', 1)[-1].strip() if antes.strip() else ''
        blanco = antes.endswith('\n\n') or antes.rstrip(' \t').endswith('\n\n')
        if not (blanco or not ult or re.search(r'[.:;]$|^(?:[IVX]+|[A-Z]|\d+)\.?$|^\(?\w{1,3}\)$', ult)): continue
        sig = a[m.end():m.end() + 80].lstrip('\n \t')
        if re.match(r'[a-z]', sig): continue
        out.append((m.end(), clase(m[0])))
    # un subtítulo temático («Scope of international obligations») corta la herencia: debajo puede ir otra cosa
    for m in re.finditer(r'(?m)(?:\A|\n[ \t]*\n|[.:;][ \t]*\n)[ \t]*([A-Z][^\d.:;()\n]{2,60})[ \t]*\n(?=[ \t]*[A-Z\d(])', a):
        if not _TITULO.match(m[1]): out.append((m.end(1), None))
    return sorted(out)


def _despues_etiqueta(a, fin, hasta):
    """La etiqueta que sigue al número en una fila de tabla («157.1 Rejected», «132.210 Congo Noted», «40.261: Supported.»,
    «112.82. Seychelles accepts the recommendation.»). No vale si entre el número y la etiqueta hay otra cosa que nombres de país
    o el texto de la recomendación (sin cifras, sin «(b)»), ni si la frase es la cabecera de otra lista («…following…:»)."""
    g = a[fin:hasta]
    g = re.sub(r'^[\s.:;,–—\-]+', '', g)   # «134.99;\n\nSupported»: el «;» que cierra la celda no es texto
    if re.match(r'(?:[IVX]+|[A-Z])\.[ \t]*\n', g): return None   # «… and 43.353.\nB.\nPartially supported recommendations»: otro apartado
    lineas = [l for l in g.split('\n') if l.strip() and not re.fullmatch(r'[ \t]*\d{1,3}\.[ \t]*', l)]   # «94.1.\n3.\nAccepted.»: número de párrafo
    for k, l in enumerate(lineas[:3]):   # «127.1 / Djibouti / Accepted»: la celda del país puede ir antes
        lin = _etiqueta_linea(l)
        if lin:   # «104.52 … 104.57 / Noted / Noted / Accepted»: varias etiquetas seguidas y distintas no se reparten
            if k + 1 < len(lineas) and _etiqueta_linea(lineas[k + 1]) not in (None, lin): return 'mixta'
            return lin
        if re.search(r'[\d.:;]', l) or len(l.strip()) > 80 or clase(l): break   # solo se salta el nombre de un país
    m = _FIN_CLAUSULA.search(g)
    cl, cierre = (g[:m.start()], g[m.start():m.end()]) if m else (g, '')
    if cl.strip() and _PARCIAL.search(cl) and len(cl) <= 80: return 'parcial'   # «109.51 – Partially accepted: This recommendation…»
    if not cl.strip() or re.search(r'(?i)following|recommendations\b', cl): return None
    if cierre.startswith(':') and not re.fullmatch(r'(?i)\s*(?:is\s+|are\s+)?(?:accepted|supported|noted)(?:\s+as\s+implemented)?\s*', cl):
        return None   # «138.115–138.124 accepted as implemented: Freedom of…» sí es su etiqueta; otra cosa con «:» abre una lista
    if cierre.startswith(':') and len({clase(x[1]) for x in _COMENTARIO.finditer(g)} - {None}) > 1:
        return 'mixta'   # «Supported: Fully cooperate with OHCHR. / Noted: give access to …»: respuesta por partes
    if _PASADO.search(cl): return None
    if _PARCIAL.search(cl): return 'parcial'
    neg, pos = _NEG.search(cl), _POS_ESTRICTO.search(_NEG.sub(lambda x: ' ' * len(x[0]), cl))
    prim = min([x.start() for x in (neg, pos) if x], default=None)
    if prim is None: return None
    antes = cl[:prim]
    if len(antes) > 300 or re.search(r'\d|\(\w{1,3}\)', antes): return None
    if neg and pos: return 'mixta'
    return NOTA if neg else APOYADA


_ETIQUETAS = re.compile(r'(?i)^(?:not\s+|partially\s+|fully\s+)?(?:support|supports|supported|accept|accepts|accepted|note|notes|noted|'
                        r'take\s+note|taken\s+note|reject|rejects|rejected)\b')


def _etiqueta_linea(l):
    """Una línea que es solo la etiqueta de la fila («Supported», «Note», «Not accepted.», «Accepted / being implemented83»): ahí
    valen también las formas cortas («Support», «Note») que, con texto detrás («Support the national plan…»), serían el imperativo
    de una recomendación copiada y no una respuesta."""
    l = re.sub(r'[\s.:;,*\d]+$', '', l.strip())   # punto final o llamada de nota («Accepted1»)
    if not l or len(l.split()) > 5 or re.search(r'\d', l) or not _ETIQUETAS.match(l): return None
    if re.search(r'[:“"«]', l): return None   # «Noted: “Abolish the death penalty…”»: la parte de una respuesta mixta, no la etiqueta
    if re.search(r'[/&]|\band\b|,', l) and re.search(r'(?i)\bnot(?:e|es|ed)?\b|\breject|\btake', l) \
            and re.search(r'(?i)support|accept', l):
        return 'mixta'   # «Note/Support», «Supported/noted», «Noted and supported»: respuesta mixta, no se elige
    if re.match(r'(?i)^(?:note|notes|take\s+note|taken\s+note)\b', l) and not re.search(r'(?i)support|accept', l): return NOTA
    return clase(l)


def _hereda(a, tit, ini):
    """La respuesta del título de apartado bajo el que va una lista suelta («Recommendations that are accepted» y, debajo,
    «145.2–145.17, 145.21–145.67»). No hereda si entre el título y la lista hay otro título a medias («Recommendations that the
    Government has taken / under advisement»), un subtítulo o una frase que diga otra respuesta."""
    prev = [(p, r) for p, r in tit if p <= ini]
    if not prev or prev[-1][1] not in (APOYADA, NOTA, 'parcial'): return None
    p, r = prev[-1]
    if len(prev) >= 2 and prev[-2][1] in (APOYADA, NOTA) and prev[-2][1] != r and p - prev[-2][0] <= 80:
        return None   # dos títulos de columna seguidos («Recommendations Supported» / «Recommendations Noted»): no se sabe de cuál es
    g = a[p:ini]
    if re.search(r'(?im)^[ \t]*(?:(?:[IVX]+|[A-Z]|\d+)\.[ \t]*)?(?:recommendations?|responses?)\b', g): return None
    if (_PARCIAL.search(g) and r != 'parcial') or _PASADO.search(g): return None
    neg, pos = bool(_NEG.search(g)), bool(_POS.search(_NEG.sub(' ', g)))
    if (r == APOYADA and neg) or (r == NOTA and pos): return None
    return r


def _paginas(a):
    """Fuera cabeceras y pies de página («A/HRC/25/10/Add.1», «GE.13-19089», el número de página): parten las frases."""
    return re.sub(r'(?m)^[ \t]*\x0c?[ \t]*(?:A/HRC/[\w/.]+|GE\.\d\d-\d+[^\n]{0,12}|\d{1,3}|\d{6}(?:[ \t]+\d{6})?|\x0c)[ \t]*\x0c?[ \t]*$', '', a)


# «With regard to the recommendations noted in 123.26 and 123.27, the GoN has accepted the visit requests…»: la frase habla de
# esos números, pero lo que sigue no es su respuesta
_REMISION = re.compile(r'(?i)\b(?:with\s+(?:regard|reference|respect)\s+to|regarding|concerning|as\s+regards|in\s+relation\s+to)\b'
                       r'[^.;:\n]{0,60}?\b(?:noted|mentioned|contained|listed|referred\s+to|supported|accepted)\s+(?:in|under|at)\s*$')


def _listas_adendo(a, validos):
    """(corridas, etiqueta detrás de cada una, ¿documento de filas?) sobre el texto ya limpio de páginas."""
    cs = [c for c in _corridas(a, validos)   # «paragraphs 146.1–146.232 of the draft report», «see 28.175»: remisiones, no respuestas
          if not re.search(r'(?i)\b(?:paragraphs?|paras?\.?|contained in|see|refer to|cf\.?)\s*$', a[max(0, c[0] - 30):c[0]])
          and not _REMISION.search(a[max(0, c[0] - 90):c[0]])]
    desp = [_despues_etiqueta(a, fin, cs[i + 1][0] if i + 1 < len(cs) else len(a)) for i, (_, fin, _) in enumerate(cs)]
    # de filas: casi todas las corridas llevan su etiqueta detrás y la última también (en una lista con cabeceras, la última lista
    # no lleva nada detrás), o casi todas son de un solo número
    sueltos = sum(1 for c in cs if len(c[2]) == 1)
    filas = len(cs) >= 5 and ((sum(1 for x in desp if x) >= 0.6 * len(cs) and desp[-1] is not None) or
                              (len(cs) >= 8 and sueltos >= 0.6 * len(cs)))
    if filas:   # fila con varias celdas (país, tema, texto de la recomendación) y la etiqueta al final, justo antes del número siguiente
        for i, (_, fin, _) in enumerate(cs):
            if desp[i] is None and i + 1 < len(cs):
                lineas = [l for l in a[fin:cs[i + 1][0]].split('\n') if l.strip()]
                corte = next((k for k, l in enumerate(lineas) if re.fullmatch(r'[ \t]*\d{1,3}\.[ \t]*', l)), None)
                if corte is not None and corte >= 2: lineas = lineas[:corte]   # la última fila acaba donde empieza el párrafo «4.»
                if len(lineas) >= 2 and sum(1 for l in lineas if _etiqueta_linea(l)) == 1 and not re.search(r'(?i)recommendation', lineas[-1]):
                    desp[i] = _etiqueta_linea(lineas[-1])   # («Partially supported recommendations» es el título de otro apartado)
        desp = _celdas(a, cs, desp)
    return cs, desp, filas


def _celdas(a, cs, desp):
    """Una celda de tabla que acaba la línea en «;» sigue más abajo, aunque en medio salga su etiqueta o un salto de página
    («134.92; … 134.99;\nSupported\n[cabecera de página]\n134.100; … 134.105», «118.9; … 118.12; Accepted\n118.13; …»). Todas las
    partes llevan la etiqueta de la celda; si en la celda sale más de una etiqueta distinta, ninguna (no se sabe cuál es de quién)."""
    desp, i = list(desp), 0
    while i < len(cs):
        j = i
        while j + 1 < len(cs) and re.match(r'[ \t]*;', a[cs[j][1]:cs[j][1] + 3]) and cs[j + 1][0] - cs[j][1] <= 1500: j += 1
        if j > i:
            et = {_etiqueta_linea(l.lstrip(' \t;,')) for k in range(i, j) for l in a[cs[k][1]:cs[k + 1][0]].split('\n')} - {None}
            if desp[j]: et.add(desp[j])
            v = next(iter(et)) if len(et) == 1 else ('mixta' if et else None)
            for k in range(i, j + 1): desp[k] = v
        i = j + 1
    return desp


def _cabecera_parcial(g):
    """¿Hay entre la fila anterior y esta una cabecera de lista que dice «en parte» («… supports the following recommendation in part
    and notes the following part:»)?"""
    for cl, cierre in reversed(_clausulas(g)):   # solo cuenta la cabecera más cercana («(a) Accepted- 124 recommendations:» manda
        if (cierre == ':' or re.search(r'(?i)\bfollowing\b', cl)) and re.search(r'(?i)recommendation|following', cl):
            # (sobre «… partially accept 11 … as follows:», que va antes; «• Partly supported and partly noted: 3» es un recuento)
            return bool(_PARCIAL.search(cl))
    return False


_COMENTARIO = re.compile(r'(?im)^[ \t]*((?:not\s+)?(?:supported|accepted|noted|rejected))[ \t]*[–—:-][ \t]*\S')


def _comentario_contrario(g, c):
    """¿Alrededor de la fila hay un comentario que empieza por la respuesta contraria («Noted – See Anti-Violence Bill 2023» junto a
    «122.187 / Support»)? En una tabla descolocada por el salto de página no se sabe de qué fila es: mejor null."""
    vistos = {clase(m[1]) for m in _COMENTARIO.finditer(g)} - {None}
    if {APOYADA, NOTA} <= vistos: return False   # «Supported: … Noted: …»: es el comentario de una fila mixta, la de al lado
    return bool(vistos - {c})


# lo que hay entre un elemento de una lista y el siguiente cuando la lista sigue: el texto de la recomendación copiado, sin frase
# que se cierre, y un «;» al final («…(Germany);\nRecommendation 143.4», «(France);\n\n116.9», «(Spain);\n(b) Recommendation»)
_SIGUE_LISTA = re.compile(r'(?s)^[ \t]*:?[^.:]{0,1500};[ \t\n]*(?:and[ \t\n]+)?(?:[•▪◦·●][ \t]*)?(?:\(?[a-z]{1,3}[.)][ \t\n]*)?(?:Recommendations?(?:[ \t]+(?:No|Nos?)\.?)?[ \t]*)?$')


def del_adendo(a, validos):
    """{número: 'apoyada' | 'tomó nota' | 'parcial' | 'mixta'} para los números (de `validos`) que el adendo nombra con su respuesta.
    Dos maneras de escribirlo: cabecera y lista («Accepted: 125.6, 125.8 …») o filas (número y etiqueta detrás); se decide para
    todo el documento. Un número que sale con dos respuestas distintas queda «mixta»."""
    if not a: return {}
    a = _paginas(a)
    cs, desp, filas = _listas_adendo(a, validos)
    votos, tit, previo = {}, _titulos(a), None
    for i, (ini, fin, nums) in enumerate(cs):
        desde = cs[i - 1][1] if i else 0
        if filas:   # en un documento de filas, lo de antes es la fila anterior: solo vale una cabecera clara («… the following:»)
            c, cpre = desp[i], _antes(a, desde, ini, fuerte=True)
            if c and cpre and c != cpre: c = 'mixta'
            c = c or cpre
            if c is None and previo in (APOYADA, NOTA) and _SIGUE_LISTA.match(a[desde:ini]):
                c = previo   # lista bajo una cabecera («takes note of the following eight recommendations:»), sin etiqueta por fila
            previo = c if not desp[i] else None   # solo sigue una lista que abrió una cabecera, no la etiqueta de una fila
            if c in (APOYADA, NOTA):
                hasta = cs[i + 1][0] if i + 1 < len(cs) else len(a)
                if _cabecera_parcial(a[desde:ini]): c = 'parcial'   # «Nepal supports the following recommendation in part and notes…:»
                elif _comentario_contrario(a[desde:ini] + '\n' + a[fin:hasta], c): c = 'mixta'
                elif len(nums) <= 2 and _frases_sobre(a[fin:min(hasta, fin + 4000)]) - {c}: c = 'mixta'   # «121.13 / Noted / The Lao PDR accepts this
                    # recommendation in part.»: la etiqueta y su comentario no dicen lo mismo
        else:
            c, cpost = _antes(a, desde, ini), _despues_verbo(a, fin)
            if c and cpost and c != cpost: c = 'mixta'
            c = c or cpost
            h = _hereda(a, tit, ini)
            if c is None:   # lista suelta bajo un título de apartado: hereda la respuesta del título
                c = h
            elif h == 'parcial' and c in (APOYADA, NOTA):   # bajo «Recommendations that are partially accepted», «138.32 is accepted…»
                c = 'parcial'
            if c is None and previo in (APOYADA, NOTA) and _SIGUE_LISTA.match(a[desde:ini]):
                c = previo   # «…following recommendations: Recommendation 143.3: Review … (Germany); Recommendation 143.4: …»
            previo = c
        if c is None: continue
        for n in nums: votos.setdefault(n, set()).add(c)
    return {n: (next(iter(v)) if len(v) == 1 else 'mixta') for n, v in votos.items()}


def _frases_sobre(x):
    """Respuestas que dicen las frases de `x` que hablan de «this/the recommendation» («This recommendation is rejected.», «The Lao
    PDR accepts this recommendation in part.»), sin las cabeceras de otra lista («… the following recommendations:»)."""
    return {clase(_limpia(f)) for f in re.split(r'(?<=[.;:])\s+', x)
            if re.search(r'(?i)\b(?:this|the|these|that|said|both)\s+(?:\w+\s+)?recommendations?\b', f)
            and not _LISTA_SIGUE.search(f) and not f.rstrip().endswith(':')} - {None, 'mixta'}


_CAMBIO = re.compile(r'''(?ix)\bchang\w*\s+(?:its|the|our|their)\s+position | \bno\s+longer\b | \bwithdr[ae]w\w* | \breconsider\w*
  | \bafter\s+(?:further\s+|careful\s+)?consideration | \b(?:initially|previously|originally|earlier)\b[^.;]{0,120}\bnow\b
  | \bmisplace\w* | \bmov(?:e|ed|ing)\s+(?:the\s+)?recommendations?\b | \bnot\s+in\s+a\s+position\s+to\b''')
_FIN_FRASE = re.compile(r'[.;:!?](?=\s)|\n[ \t]*\n')


def contradice_informe(a, inf, validos):
    """Números cuya respuesta del informe el adendo pone en duda: una frase del adendo que los nombra dice la respuesta contraria
    o «en parte» («Thailand is not in a position to support recommendation 51.1», «With regard to 128.54, … Sri Lanka is able to
    support this recommendation») o habla de un cambio de posición («initially supported, is now noted», «Upon reconsideration…»).
    Es solo una red de seguridad: el número pasa a null, no se toma la respuesta nueva."""
    if not a: return set()
    a, out = _paginas(a), set()
    cs = _corridas(a, validos)
    for ini, fin, nums in cs:
        if not any(inf.get(n) in (APOYADA, NOTA) for n in nums): continue
        ms = [m.end() for m in _FIN_FRASE.finditer(a, max(0, ini - 400), ini)]
        i0 = ms[-1] if ms else max(0, ini - 400)
        m = _FIN_FRASE.search(a, fin)
        f0 = m.start() if m else len(a)
        sl = re.search(r'\n[ \t]*(?=[A-Z•])', a[fin:f0])   # la frase acaba donde empieza otra línea en mayúscula («91.10\nNoted the…»)
        frase = _limpia(a[i0:fin + sl.start()] if sl else a[i0:f0])
        c, cambio = clase(frase), bool(_CAMBIO.search(frase))
        # lo que el adendo explica detrás del número, hasta el número siguiente: «124.13 Eliminate the caste system … (Romania)
        # / 18. In Senegal, … This recommendation is rejected.»
        sig = next((x[0] for x in cs if x[0] >= fin), len(a))
        detras = _frases_sobre(a[fin:min(sig, fin + 4000)])
        for n in nums:
            ri = inf.get(n)
            if ri in (APOYADA, NOTA) and (cambio or c == 'parcial' or c in (APOYADA, NOTA) and c != ri or detras - {ri}): out.add(n)
    return out


def respuestas(texto_informe_en, texto_adendo_en, numeros):
    """{número: {'r': 'apoyada'|'tomó nota'|None, 'fuente': 'informe'|'adendo'|None}} para TODOS los `numeros`."""
    inf = del_informe(texto_informe_en or '')
    add = del_adendo(texto_adendo_en or '', set(numeros))
    duda = contradice_informe(texto_adendo_en or '', inf, set(numeros))
    salida = {}
    for n in numeros:
        ri, ra = inf.get(n), add.get(n)
        if ri in (APOYADA, NOTA):
            if (ra is not None and ra != ri) or n in duda: salida[n] = {'r': None, 'fuente': None}   # el adendo dice otra cosa: no se elige
            else: salida[n] = {'r': ri, 'fuente': 'informe'}
        elif ra in (APOYADA, NOTA): salida[n] = {'r': ra, 'fuente': 'adendo'}
        else: salida[n] = {'r': None, 'fuente': None}
    return salida


def _lee(ruta):
    return open(ruta, encoding='utf-8', errors='ignore').read() if os.path.exists(ruta) else None


def medir(d, auditoria=None):
    inf = json.load(open(os.path.join(R.RAIZ, 'data/fuentes/epu_informes.json'), encoding='utf-8'))
    tot = {'informes': 0, 'recomendaciones': 0, 'informe': 0, 'adendo': 0, 'null': 0, 'apoyada': 0, 'tomó nota': 0,
           'informes_completos': 0, 'informes_sin_adendo_txt': 0}
    por = {}
    for iso, lista in sorted(inf['paises'].items()):
        for f in lista:
            c = R.ciclo(f['d'])
            if c == 1: continue
            t = _lee(os.path.join(d, 'txt', f"{R.slug(f['s'])}-en.txt"))
            nums = R.numeros(t) if t else None
            if not nums: continue
            a = _lee(os.path.join(d, 'txt', f"{R.slug(f['add']['s'])}-en.txt")) if f.get('add') else None
            if a is None: tot['informes_sin_adendo_txt'] += 1
            res = respuestas(t, a, nums)
            k = {'informe': 0, 'adendo': 0, 'null': 0}
            for v in res.values():
                k[v['fuente'] or 'null'] += 1
                if v['r']: tot[v['r']] += 1
            tot['informes'] += 1; tot['recomendaciones'] += len(nums)
            for x in k: tot[x] += k[x]
            if not k['null']: tot['informes_completos'] += 1
            por[f['s']] = {'iso': iso, 'ciclo': c, 'n': len(nums), **k, 'add': (f.get('add') or {}).get('s')}
    if auditoria:
        json.dump({'total': tot, 'informes': por}, open(auditoria, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return tot, por


def main():
    d = R.DIR
    if '--dir' in sys.argv: d = sys.argv[sys.argv.index('--dir') + 1]
    aud = sys.argv[sys.argv.index('--auditoria') + 1] if '--auditoria' in sys.argv else None
    tot, por = medir(d, aud)
    n = tot['recomendaciones'] or 1
    print(f"{tot['informes']} informes (ciclos 2-4) con numeración completa; {tot['recomendaciones']} recomendaciones")
    for x in ('informe', 'adendo', 'null'): print(f"  {x:8} {tot[x]:6}  {100 * tot[x] / n:5.1f} %")
    print(f"  apoyadas {tot['apoyada']}, tomó nota {tot['tomó nota']}; informes con todas respondidas: {tot['informes_completos']};"
          f" sin texto del adendo: {tot['informes_sin_adendo_txt']}")


if __name__ == '__main__': main()
