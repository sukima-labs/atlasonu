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
Si el informe y el adendo no dicen lo mismo, null; salvo que el adendo cambie la posición de forma explícita y diga cuál es la
final («… which was initially supported, is now noted»): entonces vale esa. Lo que el adendo dice de un número cuyo texto copiado es
el de otra recomendación (adendo que numera mal) no cuenta.
Mejor null que un dato falso: el que lo muestre enlaza el documento donde está la respuesta.
Uso: epu_respuestas.py [--dir DIR_TEXTOS] [--auditoria FICHERO.json]   (mide la cobertura sobre los ciclos 2 a 4; no escribe datos)"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import epu_recomendaciones as R  # noqa: E402

APOYADA, NOTA = 'apoyada', 'tomó nota'
_PARCIAL = re.compile(r'\bpartial\w*|(?:\b(?:not|cannot)\b|n[’\x27]t\b)[^.;:]{0,60}\bin\s+(?:its|their)\s+entirety\b|\bin part\b(?!\s+of\s+(?:the\s+)?(?:Articles?|art\.))|\bpartly\b|\bAIP\b|\b(?:first|second|third|fourth|other|one|some|certain)\s+parts?\b|\b(?:the|that|this)\s+(?:parts?|aspects?|elements?)\s+of\s+(?:the|this|that)\s+recommendation|\bin principle\b'
                      r'|\b(?:accept|support)\w*,?\s+in\s+respect\s+of\b|\bonly\s+(?:in\s+respect\s+of|with\s+(?:regard|respect)\s+to|as\s+regards|regarding|concerning)\b|\bto\s+the\s+extent\b|\binsofar\b'
                      r'|\bthe\s+notion\b'
                      r'|\bunder\s+the\s+(?:stipulation|condition|proviso)\b|\b(?:with|on)\s+the\s+(?:understanding|reservation|caveat|proviso)\b|\bsubject\s+to\s+(?:the\s+)?(?:clarification|reservation|condition|understanding)'
                      r'|\bprovided\s+that\b|\bon\s+condition\s+that\b', re.I)   # T75 r3: aceptación condicionada = sin dato («accepted under the stipulation that…», «with the understanding…»)   # «noted only in respect of the phrase…», «cannot accept …, to the extent that…»   # «138.32 is accepted in respect of the continuation of…»
# lo negativo va primero y se come su frase entera: «did not enjoy the support» no debe dejar suelto «the support»
_NEG = re.compile(r'''(?ix)
    (?:\b(?:not|cannot|can\s?not|unable\s+to|fail(?:s|ed)?\s+to)|n[’']t)\s+(?:\w+\s+){0,3}?(?:accept\w*|support\w*|approv\w*|enjoy\w*(?:\s+\S+){0,2}?\s+support\b|enjoy\w*)
  | \bnot\s+in\s+(?:a|the)\s+position\s+to\s+(?:accept|support)\w*
  | \b(?:impossible|difficult)\s+to\s+(?:\w+\s+){0,2}?(?:accept|support)\w*
  | \bno\s+(?:grounds|reason|basis|plans?)\s+to\s+(?:\w+\s+){0,2}?(?:accept|support)\w*
  | \breject\w*
  | \bt(?:ake|akes|aken|aking|ook)\s+(?:\w+\s+){0,2}?note\b
  | \bnote\s+(?:has|have)\s+been\s+taken\b
  | \b(?:we|I)\s+(?:\w+\s+)?note\s+(?=(?:the\s+)?(?:following|recommendations?|\d))
  | \bto\s+note\s+(?:the\s+|this\s+|these\s+)?(?=recommendation|following|\d)
  | \bnoted\b | \bnotes\s+(?:the\s+|this\s+|these\s+|that\s+)?(?=following|\d|recommendation|remaining)
  | \bwill\s+not\s+be\s+considered\b''')
_POS = re.compile(r'(?i)\baccept\w*|\bsupport\w*|\benjoy\w*\s+(?:the|its)\s+support|\bapproved\b')
_PEND = re.compile(r'(?i)will\s+(?:be\s+(?:further\s+)?examined|examine|provide\s+(?:its\s+)?respon|respond|be\s+included)|respon\w+\s+will\s+be\s+provided')


# para sacar una respuesta de una frase en prosa (no de una etiqueta ni de una cabecera), «support» tiene que ser el verbo de la
# respuesta: «accepts», «supported», «able to support», no el sustantivo («welcomes the technical support offered in fulfilling this
# recommendation», A/HRC/33/11/Add.1, 118.7, que además acepta un tratado y no el otro)
_POS_RESP = re.compile(r'(?i)\b(?:accepts|accepted|supports|supported|approved)\b|\benjoy\w*\s+(?:the|its)\s+support'
                       r'|\b(?:to|will|shall|can|could|would|does|do|hereby)\s+(?:\w+\s+)?(?:accept|support)\b')


