#!/usr/bin/env python3
"""Iconos de la web instalable (fase 6 del plan de diseño, docs/PLAN_DISENO_UX.md).

Dibuja el isotipo de Sukima Labs (las mismas coordenadas que assets/marca/isotipo_white.svg e isotipo_color.svg:
dos marcos en blanco y la puerta en cian) sobre el grafito de la marca, y guarda los PNG que pide
manifest.webmanifest:

  assets/marca/icono_192.png           icono normal (purpose «any»)
  assets/marca/icono_512.png           icono normal (purpose «any»)
  assets/marca/icono_maskable_512.png  icono «maskable»: el sistema lo recorta en círculo o en gota, así que el
                                       isotipo cabe entero en la zona segura (el círculo central del 80 %)

  python3 -I scripts/iconos_pwa.py     # necesita Pillow
"""
import os
from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAFITO, BLANCO, CIAN = (0x10, 0x13, 0x1C), (0xFF, 0xFF, 0xFF), (0x14, 0xC6, 0xD4)
# Isotipo en su caja de 200 × 200 (assets/marca/isotipo_*.svg).
TRAZOS = [
    ([(18, 174), (18, 38), (180, 14), (180, 174), (160, 174), (160, 39), (38, 57), (38, 174)], BLANCO),
    ([(52, 170), (52, 80), (142, 59), (142, 79), (72, 96), (72, 170)], BLANCO),
    ([(96, 167), (96, 109), (143, 93), (143, 173)], CIAN),
]
X0, Y0, X1, Y1 = 18, 14, 180, 174  # caja que ocupa el dibujo


def icono(lado, ocupa):
    """Lienzo cuadrado de `lado` px; el isotipo ocupa `ocupa` (0–1) del lado, centrado."""
    k = 4  # se dibuja a 4× y se reduce, para que los bordes salgan suaves
    L = lado * k
    im = Image.new("RGB", (L, L), GRAFITO)
    d = ImageDraw.Draw(im)
    esc = L * ocupa / max(X1 - X0, Y1 - Y0)
    dx = (L - (X1 - X0) * esc) / 2 - X0 * esc
    dy = (L - (Y1 - Y0) * esc) / 2 - Y0 * esc
    for puntos, color in TRAZOS:
        d.polygon([(x * esc + dx, y * esc + dy) for x, y in puntos], fill=color)
    return im.resize((lado, lado), Image.LANCZOS)


def main():
    destino = os.path.join(RAIZ, "assets", "marca")
    icono(192, 0.72).save(os.path.join(destino, "icono_192.png"), optimize=True)
    icono(512, 0.72).save(os.path.join(destino, "icono_512.png"), optimize=True)
    # Zona segura de un icono maskable: un círculo del 80 % del lado. Un cuadrado cabe entero si su lado es
    # 0,8 / √2 ≈ 0,566 del icono; con 0,54 queda un pequeño margen.
    icono(512, 0.54).save(os.path.join(destino, "icono_maskable_512.png"), optimize=True)


if __name__ == "__main__":
    main()
