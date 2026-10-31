#!/usr/bin/env python3
"""Genera data/cambios.atom (Atom 1.0) a partir de data/historial_cambios.json: «qué cambió» en las fuentes oficiales.
Uso: python3 -I scripts/generar_feed_cambios.py   (sin red; solo lee y escribe data/)"""
import json, html, xml.etree.ElementTree as ET
ENTRADAS = 'data/historial_cambios.json'
SALIDA = 'data/cambios.atom'
ATOM = 'http://www.w3.org/2005/Atom'
ET.register_namespace('', ATOM)

def texto(parent, tag, valor):
    el = ET.SubElement(parent, '{%s}%s' % (ATOM, tag)); el.text = valor; return el

historial = json.load(open(ENTRADAS, encoding='utf-8'))
feed = ET.Element('{%s}feed' % ATOM)
texto(feed, 'title', 'ATLAS ONU: qué cambió en las fuentes oficiales')
texto(feed, 'subtitle', 'Cambios detectados en el índice de mandatos de OHCHR y en la Biblioteca Digital de la ONU. Catálogo no oficial.')
texto(feed, 'id', 'tag:atlas-onu,2026:cambios')
ultima = historial[0]['fecha'] + 'T00:00:00Z' if historial else '2026-01-01T00:00:00Z'
texto(feed, 'updated', ultima)
ET.SubElement(feed, '{%s}rights' % ATOM).text = 'Código AGPL-3.0; datos de las fuentes oficiales de la ONU. Autoría visible obligatoria.'
for h in historial:
    e = ET.SubElement(feed, '{%s}entry' % ATOM)
    texto(e, 'title', '%s: %d cambio(s)' % (h['fecha'], len(h['cambios'])))
    texto(e, 'id', 'tag:atlas-onu,%s:cambios' % h['fecha'])
    texto(e, 'updated', h['fecha'] + 'T00:00:00Z')
    cuerpo = ''.join('<li>%s</li>' % html.escape(c['texto']) for c in h['cambios'])
    c = ET.SubElement(e, '{%s}content' % ATOM, type='html'); c.text = '<ul>%s</ul>' % cuerpo
ET.indent(feed, space='  ')
ET.ElementTree(feed).write(SALIDA, encoding='utf-8', xml_declaration=True)
print('feed:', SALIDA, len(historial), 'entradas')
