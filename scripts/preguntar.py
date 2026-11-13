#!/usr/bin/env python3
"""Preguntar a los documentos (fase 4): respuesta redactada por IA, solo con párrafos de la ONU y con su cita.

1. Busca los párrafos más pertinentes en el índice de texto completo (palabras + significado, texto_completo.py).
2. Se los pasa a un modelo de OpenCode Go (API compatible con OpenAI) con la orden de responder SOLO con ellos y
   citar cada afirmación con [n]. Si no bastan, debe decirlo.
3. Comprueba la respuesta: se quitan las citas a párrafos que no se le dieron; sin ninguna cita válida, no se da
   la respuesta y se muestran solo los párrafos.

Qué sale de aquí: la pregunta y párrafos públicos de la ONU. Ni IP, ni cookies, ni nada de quien pregunta. La web
solo pregunta cuando la persona pulsa el botón y le avisa antes. La clave va en OPENCODE_GO_API_KEY (fuera del
repositorio); sin clave, la función no está disponible.
  python3 scripts/preguntar.py "¿Pueden los relatores visitar un país sin invitación?"
"""
import json, os, re, sqlite3, sys, threading, time, urllib.request, uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import texto_completo as tc  # noqa: E402

API = os.environ.get("OPENCODE_GO_URL", "https://opencode.ai/zen/go/v1") + "/chat/completions"
MODELO = os.environ.get("ATLAS_MODELO_IA", "glm-5.3-flash")
SESION = "atlas-" + str(uuid.uuid4())          # la API exige x-opencode-session; identifica el uso de ATLAS
MAX_POR_MIN = 10                               # preguntas nuevas por minuto, todas las visitas juntas
TTL, MAX_CACHE, N_PARRAFOS = 3600, 300, 8
_cache, _veces, _lock = {}, [], threading.Lock()

SISTEMA = """Eres el asistente documental de ATLAS ONU. Respondes en español, con claridad y en pocas frases, a partir
EXCLUSIVAMENTE de los extractos numerados de documentos oficiales de la ONU que se te dan.
Reglas:
- Cada afirmación lleva su cita con el número del extracto entre corchetes, por ejemplo [2] o [1][3].
- No uses nada que no esté en los extractos: ni memoria, ni suposiciones, ni otros documentos.
- Si los extractos no bastan para responder, dilo en una frase y no inventes.
- Si un extracto está en inglés, tradúcelo al citarlo.
- No des consejos jurídicos personales; describe lo que dicen los documentos.
- No hagas preguntas ni ofrezcas seguir la conversación: quien lee no puede contestarte."""
MAX_TEXTO = 1200                               # caracteres de cada párrafo que recibe la IA

# Párrafos sin contenido: líneas del índice (con puntos de relleno) y la portada de los informes
# (los primeros párrafos, con «Adición», «Nota de la Secretaría» o solo el título y la autora).
_INDICE = re.compile(r"(\.\s?){6,}|…{3,}")
_PORTADA = re.compile(r"\b(Adición|Addendum|Nota de la Secretaría|Note by the Secretariat|Distr\.|Original:)", re.I)
_TITULO = re.compile(r"^\s*(Informe|Report)\b", re.I)


def es_relleno(texto, n):
    """True si el párrafo no dice nada por sí mismo: índice, encabezado suelto o portada."""
    t = re.sub(r"\s+", " ", texto).strip()
    if _INDICE.search(t) or len(t) < 60 or (len(t) < 100 and t[-1] not in ".;:"):
        return True   # índice o encabezado suelto («Acceso al agua potable», «Relatora Especial … (solicitada en 2009)»)
    return int(n or 0) <= 3 and (bool(_PORTADA.search(t)) or (_TITULO.match(t) and len(t) < 200))


class NoDisponible(Exception):
    pass


def disponible():
    return bool(os.environ.get("OPENCODE_GO_API_KEY"))


