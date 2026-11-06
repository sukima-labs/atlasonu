from pathlib import Path
import subprocess,re,json,zipfile,hashlib
p=Path('/mnt/data/ATLAS_ONU_publicacion/index.html');s=p.read_text()
assert 'id="recuperar"' in s
assert 'data-page="recuperar"' in s
assert 'E/1980/13' in s
assert '1980' in s
assert 'PENDIENTE' in s
assert 'https://github.com/sukima-labs/onu-arqueologia-documental' in s
assert len(re.findall(r'<section id="[^\"]+"',s))>=7
assert 'function filterMandates' in s and 'function recoverDocument' in s
print('STATIC PASS: required functional structures')
# Chromium headless browser timed out in this environment; don't report as passed.
print('BROWSER SMOKE: NOT COMPLETED (headless Chromium timed out)')
# bundling
root=Path('/mnt/data/ATLAS_ONU_publicacion')
(root/'README.md').write_text('''# ATLAS ONU — Arqueología documental

**Autor:** Jeisson Arley Osorio Mesa · 2026. Proyecto académico independiente.

## Abrir

Abrir `index.html` desde Chrome, Edge, Firefox o Safari; no requiere instalar código. Para páginas web públicas se puede alojar con GitHub Pages.

## Qué funciona

- Navegación local, catálogo y búsqueda por palabras, figura y órgano.
- Traces históricas con alertas, nomenclatura ONU y explicación de selección de relatores.
- Módulo **Recuperar documentos**: permite identificar el acto jurídico frente al informe que lo reproduce; buscar por símbolo y tema; ofrece rutas de acceso alternativas y un ejemplo comprobado (Comisión de Derechos Humanos, resolución 20 (XXXVI) de 1980, en E/1980/13–E/CN.4/1408, pp. 180–181).
- Panel estadístico limitado a la muestra de 28 mandatos; no corresponde al universo completo de ONU.

## No implementado ni acreditado

- Descarga o recuperación automática masiva de PDFs y cotejo integral de documentos históricos.
- Sincronización automática de mandatos, titulares, informes y cifras con servidores externos.
- Mapas geográficos, permisos diferenciados y catalogación exhaustiva.
- Validación jurídica del 100% de referencias o enlaces.

El módulo de recuperación sugiere varias rutas oficiales, pero **una ruta no es un documento recuperado**. No afirmar que un enlace está verificado sin cotejar el texto y metadatos del documento primario. Los documentos históricos podrían estar integrados en informes de sesión o no digitalizados.

## Fuentes

- ONU Biblioteca Digital: https://digitallibrary.un.org/
- ONU Documentos: https://docs.un.org/
- UN Library, búsqueda: https://research.un.org/en/docs/find/documents
- Registro histórico del WGEID: https://digitallibrary.un.org/record/96859?ln=en

## Autoría

© 2026 Jeisson Arley Osorio Mesa. Todos los derechos reservados. La publicación pública por sí misma no constituye licencia abierta. Este trabajo no representa ni está avalado por la ONU o la Universidad de Alcalá.
''')
(root/'tests').mkdir(exist_ok=True)
(root/'tests'/'RESULTADOS.md').write_text('''# Pruebas de la versión local

- Verificación estática de secciones, navegación, panel de recuperación y enlace de autoría: **superada**.
- Ejecución del JavaScript mediante `node --check`: **superada**.
- Prueba real en Chromium: **no completada**, por tiempo de espera agotado en el entorno.
- Resolución original 20 (XXXVI): acto y ubicación acreditados mediante Biblioteca Digital ONU (1980, informe E/1980/13–E/CN.4/1408, pp. 180–181).
- Auditoría exhaustiva de 28 mandatos, 11 trazas y enlaces externos: **no completada**.
- Sincronización web automática: **no implementada**.
- Publicación GitHub / Pages: **pendiente de permisos de escritura; el conector respondió 403**.
''')
zip_path=Path('/mnt/data/ATLAS_ONU_CORREGIDO_ARQUEOLOGIA_2026.zip')
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
 for file in [root/'index.html',root/'README.md',root/'tests'/'RESULTADOS.md']:
  z.write(file,file.relative_to(root))
print('ZIP',zip_path,'bytes',zip_path.stat().st_size,'sha256',hashlib.sha256(zip_path.read_bytes()).hexdigest()[:16])
