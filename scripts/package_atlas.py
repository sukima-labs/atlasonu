from pathlib import Path
import zipfile,hashlib,subprocess,json,re
root=Path('/mnt/data/ATLAS_ONU_publicacion')
readme='''# ATLAS ONU · Arqueología documental de procedimientos especiales

**Autor y dirección académica:** Jeisson Arley Osorio Mesa (2026).

Proyecto educativo independiente, sin respaldo ni aval oficial de Naciones Unidas ni de la Universidad de Alcalá.

## Inicio inmediato

Abre `index.html` en Chrome, Edge, Firefox o Safari. Al publicarse mediante GitHub Pages, el mismo archivo puede servirse como página de inicio del sitio. No se necesita instalar aplicaciones ni escribir código. Las búsquedas y la navegación funcionan sin conexión a internet; los enlaces externos requieren conexión.

## Funciones actuales

- Portada visual, navegación y estadísticas calculadas sobre una **muestra de 28 mandatos**, no el total mundial vigente.
- Buscador temático y bilingüe (español/inglés); filtros por temática, figura, órgano y año.
- Fichas sobre relatores especiales, expertos independientes y grupos de trabajo.
- Nomenclatura y jerarquía: Comisión de Derechos Humanos, ECOSOC, Asamblea General y Consejo de Derechos Humanos.
- Arqueología con 11 rastros históricos, 9 alertas documentales y ejemplo recuperado de la resolución 20 (XXXVI) de 1980, cuyo texto consta en E/1980/13–E/CN.4/1408, pp. 180–181.
- Recuperación **guiada**, no descarga masiva: propone rutas de búsqueda en Biblioteca Digital ONU y docs.un.org. La propuesta de búsqueda no equivale a un documento cotejado.
- Proceso de selección de expertos, enlaces a fuentes oficiales y exportación de resultados CSV.

## Limitaciones verificadas

- **No hay sincronización automática** con bases de la ONU al abrir el documento. Los datos son una muestra local; se ofrecen enlaces a fuentes oficiales actuales.
- No incluye cartografía mundial ni estadísticas oficiales por país; representar la muestra como distribución global sería engañoso.
- No es una auditoría jurídica exhaustiva: varias resoluciones históricas, renovaciones y enlaces requieren cotejo del original.
- El archivo público HTML/Excel no concede control de edición: para modificar el repositorio se aplican permisos de GitHub. La protección de hojas Excel solo previene cambios accidentales.
- La aplicación no recolecta ni transmite información personal por sí misma; al abrir enlaces externos se aplican las políticas del sitio de destino.

## Evidencia reproducible de calidad

Ejecutar `node tests/smoke.cjs` tras descargar el proyecto. La prueba cubre carga de catálogo, búsqueda en español e inglés, vacío de resultados, filtro histórico, recuperación de símbolo, detalle y enlace de autoría. No sustituye una prueba de accesibilidad y comportamiento en todos los navegadores.

## Referencias oficiales

- https://www.ohchr.org/es/special-procedures-human-rights-council
- https://digitallibrary.un.org/
- https://docs.un.org/
- https://digitallibrary.un.org/record/96859?ln=en

## Autoría y reutilización

© 2026 Jeisson Arley Osorio Mesa. Todos los derechos reservados. La distribución pública por GitHub no otorga automáticamente permisos de reutilización más allá de los concedidos por la ley. Los documentos de Naciones Unidas mantienen sus condiciones de uso correspondientes.
'''
(root/'README.md').write_text(readme,encoding='utf-8')
run=subprocess.run(['node',str(root/'tests'/'smoke.cjs')],capture_output=True,text=True)
if run.returncode: raise RuntimeError(run.stderr)
(root/'tests'/'RESULTADOS.md').write_text('# Validación de ATLAS ONU (27 de octubre de 2026)\n\n**Pruebas de lógica:** 14 comprobaciones ejecutadas correctamente bajo Node VM simulando el DOM.\n\nSalida: `'+run.stdout.strip()+'`\n\n**No probado:** interacción real en Chromium (el proceso agota el tiempo de ejecución), compatibilidad total en navegadores móviles, actualización online y cotejo del universo completo de mandatos.\n\n**GitHub:** repositorio público existente, integración de escritura rechazada por error `403 Resource not accessible by integration`. Este ZIP no constituye un commit ni push confirmado.\n',encoding='utf-8')
zip_path=Path('/mnt/data/ATLAS_ONU_V06_AUDITADA_PUBLICACION.zip')
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
 for path in root.rglob('*'):
  if path.is_file() and not path.name.startswith('.'):
   z.write(path,path.relative_to(root))
with zipfile.ZipFile(zip_path) as z:
 broken=z.testzip();assert not broken,broken
 names=z.namelist();assert all(x in names for x in ['index.html','README.md','tests/smoke.cjs','datos/atlas-onu-catalogo.xlsx'])
print(json.dumps({'zip':str(zip_path),'files':names,'bytes':zip_path.stat().st_size,'sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest(),'tests':run.stdout.strip()},ensure_ascii=False))
