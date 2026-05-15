#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Watermark PDF – trame ondulée + micro-trame du numéro d'exemplaire.

Trois couches superposées (du fond vers le dessus) :
  1. Micro-trame du NUMÉRO SEUL : dense, décalée, légèrement inclinée.
     → Toute découpe du document, même minuscule, contiendra le numéro.
  2. Trame ondulée générale : vagues diagonales + texte complet.
     → Contexte légal et identification du document.
  3. Header/footer discret : numéro · titre · date.

Usage :
  python watermark_pdf.py source.pdf "Ex 0101" --title "Eval TSA Chambon"
  python watermark_pdf.py source.pdf "Ex 0101" --title "Mon Doc" -d 2026-05-15 -o out.pdf
"""

import argparse
import io
import math
from datetime import date
from pathlib import Path

from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter


# ── Couche 1 : micro-trame numéro ─────────────────────────────────────────────
MICRO_GRAY   = 0.89    # gris très clair
MICRO_SIZE   = 5.5     # pt
MICRO_ANGLE  = 15      # inclinaison de la grille (°)
MICRO_STEP_X = 42      # espacement horizontal (pt) — ~1 numéro tous les 1,5 cm
MICRO_STEP_Y = 19      # espacement vertical (pt)   — ~1 numéro tous les 7 mm

# ── Couche 2 : trame ondulée générale ─────────────────────────────────────────
WAVE_ANGLE  = 32       # angle des sinusoïdes diagonales (°)
WAVE_AMP    = 11       # amplitude (pt)
WAVE_LEN    = 78       # longueur d'onde (pt)
WAVE_SPACE  = 40       # espacement entre lignes parallèles (pt)
WAVE_GRAY   = 0.90     # gris des lignes de vagues
TEXT_GRAY   = 0.85     # gris du texte de trame
TEXT_SIZE   = 7.5      # pt

# ── Couche 3 : header/footer ───────────────────────────────────────────────────
HDR_GRAY    = 0.65
HDR_SIZE    = 6.0


# ───────────────────────────────────────────────────────────────────────────────

def _trame_text(title: str, label: str) -> str:
    return f"Reproduction et copie interdites – {title} – {label} – Confidentiel Personnel"


def _make_watermark_page(width: float, height: float,
                          label: str, title: str, doc_date: str) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(width, height))
    _draw_micro_number(c, width, height, label)
    _draw_wave_trame(c, width, height, _trame_text(title, label))
    _draw_header_footer(c, width, height, label, title, doc_date)
    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()


# ── Couche 1 ───────────────────────────────────────────────────────────────────

def _draw_micro_number(c, width: float, height: float, label: str):
    """
    Grille micro-dense du numéro d'exemplaire SEUL.
    Rangées alternées décalées + légère inclinaison = aspect "trame".
    Toute portion découpée du document contiendra le numéro.
    """
    alpha = math.radians(MICRO_ANGLE)
    ca, sa = math.cos(alpha), math.sin(alpha)

    c.saveState()
    c.setFillGray(MICRO_GRAY)
    c.setFont("Helvetica-Bold", MICRO_SIZE)

    diag = math.sqrt(width ** 2 + height ** 2)
    cx, cy = width / 2, height / 2

    rows = int(diag / MICRO_STEP_Y) + 4
    cols = int(diag / MICRO_STEP_X) + 4

    for row in range(-rows // 2, rows // 2 + 1):
        stagger = (row % 2) * (MICRO_STEP_X / 2)
        for col in range(-cols // 2, cols // 2 + 1):
            gx = col * MICRO_STEP_X + stagger
            gy = row * MICRO_STEP_Y
            # Rotation de la grille autour du centre de la page
            x = cx + gx * ca - gy * sa
            y = cy + gx * sa + gy * ca
            c.saveState()
            c.translate(x, y)
            c.rotate(MICRO_ANGLE)
            c.drawString(0, 0, label)
            c.restoreState()

    c.restoreState()


# ── Couche 2 ───────────────────────────────────────────────────────────────────

def _draw_wave_trame(c, width: float, height: float, full_text: str):
    """
    Deux familles de sinusoïdes diagonales (±WAVE_ANGLE) formant des cellules
    en losange. Texte complet répété en diagonal entre les lignes.
    """
    alpha = math.radians(WAVE_ANGLE)
    freq  = 2 * math.pi / WAVE_LEN
    diag  = math.sqrt(width ** 2 + height ** 2) * 1.1
    cx, cy = width / 2, height / 2
    n     = int(diag / WAVE_SPACE) + 4

    def draw_family(ang: float):
        dx, dy = math.cos(ang), math.sin(ang)
        px, py = -math.sin(ang), math.cos(ang)
        c.setStrokeGray(WAVE_GRAY)
        c.setLineWidth(0.30)
        for i in range(-n // 2, n // 2 + 1):
            bx = cx + px * i * WAVE_SPACE
            by = cy + py * i * WAVE_SPACE
            sx = bx - dx * diag / 2
            sy = by - dy * diag / 2
            path = c.beginPath()
            first = True
            for step in range(0, int(diag) + 1, 3):
                w = WAVE_AMP * math.sin(freq * step)
                x = sx + dx * step + px * w
                y = sy + dy * step + py * w
                if first:
                    path.moveTo(x, y); first = False
                else:
                    path.lineTo(x, y)
            c.drawPath(path)

    c.saveState()
    draw_family(alpha)
    draw_family(-alpha)

    # Texte entre les lignes de la famille +alpha
    c.setFillGray(TEXT_GRAY)
    c.setFont("Helvetica", TEXT_SIZE)
    dx, dy = math.cos(alpha), math.sin(alpha)
    px, py = -math.sin(alpha), math.cos(alpha)
    str_w = len(full_text) * TEXT_SIZE * 0.55 + 18

    for i in range(-n // 2, n // 2 + 1):
        bx = cx + px * (i + 0.5) * WAVE_SPACE
        by = cy + py * (i + 0.5) * WAVE_SPACE
        sx = bx - dx * diag / 2
        sy = by - dy * diag / 2
        for j in range(-1, int(diag / str_w) + 2):
            tx = sx + dx * j * str_w
            ty = sy + dy * j * str_w
            c.saveState()
            c.translate(tx, ty)
            c.rotate(WAVE_ANGLE)
            c.drawString(0, 0, full_text)
            c.restoreState()

    c.restoreState()


# ── Couche 3 ───────────────────────────────────────────────────────────────────

def _draw_header_footer(c, width: float, height: float,
                         label: str, title: str, doc_date: str):
    c.saveState()
    c.setFillGray(HDR_GRAY)
    c.setFont("Helvetica", HDR_SIZE)
    m = 18
    stamp = f"{label}  ·  {title}  ·  {doc_date}"
    c.drawString(m, height - 10, stamp)
    c.drawRightString(width - m, height - 10, stamp)
    c.setStrokeGray(HDR_GRAY)
    c.setLineWidth(0.25)
    c.line(m, height - 14, width - m, height - 14)
    c.line(m, 14, width - m, 14)
    c.drawString(m, 5, stamp)
    c.drawRightString(width - m, 5, stamp)
    c.restoreState()


# ── Application ────────────────────────────────────────────────────────────────

def watermark_pdf(src: Path, label: str, title: str, doc_date: str, dst: Path):
    reader = PdfReader(str(src))
    writer = PdfWriter()
    cache: dict = {}

    for page in reader.pages:
        box = page.mediabox
        pw, ph = float(box.width), float(box.height)
        key = (round(pw, 1), round(ph, 1))
        if key not in cache:
            cache[key] = _make_watermark_page(pw, ph, label, title, doc_date)

        # Trame comme base, contenu du doc par-dessus
        wm_page = PdfReader(io.BytesIO(cache[key])).pages[0]
        wm_page.merge_page(page)
        writer.add_page(wm_page)

    with open(dst, "wb") as f:
        writer.write(f)
    print(f"[OK] {dst}")


def main():
    p = argparse.ArgumentParser(description="Watermark ondulé + micro-trame numéro pour PDF")
    p.add_argument("source",         help="PDF source")
    p.add_argument("label",          help="Numéro d'exemplaire  (ex: 'Ex 0101')")
    p.add_argument("--title",        help="Titre du document (non confidentiel)",
                   default="Document")
    p.add_argument("-d", "--date",   help="Date (défaut = aujourd'hui)",
                   default=date.today().isoformat())
    p.add_argument("-o", "--output", help="PDF de sortie")
    args = p.parse_args()

    src = Path(args.source)
    if not src.exists():
        p.error(f"Introuvable : {src}")
    dst = Path(args.output) if args.output else src.with_stem(src.stem + "_wm")
    watermark_pdf(src, args.label, args.title, args.date, dst)


if __name__ == "__main__":
    main()