def clase(x, estricto=False):
    """'apoyada', 'tomó nota', 'parcial', 'mixta' (dice las dos cosas) o None (no dice qué). `estricto`: lo positivo solo con el
    verbo de la respuesta (_POS_RESP); lo negativo y lo parcial, igual."""
    if _PARCIAL.search(x): return 'parcial'
    neg = bool(_NEG.search(x))
    pos = bool((_POS_RESP if estricto else _POS).search(_NEG.sub(' ', x)))
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
_NUM = re.compile(r'(?<![\d,/])(?<!\d\.)(\d{2,3})\.(\d{1,3})(?![\d]|\.\d)')   # «Rec.123.86» también
# 117.84, 85, 86 · 80.15–16 · «No. 34.6, 7, …, 31,\n32, 33, …» (la lista sigue en la línea siguiente si allí sigue con «,»)
_CONT = re.compile(r'[ \t]*(?:(,)|[-–—‑]|\bto\b)[ \t]*(?:(?<=,)[ \t]*\n[ \t]*(?=\d{1,3}[ \t]*,))?(\d{1,3})(?![\d]|\.\d)')
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
            elif _SEP.match(gap) or (re.fullmatch(r'[ \t]*:[ \t]*\n?[ \t]*', gap) and expl[-1] and re.match(r'[ \t]*[;:,]', a[fin:fin + 3])) \
                    or (not gap.strip() and ('\n' not in gap or (
                    _solo_en_linea(a, ini, fin) and not expl[-1]
                    and (gap.count('\n') == 1 or not a[a.rfind('\n', 0, ult) + 1:ult].strip())))):
                # una lista que separa con «;» y acaba la línea sin él («134.104; 134.105\n134.106»): lo de abajo es otra fila;
                # tras una línea en blanco solo sigue una columna de números sueltos, no «See 186.1\n\n186.14.»; un «:» por «;» en
                # medio de una lista que separa con «;» («24.305; 24.306:\n24.307: 24.308; 24.309», A/HRC/57/6/Add.1) es una errata
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
    if cierre == '.' and re.search(r'(?i)\b(?:(?:this|that|said|the)\s+recommendation|these\s+recommendations)$', cl):
        return False   # «108.8 / Seychelles accepts the recommendation.»: es la respuesta de la fila de antes, no la cabecera de la siguiente
    cl = re.sub(r'\s*\(\d+\)$', '', cl)   # «Recommendations accepted by the Government (22)»: el recuento no cuenta
    if re.match(r'(?:(?:[IVX]+|[A-Z]|\d+)\.\s*)?(?:Recommendations?|RECOMMENDATIONS?)\b', cl) and len(cl) <= 120: return True
    # («Following the ratification of ILO Conventions…, Italy has accepted to be reviewed…» no presenta ninguna lista)
    return cierre == ':' or (len(cl) <= 40 and not fuerte) or bool(re.search(r'(?i)recommendations?(?: nos?\.?| numbers?)?$|\bfollowing\b', cl)
                                                                      and not re.match(r'(?i)following\s+(?!(?:\w+\s+){0,2}?recommendations?\b)', cl))


def _antes(a, desde, ini, fuerte=False):
    """Respuesta que da la cabecera inmediatamente anterior a la lista («X supports the following recommendations:», «(a) Accepted.»)."""
    cls = _clausulas(a[max(desde, ini - 600):ini])
    for j in range(len(cls) - 1, max(-1, len(cls) - 4), -1):
        cl, cierre = cls[j]
        if _PASADO.search(cl): return None
        if re.search(r'(?i)\bexcept\b|\bother\s+than\b|\bwith\s+the\s+exception\b', cl): return None   # «All … enjoy support of
        # Montenegro, except recommendations number:» presenta las que NO (A/HRC/23/12/Add.1)
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
    r = NOTA if neg else APOYADA
    if cierre.startswith(';'):   # «109.8. Not accepted with respect to ICRMW (see recommendation 2); accepted\nconcerning CPED.»
        resto = g[m.end():]       # (A/HRC/23/5/Add.1): la frase sigue tras el «;» y dice otra cosa; se lee entera
        f = re.search(r'\.(?=\s|$)|\n[ \t]*\n', resto)
        cr = clase(resto[:f.start()] if f else resto[:300])
        if cr and cr != r: return 'mixta'
    return r


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


_SECCION = re.compile(r'''(?mx)
    ^[ \t]*[A-H]\.[ \t]*\n(?:[ \t]*\n)*[ \t]*
      ((?:Partially\s+|Not\s+)?(?:Support|Supported|Accept|Accepted|Note|Noted|Reject|Rejected))(?:[ \t]+recommendations?)?[ \t]*$
  | ^[ \t]*(?:(?:[A-Z]|[IVX]+)\.[ \t]*)?((?:Partially\s+|Not\s+)?(?:Supported|Accepted|Noted|Rejected))[ \t]+recommendations[ \t]*$''')


