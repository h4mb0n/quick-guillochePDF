#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import io
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter
from pathlib import Path

from watermark_pdf import _make_watermark_page


def main():
    parser = argparse.ArgumentParser(
        description="Génération PDF – Déclaration de confidentialité (exemplaire numéroté + watermark)"
    )
    parser.add_argument("param1", help="Numéro d'exemplaire (ex: Ex 001)")
    parser.add_argument("--param2", help="Identifiant du document (par défaut = param1)")
    parser.add_argument("-d", "--date", help="Date à graver (défaut = aujourd'hui)",
                        default=date.today().isoformat())
    parser.add_argument("-o", "--output", help="PDF de sortie")

    args = parser.parse_args()

    param1 = args.param1
    param2 = args.param2 if args.param2 else param1
    doc_date = args.date

    output = (
        Path(args.output)
        if args.output
        else Path(f"exemplaire_{param1.replace(' ', '_')}.pdf")
    )

    w, h = A4

    # --- 1. Générer le contenu brut ---
    raw_buf = io.BytesIO()
    c = canvas.Canvas(raw_buf, pagesize=A4)

    text = c.beginText(50, h - 80)
    text.setFont("Helvetica", 11)

    lines = [
        f"EXEMPLAIRE N° {param1}",
        "",
        f"Le présent document, identifié comme {param2}, est remis à titre strictement personnel.",
        "",
        "Le détenteur de cet exemplaire reconnaît que :",
        "",
        "- cet exemplaire est unique et individualisé ;",
        "- toute reproduction, même partielle, est interdite ;",
        "- toute transmission à un tiers est interdite ;",
        "- toute conservation hors nécessité est interdite.",
        "",
        "Le détenteur s'engage à :",
        "",
        "- conserver l'exemplaire sous sa responsabilité exclusive ;",
        "- empêcher tout accès non autorisé ;",
        "- procéder à sa destruction à l'issue de l'usage autorisé.",
        "",
        f"Toute utilisation non conforme de l'exemplaire {param1} engage la responsabilité",
        "personnelle de son détenteur.",
        "",
        "Fait pour servir et valoir ce que de droit.",
        "",
        "",
        "Exemplaire remis à : ......................................................",
        "Date : ......................................................................",
        "Signature :",
    ]

    for line in lines:
        text.textLine(line)

    c.drawText(text)
    c.showPage()
    c.save()
    raw_buf.seek(0)

    # --- 2. Appliquer le watermark par-dessus ---
    wm_bytes = _make_watermark_page(w, h, param1, doc_date)
    raw_reader = PdfReader(raw_buf)

    writer = PdfWriter()
    for page in raw_reader.pages:
        wm_page = PdfReader(io.BytesIO(wm_bytes)).pages[0]
        wm_page.merge_page(page)
        writer.add_page(wm_page)

    with open(output, "wb") as f:
        writer.write(f)

    print(f"[OK] PDF généré : {output}")


if __name__ == "__main__":
    main()
