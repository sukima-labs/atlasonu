#!/usr/bin/env python3
"""T95 · Traduce los textos de interfaz que faltan (idiomas/es.json -> en, fr, ar, zh, ru) con un modelo abierto que corre
en el servidor del proyecto (Qwen3-4B-Instruct-2507 con llama.cpp), sin servicios externos. Decidido el 13-11-2026 (#321).

Solo toca lo que falta: un texto que ya tiene traducción no se cambia. Cada traducción pasa una comprobación:
  - las mismas etiquetas HTML y los mismos marcadores ({n}, {fecha}…), en el mismo orden;
  - en árabe, chino y ruso, que esté escrita en su alfabeto (no se queda en español);
  - que no esté vacía, que no repita el original y que no tenga una longitud disparatada.
Si falla, se repite una vez avisando del fallo; si vuelve a fallar, el texto se queda sin traducir (la web lo enseña en
español) y queda para la tanda de `atlas-rapido`. Lo traducido aquí se anota en idiomas/automaticas.json para la revisión
de personas nativas (#262). Después se regeneran data/idiomas/<ln>.js (scripts/idiomas.py).

El script arranca su propio llama-server en 127.0.0.1 y lo para al terminar. En sk-atlas se corre como `atlas` dentro de
atlas-trad.slice (lo programa `maquina`), nunca a la vez que atlas-textos.

Uso: traducir_local.py [--idiomas en,fr] [--max N] [--probar]   (--probar: no escribe nada; enseña lo que haría)
Variables: ATLAS_MODELO, ATLAS_LLAMA_SERVER, ATLAS_LLM_PUERTO, ATLAS_LLM_HILOS."""
import json, os, re, subprocess, sys, time, urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDI = os.path.join(RAIZ, "idiomas")
MODELO = os.environ.get("ATLAS_MODELO", "/var/lib/atlas/modelos/gguf/Qwen3-4B-Instruct-2507-Q4_K_M.gguf")
SERVIDOR = os.environ.get("ATLAS_LLAMA_SERVER", "/usr/local/bin/llama-server")
PUERTO = int(os.environ.get("ATLAS_LLM_PUERTO", "8790"))
HILOS = os.environ.get("ATLAS_LLM_HILOS", "3")
NOMBRE = {"en": "English", "fr": "French", "ar": "Arabic", "zh": "Simplified Chinese", "ru": "Russian"}
ALFABETO = {"ar": r"[؀-ۿ]", "zh": r"[一-鿿]", "ru": r"[Ѐ-ӿ]"}
# Términos fijos: se toman de las traducciones ya revisadas, no se escriben aquí
GLOSARIO = ["Examen Periódico Universal", "Consejo de Derechos Humanos", "Relatores y relatoras", "Procedimientos especiales",
            "Tratados y comités", "Observaciones finales", "Países", "Siglas"]


def lee(ln):
    with open(os.path.join(IDI, ln + ".json"), encoding="utf-8") as f:
        return json.load(f)