def _secciones(a):
    """[(pos, respuesta)] de los apartados con etiqueta («A.\\n\\nSupport» … «B.\\n\\nNote», A/HRC/55/10/Add.1; «Supported
    recommendations» … «Noted recommendations», A/HRC/47/12/Add.1) y de los títulos de apartado de _titulos(): en una tabla, una
    fila sin etiqueta propia va en el apartado que la contiene."""
    out = [(m.end(), _etiqueta_linea(m[1] or m[2]) or clase(m[1] or m[2])) for m in _SECCION.finditer(a)]
    # cualquier otro título enumerado corta el apartado anterior y, si dice cuál es su respuesta, abre el suyo («ІІІ. Not accepted/
    # Noted recommendations», con la «І» cirílica, en A/HRC/30/10/Add.1; «II. Accepted recommendations that Bulgaria considers…»)
    for m in re.finditer(r'(?m)^[ \t]*(?:[IVXІ]{1,5}|[A-H])\.[ \t]+([^\n]{3,90})$', a):
        if any(abs(m.end() - p) <= 2 for p, _ in out): continue
        c = clase(m[1]) if re.search(r'(?i)recommendation', m[1]) and not re.search(r'(?i),|\bexcept\b', m[1]) else None
        out.append((m.start(1), c if c in (APOYADA, NOTA) else None))   # («IX. Recommendations 108.25, 108.51 and 108.62»: los números
        # del título ya van en su apartado; «I. All the recommendations enjoy support of Montenegro,\nexcept …» no es un título)
    # y un título suelto que habla de recomendaciones («Explanations on some recommendations already supported on 26 January
    # 2021», debajo de «Noted recommendations» en A/HRC/47/12/Add.1) corta el apartado sin abrir otro
    for m in re.finditer(r'(?m)(?<=\n\n)[ \t]*[A-Z][^\n.:;]{0,80}\brecommendations?\b[^\n.:;]{0,50}$', a):
        if not any(abs(m.end() - p) <= 2 for p, _ in out): out.append((m.end(), None))
    return sorted(out + [x for x in _titulos(a) if _TITULO.match(a, a.rfind('\n', 0, x[0]) + 1)])


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