def _llamar(mensajes):
    if not disponible():
        raise NoDisponible("sin clave")
    body = {"model": MODELO, "messages": mensajes, "temperature": 0.1, "max_tokens": 1000}
    req = urllib.request.Request(API, data=json.dumps(body).encode(), headers={
        "Authorization": "Bearer " + os.environ["OPENCODE_GO_API_KEY"], "Content-Type": "application/json",
        "x-opencode-session": SESION, "User-Agent": "ATLAS-ONU/1.0 (+https://github.com/sukima-labs/atlasonu)"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.load(r)["choices"][0]["message"]["content"] or ""


def limpiar_citas(texto, n):
    """Quita las citas [k] con k fuera de 1..n. Devuelve (texto, citas válidas usadas en orden)."""
    usadas = []

    def sub(m):
        k = int(m.group(1))
        if 1 <= k <= n:
            if k not in usadas:
                usadas.append(k)
            return m.group(0)
        return ""
    return re.sub(r"\[(\d{1,2})\]", sub, texto).strip(), usadas


def _sin_marcas(t):
    return t.replace(tc.INI, "").replace(tc.FIN, "")


def _recortar(t):
    t = re.sub(r"\s+", " ", t).strip()
    return t if len(t) <= MAX_TEXTO else t[:MAX_TEXTO].rsplit(" ", 1)[0] + " …"


def responder(con, pregunta, clave=None):
    pregunta = re.sub(r"\s+", " ", pregunta).strip()
    ck = pregunta.lower()
    ahora = time.time()
    with _lock:
        hit = _cache.get(ck)
        if hit and ahora - hit[0] < TTL:
            return hit[1]
    parrafos, vistos = [], set()   # un extracto por documento: el mismo párrafo en es y en gastaría dos citas
    for p in tc.buscar_hibrido(con, pregunta, limite=N_PARRAFOS * 6, por_doc=3, clave=clave):
        if p["simbolo"] in vistos or len(parrafos) >= N_PARRAFOS:
            continue
        fila = con.execute("SELECT texto FROM parrafos WHERE simbolo = ? AND lengua = ? AND n = ?",
                           (p["simbolo"], p["lengua"], p["parrafo"])).fetchone()
        texto = fila[0] if fila else _sin_marcas(p["fragmento"])
        if es_relleno(texto, p["parrafo"]):
            continue
        vistos.add(p["simbolo"])
        parrafos.append(p)
        p["_texto"] = texto
    if not parrafos:
        return {"pregunta": pregunta, "respuesta": "", "citas": [], "parrafos": [], "motivo": "sin_parrafos"}
    with _lock:
        _veces[:] = [t for t in _veces if ahora - t < 60]
        if len(_veces) >= MAX_POR_MIN:
            raise RuntimeError("limite")
        _veces.append(ahora)
    extractos = "\n\n".join(f"[{i}] {p['simbolo']} ({p.get('tipo') or 'Resolución'}, {p['lengua']}, párrafo {p['parrafo']}): "
                            f"{_recortar(p.pop('_texto'))}" for i, p in enumerate(parrafos, 1))
    texto = _llamar([{"role": "system", "content": SISTEMA},
                     {"role": "user", "content": f"Extractos:\n{extractos}\n\nPregunta: {pregunta}"}])
    texto, usadas = limpiar_citas(texto, len(parrafos))
    out = {"pregunta": pregunta, "modelo": MODELO, "parrafos": parrafos, "citas": usadas,
           "respuesta": texto if usadas else "", "motivo": "" if usadas else "sin_citas"}
    with _lock:
        if len(_cache) >= MAX_CACHE:
            _cache.clear()
        _cache[ck] = (ahora, out)
    return out


if __name__ == "__main__":
    db = tc.ruta_db()
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    r = responder(con, " ".join(sys.argv[1:]), clave=os.path.getmtime(db))
    print(r["respuesta"] or f"(sin respuesta: {r['motivo']})")
    for k in r["citas"]:
        p = r["parrafos"][k - 1]
        print(f"  [{k}] {p['simbolo']} [{p['lengua']}] §{p['parrafo']}")