def escribe(nombre, d):
    with open(os.path.join(IDI, nombre + ".json"), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
        f.write("\n")


def marcas(s):
    return re.findall(r"</?[a-zA-Z]+[^>]*>|\{\w+\}", s)


def valida(es, tr, ln):
    """None si la traducción vale; si no, el motivo (en inglés: se le devuelve al modelo en el reintento)."""
    if not tr.strip():
        return "the answer was empty"
    if marcas(tr) != marcas(es):
        return "HTML tags and placeholders must be exactly %s, in this order" % (marcas(es) or "none")
    # Palabras corrientes (en minúscula y de 4 letras o más): un nombre propio o una marca («Chrome», «CEDAW») se puede quedar igual
    corrientes = re.findall(r"(?<![\w])[a-záéíóúñü]{4,}", re.sub(r"<[^>]+>|\{\w+\}", "", es))
    if ln in ALFABETO and corrientes and not re.search(ALFABETO[ln], tr):
        return "the answer must be written in %s" % NOMBRE[ln]
    if tr.strip() == es.strip() and corrientes:
        return "the answer repeated the Spanish text"
    if "ATLAS ONU" in es and "ATLAS ONU" not in tr:
        return "keep the name ATLAS ONU exactly as written"
    if tr.lstrip().startswith("[") and not es.lstrip().startswith("["):
        return "answer with the translation only, without notes or brackets"
    if len(tr) > 4 * len(es) + 40:
        return "the answer is much longer than the source; translate only the text"
    return None


def pantallas():
    """Texto de cada <section id=…> de index.html, para decirle al modelo en qué pantalla sale cada frase."""
    html = open(os.path.join(RAIZ, "index.html"), encoding="utf-8").read()
    trozos = re.split(r'(<section id="[^"]+")', html)
    out, actual = [], ""
    for t in trozos:
        m = re.match(r'<section id="([^"]+)"', t)
        if m:
            actual = m.group(1)
        else:
            out.append((actual, t))
    return out


def contexto(k, secs):
    return next((s for s, t in secs if s and k in t), "")


def sistema(ln, glos, pantalla=""):
    g = "\n".join("- %s => %s" % (a, b) for a, b in glos)
    donde = ("\nThe text appears on the site section «%s»." % pantalla) if pantalla else ""
    return ("You translate user-interface text of ATLAS ONU, a free website about the United Nations human rights system, "
            "from Spanish into %s.\nRules: output ONLY the translation, nothing else. Keep every HTML tag (<b>, <a>, <span>, ...) "
            "and every placeholder like {n} or {fecha} exactly as in the source, same count and order. Never translate the name "
            "ATLAS ONU (keep it exactly) nor UN document symbols (e.g. A/HRC/RES/5/1, CEDAW). Use the official United Nations terminology in %s. Address "
            "the reader informally where the language allows. Keep it short and plain. If the source is a fragment of a "
            "sentence, translate it as a fragment.%s\nFixed glossary:\n%s" % (NOMBRE[ln], NOMBRE[ln], donde, g))


def pide(mensajes):
    cuerpo = json.dumps({"messages": mensajes, "temperature": 0, "max_tokens": 600, "cache_prompt": True}).encode()
    q = urllib.request.Request("http://127.0.0.1:%d/v1/chat/completions" % PUERTO, cuerpo, {"Content-Type": "application/json"})
    with urllib.request.urlopen(q, timeout=600) as r:
        t = json.load(r)["choices"][0]["message"]["content"]
    return re.sub(r"<think>.*?</think>", "", t, flags=re.S).strip()


def traduce(es, ln, glos, pantalla):
    msj = [{"role": "system", "content": sistema(ln, glos, pantalla)}, {"role": "user", "content": es}]
    tr = pide(msj)
    fallo = valida(es, tr, ln)
    if fallo:   # un reintento, diciéndole qué falló
        msj += [{"role": "assistant", "content": tr}, {"role": "user", "content": "Not valid: %s. Answer again with only the corrected translation." % fallo}]
        tr = pide(msj)
        fallo = valida(es, tr, ln)
    return tr, fallo


def arranca():
    if not os.path.exists(MODELO) or not os.path.exists(SERVIDOR):
        sys.exit("Falta el modelo (%s) o llama-server (%s): esto corre en sk-atlas (T95)." % (MODELO, SERVIDOR))
    p = subprocess.Popen([SERVIDOR, "-m", MODELO, "-t", HILOS, "-c", "4096", "--host", "127.0.0.1", "--port", str(PUERTO)],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(180):
        try:
            urllib.request.urlopen("http://127.0.0.1:%d/health" % PUERTO, timeout=2)
            return p
        except Exception:
            if p.poll() is not None:
                sys.exit("llama-server terminó al arrancar (código %s)" % p.returncode)
            time.sleep(1)
    p.terminate()
    sys.exit("llama-server no respondió en 3 minutos")


def main(args):
    idiomas = next((a.split("=", 1)[1] for a in args if a.startswith("--idiomas=")), None)
    if "--idiomas" in args:
        idiomas = args[args.index("--idiomas") + 1]
    idiomas = [x for x in (idiomas or ",".join(NOMBRE)).split(",") if x in NOMBRE]
    tope = int(args[args.index("--max") + 1]) if "--max" in args else None
    probar = "--probar" in args
    es = lee("es")
    try:
        auto = lee("automaticas")
    except FileNotFoundError:
        auto = {"_": "T95: textos traducidos por el modelo local (scripts/traducir_local.py), pendientes de revisión por personas nativas (#262). Al revisar uno, se quita de aquí."}
    falta = {ln: [k for k in es if not str(lee(ln).get(k, "")).strip()][:tope] for ln in idiomas}
    if not any(falta.values()):
        print("Nada que traducir.")
        return 0
    secs = pantallas()
    srv = arranca()
    hechos, fallidos = 0, []
    try:
        for ln in idiomas:
            d = lee(ln)
            glos = [(g, d[g]) for g in GLOSARIO if d.get(g)]
            for k in falta[ln]:
                t0 = time.time()
                tr, fallo = traduce(k, ln, glos, contexto(k, secs))
                if fallo:
                    fallidos.append((ln, k, fallo))
                    print("✗ %s %.1fs %s | %s" % (ln, time.time() - t0, k[:70], fallo), flush=True)
                    continue
                d[k] = tr
                auto.setdefault(ln, [])
                if k not in auto[ln]:
                    auto[ln].append(k)
                hechos += 1
                print("✓ %s %.1fs %s => %s" % (ln, time.time() - t0, k[:60], tr[:60]), flush=True)
            if not probar:
                escribe(ln, d)
    finally:
        srv.terminate()
        try:
            srv.wait(20)
        except subprocess.TimeoutExpired:
            srv.kill()
    if not probar and hechos:
        escribe("automaticas", auto)
        subprocess.run([sys.executable, "-I", os.path.join(RAIZ, "scripts", "idiomas.py")], check=True)
    print("Traducidos: %d · sin traducir (para la tanda de atlas-rapido): %d" % (hechos, len(fallidos)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