def _listas_adendo(a, validos, textos=None):
    """(corridas, etiqueta detrás de cada una, ¿documento de filas?) sobre el texto ya limpio de páginas."""
    cs = _corridas(a, validos)
    ajenas = {cs[k][0] for k in _ajenas(a, cs, textos)}   # siguen en la lista (marcan dónde acaba la anterior), pero no votan
    cs = [c for c in cs   # «paragraphs 146.1–146.232 of the draft report», «see 28.175»: remisiones, no respuestas
          if not re.search(r'(?i)\b(?:paragraphs?|paras?\.?|contained in|see|refer to|cf\.?|(?:(?:see|refer\s+to)(?:\s+also)?\s+(?:the\s+|our\s+)?(?:explanations?|answers?|responses?|repl(?:y|ies)|comments?)|explanations?)\s+(?:on|to|for|in|under)(?:\s+(?:recommendations?|rec\.))?)\s*$', a[max(0, c[0] - 60):c[0]])
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
    return cs, desp, filas, ajenas


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
        if (cierre == ':' and re.search(r'(?i)recommendation|following', cl)) or \
                re.search(r'(?i)\bthe\s+following\s+(?:\w+\s+){0,3}?(?:recommendations?|parts?)\b', cl):
            # (sobre «… partially accept 11 … as follows:», que va antes; «• Partly supported and partly noted: 3» es un recuento)
            # un recuento con varias cifras («Of the following 60 recommendations …, 58 have been noted and 2 partially noted …»)
            # no es la cabecera de la fila; ni «following verification of …» o «we provide the following information», el
            # comentario de la fila anterior
            if len(re.findall(r'(?<![\d.])\d+(?![\d.]\d)', cl)) >= 2: return False
            return bool(_PARCIAL.search(cl))
    return False


def _bloques(x):
    """Párrafos (separados por una línea en blanco) no vacíos de `x`."""
    return [b.strip() for b in re.split(r'\n[ \t]*\n', x) if b.strip()]


def _tramo(a, cs, desp, i):
    """Lo que va detrás de la fila i y es suyo: hasta la fila siguiente, salvo que (1) sea la última de la tabla («135.273 /
    Accepted» y, después, «5. In total, of the 273 recommendations received, …», o «III. Conclusion»): acaba en el párrafo
    numerado o el título que sigue; (2) la fila siguiente no lleve etiqueta detrás de su número porque la lleva encima, alineada
    con su primera línea («94.104 / Accepted / Grenada supports this recommendation. / Noted / Grenada notes this recommendation. /
    Decriminalize abortion / 94.105»): lo suyo acaba donde empieza la segunda etiqueta."""
    fin = cs[i][1]
    hasta = cs[i + 1][0] if i + 1 < len(cs) else len(a)
    t = a[fin:min(hasta, fin + 4000)]
    if i + 1 == len(cs):
        m = re.search(r'\n[ \t]*(?:\d{1,3}\.|[IVX]+\.[ \t]+[A-Z][^\n]*|Conclusions?|Notes?)[ \t]*\n', t)   # («Notes»: las notas al pie)
        if m: t = t[:m.start()]
    elif desp[i + 1] is None:
        lineas = t.split('\n')
        ets = [k for k, l in enumerate(lineas) if l.strip() and _etiqueta_linea(l)]
        if len(ets) >= 2 and not [l for l in lineas[:ets[0]] if l.strip(' \t.:;,')]:
            t = '\n'.join(lineas[:ets[1]])
    return t


def _suelto(a, cs, desp, i):
    """¿La columna de comentarios de la tabla va suelta? Detrás de la fila i salen tres párrafos o más y las dos filas de antes no
    llevaban ninguno (solo su etiqueta): el PDF puso juntos los comentarios de varias filas («42.342 / Accepted / 42.343 /
    Accepted / Already implemented. / Already implemented. / Egypt rejects the erroneous references in this recommendation. / …»).
    Entonces no se sabe de qué fila es cada comentario, y manda la etiqueta de la fila."""
    if i < 2: return False
    def comentarios(k):
        hasta = cs[k + 1][0] if k + 1 < len(cs) else len(a)
        bs = _bloques(a[cs[k][1]:hasta].lstrip(' \t.:;,'))
        return bs[1:] if bs and _etiqueta_linea(bs[0].split('\n')[0]) and '\n' not in bs[0] else bs
    return len(comentarios(i)) >= 3 and all(desp[k] and not comentarios(k) for k in (i - 1, i - 2))


_COMENTARIO = re.compile(r'(?im)^[ \t]*((?:not\s+)?(?:supported|accepted|noted|rejected))[ \t]*[–—:-][ \t]*\S')


def _comentario_contrario(g, c, post=None):
    """¿Alrededor de la fila hay un comentario que empieza por la respuesta contraria («Noted – See Anti-Violence Bill 2023» junto a
    «122.187 / Support»)? En una tabla descolocada por el salto de página no se sabe de qué fila es: mejor null.
    Con `post` (lo de después de la fila), `g` es lo de antes y no cuentan: la etiqueta de la fila anterior, que abre ese tramo
    («58.33.\\nNoted – Access to …» antes de «58.34. Supported.»), ni, si la fila lleva su etiqueta justo detrás del número, los
    trozos «Noted: …» / «Supported: …» de una respuesta por partes que el salto de página dejó encima («Noted: and transitional
    justice mechanisms» y, debajo, «135.66 / Accepted»): esos son de otra fila, la que dice «Partially accepted»."""
    if post is not None:
        pre = g.lstrip(' \t\n.;,')
        primera = _COMENTARIO.match(pre)
        if primera: pre = pre[primera.end():]
        propia = bool(_etiqueta_linea(post.lstrip(' \t\n.;,:').split('\n')[0]))
        quitar = [m.span() for m in _COMENTARIO.finditer(pre) if propia and ':' in pre[m.end(1):m.end()]]
        for i, j in reversed(quitar): pre = pre[:i] + '\n' + pre[j:]
        g = pre + '\n' + post
    vistos = {clase(m[1]) for m in _COMENTARIO.finditer(g)} - {None}
    if {APOYADA, NOTA} <= vistos: return False   # «Supported: … Noted: …»: es el comentario de una fila mixta, la de al lado
    return bool(vistos - {c})


# lo que hay entre un elemento de una lista y el siguiente cuando la lista sigue: el texto de la recomendación copiado, sin frase
# que se cierre, y un «;» al final («…(Germany);\nRecommendation 143.4», «(France);\n\n116.9», «(Spain);\n(b) Recommendation»)
_SIGUE_LISTA = re.compile(r'(?s)^[ \t]*:?[^.:]{0,1500};[ \t\n]*(?:and[ \t\n]+)?(?:[•▪◦·●][ \t]*)?(?:\(?[a-z]{1,3}[.)][ \t\n]*)?(?:Recommendations?(?:[ \t]+(?:No|Nos?)\.?)?[ \t]*)?$')


# el Estado dice que no toma posición («has decided not to consider recommendations 125.86, …», A/HRC/41/6/Add.1, en una «Additional
# note» que va detrás de «Recommendations not accepted»): ni «apoyada» ni «tomó nota»
_SIN_POSICION = re.compile(r'(?i)\b(?:not|never)\s+(?:to\s+)?(?:consider|examine|address|respond\s+to|take\s+(?:a\s+|any\s+)?position)\b'
                           r'|\bdeclin\w*\s+to\s+(?:consider|examine|respond|take)\b|\bno\s+(?:response|position)\s+(?:to|on)\b')


_REMITE = re.compile(r'(?i)\b(?:answered|addressed|response|responses|replied|found|covered|explained)\s+(?:is\s+|are\s+)?(?:in|under|at|by)\s*$')


def _parrafo(a, ini, fin):
    """El párrafo del adendo (entre líneas en blanco, hasta 1500 caracteres a cada lado) en el que va la corrida [ini, fin)."""
    i = a.rfind('\n\n', max(0, ini - 1500), ini)
    j = a.find('\n\n', fin, fin + 1500)
    return _limpia(a[i if i >= 0 else max(0, ini - 1500):j if j >= 0 else fin + 1500])


def _frase_de(a, ini, fin):
    """La frase del adendo en la que va la corrida [ini, fin)."""
    ms = [m.end() for m in _FIN_FRASE.finditer(a, max(0, ini - 400), ini)]
    m = _FIN_FRASE.search(a, fin)
    return _limpia(a[ms[-1] if ms else max(0, ini - 400):m.start() if m else len(a)])


def _hereda_fila(a, ini, fin, r):
    """¿Una fila sin etiqueta puede tomar la respuesta `r` del apartado que la contiene? No si la frase en la que va dice que el
    Estado no toma posición (_SIN_POSICION), ni si dice otra respuesta o «en parte»."""
    f = _frase_de(a, ini, fin)
    if _SIN_POSICION.search(f): return False
    c = clase(f)
    return c is None or c == r


def del_adendo(a, validos, textos=None, pendientes=None):
    """{número: 'apoyada' | 'tomó nota' | 'parcial' | 'mixta'} para los números (de `validos`) que el adendo nombra con su respuesta.
    Dos maneras de escribirlo: cabecera y lista («Accepted: 125.6, 125.8 …») o filas (número y etiqueta detrás); se decide para
    todo el documento. Un número que sale con dos respuestas distintas queda «mixta». Con `pendientes` (los números que el
    informe deja para el adendo), una fila sin etiqueta solo toma la del apartado que la contiene si es de esos: en A/HRC/47/12/Add.1
    las «Explanations on some recommendations already supported» van debajo de «Noted recommendations» y no son de ese apartado."""
    if not a: return {}
    a = _paginas(a)
    cs, desp, filas, ajenas = _listas_adendo(a, validos, textos)
    votos, tit, previo, secs, sueltas, propia = {}, _titulos(a), None, (_secciones(a) if filas else []), {}, {}
    for i, (ini, fin, nums) in enumerate(cs):
        desde = cs[i - 1][1] if i else 0
        if ini in ajenas:   # el adendo copia otra recomendación con este número (Senegal, A/HRC/25/4/Add.1): no es esta
            previo = None; continue
        if filas:   # en un documento de filas, lo de antes es la fila anterior: solo vale una cabecera clara («… the following:»)
            c, cpre = desp[i], _antes(a, desde, ini, fuerte=True)
            if c and cpre and c != cpre: c = 'mixta'
            c = c or cpre
            if c is None and previo in (APOYADA, NOTA) and _SIGUE_LISTA.match(a[desde:ini]):
                c = previo   # lista bajo una cabecera («takes note of the following eight recommendations:»), sin etiqueta por fila
            previo = c if not desp[i] else None   # solo sigue una lista que abrió una cabecera, no la etiqueta de una fila
            if c is None:   # fila sin etiqueta («140.40–140.43» bajo «A. Support»): la del apartado que la contiene; no si son
                ant = [(p, r) for p, r in secs if p <= ini]   # dos títulos de columna seguidos («Accepted recommendations» /
                if ant and ant[-1][1] in (APOYADA, NOTA) and (pendientes is None or set(nums) <= pendientes) and _hereda_fila(a, ini, fin, ant[-1][1]) and not (   # «Noted recommendations», A/HRC/58/14/Add.1)
                        len(ant) >= 2 and ant[-2][1] in (APOYADA, NOTA) and ant[-2][1] != ant[-1][1] and ant[-1][0] - ant[-2][0] <= 80):
                    c = ant[-1][1]
            if c in (APOYADA, NOTA):
                hasta = cs[i + 1][0] if i + 1 < len(cs) else len(a)
                if _cabecera_parcial(a[desde:ini]): c = 'parcial'   # «Nepal supports the following recommendation in part and notes…:»
                elif desp[i] and _suelto(a, cs, desp, i):
                    pass   # la columna de comentarios va aparte (varios seguidos tras filas sin ninguno): manda la etiqueta de la fila
                elif _comentario_contrario(a[desde:ini], c, _tramo(a, cs, desp, i)): c = 'mixta'
                elif len(nums) <= 2 and _frases_sobre(_tramo(a, cs, desp, i)) - {c}: c = 'mixta'   # «121.13 / Noted / The Lao PDR accepts this
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
        if c is None and len(nums) == 1 and re.search(r'(?i)(?:\A|\n)[ \t]*(?:•[ \t]*)?(?:recommendations?[ \t]+(?:no\.?[ \t]*)?)?\Z', a[max(0, ini - 40):ini]):
            # «128.33: The recommendation is in conflict with South Sudan customs … cannot be supported.», «Recommendation 96.26 …
            # / 11. … / Samoa notes this recommendation on the grounds…»: el número abre su apartado y, hasta el siguiente, todo lo que
            # se dice de «this recommendation» dice lo mismo
            hasta = cs[i + 1][0] if i + 1 < len(cs) else len(a)
            tr = _tramo(a, cs, desp, i) if filas else a[fin:min(hasta, fin + 4000)]
            # hasta el título del apartado siguiente («II.», «B.», o un subtítulo suelto: «Non-discrimination»)
            tr = re.split(r'\n[ \t]*(?:[IVX]+|[A-H])\.[ \t]*(?=\n|[A-Z])|(?<=[.\n])[ \t]*\n[ \t]*[A-Z][^\d.:;()\n]{2,60}[ \t]*\n(?=[ \t]*[A-Z\d(])', tr[:2500])[0]
            fs = _frases_sobre(tr, estricto=True)
            prim = next((l.strip() for l in tr.split('\n') if l.strip(' \t.:;–—-')), '')
            if len(prim.split()) <= 4 and not prim.endswith('.'): fs = set()   # «84.57 / Taken into consideration»: una etiqueta que no se entiende
            if fs and not any(_etiqueta_linea(l) for l in tr.split('\n') if 0 < len(l.split()) <= 3):
                sueltas.setdefault(nums[0], set()).update(fs)   # (si hay una etiqueta de fila, «Accepted», manda ella y aquí no se lee nada); solo
                propia.setdefault(nums[0], set()).add(ini)      # vale si el número no sale en ninguna otra lista con respuesta
            continue
        if c is None: continue
        for n in nums: votos.setdefault(n, set()).add(c)
    # si el adendo nombra el número en otro sitio (no en una remisión: «Answered in 118.15.»), el párrafo de allí tiene que decir lo
    # mismo con todas las letras: «Recommendation 96.2 / … Samoa accepts this recommendation» y, más abajo, «Recommendations 96.1,
    # 96.2, … / … Samoa notes this recommendation» (A/HRC/33/6/Add.1, una recomendación de varios tratados) no se elige; «… did not
    # enjoy its support and therefore are noted … (128.30, 128.33, …)» y «128.33: … cannot be supported» (A/HRC/34/13/Add.1) sí
    otras = {}
    for ini, fin, ns in cs:
        if _REMITE.search(a[max(0, ini - 40):ini]): continue
        for n in ns:
            if n in sueltas and ini not in propia.get(n, ()): otras.setdefault(n, []).append((ini, fin))
    for n, v in sueltas.items():
        if n in votos or len(v) != 1 or next(iter(v)) not in (APOYADA, NOTA): continue
        if all(clase(_parrafo(a, ini, fin), estricto=True) == next(iter(v)) for ini, fin in otras.get(n, [])): votos[n] = v
    return {n: (next(iter(v)) if len(v) == 1 else 'mixta') for n, v in votos.items()}


_VERBO = re.compile(r'(?i)\b(?:accept\w*|support\w*|approv\w*|not(?:e|es|ed)\b|reject\w*|t(?:ake|akes|aken|ook)\s+(?:\w+\s+)?note)')
_SOBRE = re.compile(r'(?i)\b(?:this|the|these|that|said|both)\s+(?:(\w+)\s+)?recommendations?\b')
# un recuento («In total, of the 273 recommendations received, 226 were accepted … 10 were partially accepted», «The 17
# recommendations which are ‘Noted’», «all recommendations which received TGoNU approval») no habla de ninguna en concreto
_RECUENTO = re.compile(r'(?i)\b(?!(?:19|20)\d\d\b)\d+\s+(?:of\s+the\s+\d+\s+)?(?:recommendations|were|are|have|had)\b|\bthe\s+\d+\s+recommendations\b'
                       r'|\b(?:all|most|some|many|other)\s+(?:of\s+)?(?:the\s+)?recommendations\b'   # («does not support all the recommendations relating to LGBTQ persons», A/HRC/63/5/Add.1)
                       r'|\brecommendations\s+(?:formulated|made|received)\s+(?:\w+\s+){0,3}?during\b'   # título de otro apartado
                       r'|\bthe\s+recommendations\s+(?:that|which)\b'
                       r'|\b(?:noted|mentioned)\s+(?:above|earlier|before|previously)\b')   # «noted above» = mencionada, no «tomó nota»   # «The recommendations that were “noted”, should not imply…»


def _frases_sobre(x, estricto=False):
    """Respuestas que dicen las frases de `x` que hablan de «this/the recommendation» («This recommendation is rejected.», «The Lao
    PDR accepts this recommendation in part.»), sin las cabeceras de otra lista («… the following recommendations:», o la frase sin
    cerrar que va justo antes de los números siguientes: «Azerbaijan rejects the recommendations» 110.1, …) ni los recuentos. Solo
    cuenta lo que se dice junto a «the recommendation» (diez palabras antes, catorce después): en «The accepted recommendations will be
    implemented…» no hay respuesta a esa recomendación. «En parte» solo cuenta si la frase dice también qué hace con ella («accepts
    this recommendation in part»; no «aligns itself with the first part of the recommendation»). Tampoco las que hablan de otro
    ciclo («the recommendations posed during the second cycle of review and enjoy the support of Turkey»).
    `estricto` (para sacar de ahí una respuesta, no solo para ponerla en duda): seis palabras a cada lado («… as well as the
    recommendations and guidelines of the European Asylum Support Office» no dice nada), salvo que la frase empiece por «The
    recommendation …» («The recommendation is in conflict with South Sudan customs and beliefs as such cannot be supported.»)."""
    fr = re.split(r'(?<=[.;:])\s+|\n[ \t]*\n', x)
    if fr and not re.search(r'[.;:!?]\s*$', x) and re.search(
            r'(?i)(?:recommendations?(?:\s+(?:nos?\.?|numbers?))?|\b(?:are|is|include|includes|namely|in|under|at|to|of|on))\s*$', fr[-1]):
        fr = fr[:-1]   # («With regard to the recommendations noted above in» 123.28: lleva al número siguiente)
    out = set()
    for f in fr:
        f = _limpia(_POS_ANTERIOR.sub(' ', f))   # «… from immediately accepting to note the recommendation»: vale la de ahora
        if not _SOBRE.search(f) or _LISTA_SIGUE.search(f) or f.endswith(':') or _RECUENTO.search(f) or _PASADO.search(f): continue
        if _PARCIAL.search(f):
            if _VERBO.search(f): out.add('parcial')
            continue
        cf = clase(f, estricto)
        if cf == 'mixta': continue   # «Noted – Ethiopia needs thorough deliberation … to accept the recommendation»
        if estricto and re.match(r'(?i)(?:this|the|these)\s+recommendations?\b', f):
            out.add(cf); continue
        antes, despues = (6, 6) if estricto else (10, 14)
        for m in _SOBRE.finditer(f):
            nucleo = m[0] if not m[1] or not re.fullmatch(r'(?i)accepted|supported|noted|rejected', m[1]) else m[0].replace(m[1] + ' ', '')
            ventana = ' '.join(f[:m.start()].split()[-antes:] + [nucleo] + f[m.end():].split()[:despues])
            cv = clase(ventana, estricto)
            out.add(cv)
            if cv in (APOYADA, NOTA) and cf in (APOYADA, NOTA) and cf != cv: out.add(cf)   # la ventana cortó una negación: las dos
    return out - {None, 'mixta'}



# un cambio de posición escrito con todas las letras: si además el adendo dice cuál es la final, vale esa (no «withdrawal of
# reservation», que es el tema de la recomendación, ni «not in a position to», que solo dice la respuesta)
_CAMBIO_EXPL = re.compile(r'''(?ix)\bchang\w*\s+(?:its|the|our|their)\s+position | \breconsider\w*
  | \b(?:initially|previously|originally)\b[^.;]{0,120}\b(?:is|are)\s+now\b | \bmisplace\w*
  | \bmov(?:e|ed|ing)\s+(?:the\s+)?recommendations?\b[^.;]{0,80}\bcategory\b''')
# la posición de antes, que se quita de la frase para leer la final: «recommendation 146.67, which was initially supported, is now
# noted», «change its position on this recommendation from immediately accepting to note»
_POS_ANTERIOR = re.compile(r'(?i),?\s*which\s+(?:was|were|had\s+been)\s+(?:initially|previously|originally|first)\s+\w+,?'
                           r'|\bfrom\s+(?:immediately\s+)?(?:accepting|supporting|noting)\s+(?=to\b)')
_CATEGORIA = re.compile(r'(?i)\brecommendations?\s+(\d{2,3}\.\d{1,3})\s+(?:in)?to\s+the\s+category\s+of\s+(supported|accepted|noted)\b')
_EXCEPTO = re.compile(r'(?i)\b(?:except|other\s+than|with\s+the\s+exception\s+of|apart\s+from|save\s+for)\s*(?:recommendations?\s*)?$')
_CAMBIO = re.compile(r'''(?ix)\bchang\w*\s+(?:its|the|our|their)\s+position | \bno\s+longer\b
  | \bwithdr[ae]w\w*\s+(?:its\s+|our\s+|the\s+)?(?:support|acceptance|position|recommendation) | \breconsider\w*
  | \bafter\s+(?:further\s+|careful\s+)?consideration | \b(?:initially|previously|originally|earlier)\b[^.;]{0,120}\bnow\b
  | \bmisplace\w* | \bmov(?:e|ed|ing)\s+(?:the\s+)?recommendations?\b | \bnot\s+in\s+a\s+position\s+to\b''')
_FIN_FRASE = re.compile(r'[.;:!?](?=\s)|\n[ \t]*\n')


def contradice_informe(a, inf, validos, textos=None):
    """Números cuya respuesta del informe el adendo pone en duda (un conjunto). Ver revisa_informe()."""
    return set(revisa_informe(a, inf, validos, textos)[0])


def revisa_informe(a, inf, validos, textos=None):
    """(duda, final): `duda`, los números cuya respuesta del informe el adendo pone en duda: una frase del adendo que los nombra
    dice la respuesta contraria o «en parte» («Thailand is not in a position to support recommendation 51.1», «With regard to
    128.54, … Sri Lanka is able to support this recommendation»), o habla de un cambio de posición («initially supported, is now
    noted», «Upon reconsideration…»). `final`: de esos, los que el adendo cambia de forma explícita («… which was initially
    supported, is now noted», «decided to move the recommendation 117.18 into the category of supported recommendations») y cuya
    posición final dice con todas las letras, siempre la misma, en todas las frases que los nombran: {número: respuesta}.
    No es duda que el adendo comente un número sin decir otra cosa («Recommendations 97.76 to 97.81 on the prohibition of corporal
    punishment of children» y la explicación), ni «accepts … all recommendations except 110.1, 110.2…» (habla de las demás), ni
    «Recommendations 119.18, 119.19 and the first part of 120.20» (la parte es de la 120.20)."""
    if not a: return {}, {}
    a, duda, vistas, expl, malas = _paginas(a), {}, {}, set(), set()
    cs = _corridas(a, validos)
    ajenas = _ajenas(a, cs, textos)
    for k, (ini, fin, nums) in enumerate(cs):
        if k in ajenas or not any(inf.get(n) in (APOYADA, NOTA) for n in nums): continue
        ms = [m.end() for m in _FIN_FRASE.finditer(a, max(0, ini - 400), ini)]
        i0 = ms[-1] if ms else max(0, ini - 400)
        m = _FIN_FRASE.search(a, fin)
        f0 = m.start() if m else len(a)
        sl = re.search(r'\n[ \t]*(?=[A-Z•])', a[fin:f0])   # la frase acaba donde empieza otra línea en mayúscula («91.10\nNoted the…»)
        frase = _limpia(a[i0:fin + sl.start()] if sl else a[i0:f0])
        # «… and the first part of 120.20»: esa parte es de otro número
        frase = re.sub(r'(?i)\b(?:the\s+)?(?:first|second|third|other|one|some)\s+parts?\s+of\s+(?:recommendations?\s+)?(\d{2,3}\.\d{1,3})',
                       lambda x: x[0] if x[1] in nums else ' ', frase)
        excepto = bool(_EXCEPTO.search(_limpia(a[i0:ini])))
        c, cambio = (None if excepto else clase(frase)), bool(_CAMBIO.search(frase))
        cf = None if excepto else clase(_POS_ANTERIOR.sub(' ', frase))
        cat = {x[1]: (APOYADA if x[2].lower() in ('supported', 'accepted') else NOTA) for x in _CATEGORIA.finditer(frase)}
        p0 = a.rfind('\n\n', 0, ini); p1 = a.find('\n\n', fin)
        if _CAMBIO_EXPL.search(a[max(p0, ini - 1500, 0):min(p1 if p1 >= 0 else len(a), fin + 1500)]): expl.update(nums)
        # lo que el adendo explica detrás del número, hasta el número siguiente: «124.13 Eliminate the caste system … (Romania)
        # / 18. In Senegal, … This recommendation is rejected.»
        sig = next((x[0] for x in cs if x[0] >= fin), len(a))
        detras = _frases_sobre(a[fin:min(sig, fin + 4000)])
        et = _despues_etiqueta(a, fin, sig)   # «127.6: Not accepted» detrás del número (no la cabecera de la lista siguiente:
        if et and not re.search(r'(?i)following|recommendations?\b|\bbelow\b', a[fin:sig].strip(' \t\n.:;,').split('\n')[0]) \
                and not re.fullmatch(r'(?i)[\s,]*(?:and\s+)?(?:the\s+)?(?:first|second|third|other|one|some)\s+parts?\s+of\s*(?:recommendations?\s*)?', a[fin:sig]):
            detras.add(et)                    # «91.10\nNoted the following recommendations:»)
        for n in nums:
            ri = inf.get(n)
            if ri in (APOYADA, NOTA) and (cambio or c == 'parcial' or c in (APOYADA, NOTA) and c != ri or detras - {ri}): duda[n] = True
            for x in ({cat.get(n, cf)} | detras) - {None}:
                if x in (APOYADA, NOTA): vistas.setdefault(n, set()).add(x)
                else: malas.add(n)   # «en parte» o las dos cosas
    final = {n: next(iter(v)) for n, v in vistas.items()
             if n in duda and n in expl and n not in malas and len(v) == 1 and next(iter(v)) != inf.get(n)}
    return duda, final


def textos_informe(t):
    """{número: texto de la recomendación en el informe} (para ver si el adendo, al copiarla, habla de la misma)."""
    s = R.seccion(t or '')
    if s is None: return {}
    ls, _ = R.listas(s)
    pos = sorted((p, f'{pre}.{k}') for pre, _, ks in ls for k, p in ks)
    return {n: s[p:pos[j + 1][0] if j + 1 < len(pos) else p + 800] for j, (p, n) in enumerate(pos)}


def _palabras(x): return {w for w in re.findall(r'[a-z]{5,}', x.lower())}


def _ajenas(a, cs, textos):
    """Índices de las corridas en las que el adendo copia, detrás del número, el texto de OTRA recomendación: el adendo de Senegal
    (A/HRC/25/4/Add.1) numera «124.13 Eliminate the caste system … (Romania)» la que en el informe es la 125.13; su «124.13» no
    es la 124.13 del informe y lo que diga de ella no vale. Solo cuenta un número suelto seguido de texto de recomendación (no de
    una etiqueta ni de una respuesta) que no comparte casi ninguna palabra con el texto del informe y sí casi todas con el de otra."""
    if not textos: return set()
    out, pal = set(), {n: _palabras(x) for n, x in textos.items()}
    for k, (ini, fin, nums) in enumerate(cs):
        if len(nums) != 1 or nums[0] not in textos: continue
        if a[a.rfind('\n', 0, ini) + 1:ini].strip(' \t•'): continue   # el número abre la línea
        # el texto copiado acaba en la línea en blanco, en el número de párrafo («9.») o con el Estado que la hizo («(Uruguay)»)
        q = re.split(r'\n[ \t]*\n|\n[ \t]*\d{1,3}\.[ \t]*\n|\)[ \t]*;?[ \t]*\n', a[fin:fin + 400])[0]
        q = re.sub(r'^[\s.:–—\-]+', '', q)
        if not re.match(r'[A-Z][a-z]', q) or _POS_ESTRICTO.search(q[:80]) or _NEG.search(q[:80]) or _etiqueta_linea(q.split('\n')[0]):
            continue   # «Supported», «Greece cannot accept this recommendation»: es la respuesta, no el texto copiado
        w = list(dict.fromkeys(re.findall(r'[a-z]{5,}', q.lower())))[:12]
        if len(w) < 5: continue
        def parecido(n): return sum(1 for x in w if x in pal[n]) / len(w)
        if parecido(nums[0]) < 0.25 and max(parecido(n) for n in pal if n != nums[0]) >= 0.75: out.add(k)   # es otra, y se ve cuál
    return out


def respuestas(texto_informe_en, texto_adendo_en, numeros):
    """{número: {'r': 'apoyada'|'tomó nota'|None, 'fuente': 'informe'|'adendo'|None}} para TODOS los `numeros`.
    Si el informe y el adendo no dicen lo mismo, null; salvo que el adendo cambie la posición de forma explícita y diga cuál es la
    final (revisa_informe()): entonces vale esa."""
    inf, textos = del_informe(texto_informe_en or ''), textos_informe(texto_informe_en)
    add = del_adendo(texto_adendo_en or '', set(numeros), textos, {n for n in numeros if inf.get(n) not in (APOYADA, NOTA)})
    duda, final = revisa_informe(texto_adendo_en or '', inf, set(numeros), textos)
    salida = {}
    for n in numeros:
        ri, ra = inf.get(n), add.get(n)
        if ri in (APOYADA, NOTA):
            if n in final and ra in (None, final[n]): salida[n] = {'r': final[n], 'fuente': 'adendo'}
            elif (ra is not None and ra != ri) or n in duda: salida[n] = {'r': None, 'fuente': None}   # el adendo dice otra cosa: no se elige
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
