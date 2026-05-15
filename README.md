# Quick-GuillochePDF

Watermarking de PDFs pour tracer la diffusion d'exemplaires numérotés.

Chaque exemplaire reçoit une trame incrustée derrière le contenu, résistante à l'impression et à la numérisation/photocopie. Le numéro d'exemplaire est présent à haute densité sur toute la surface de chaque page : toute découpe du document, même partielle, conserve le numéro.

## Principe

Trois couches superposées, de la plus profonde à la plus visible :

| Couche | Contenu | Densité | Gris |
|--------|---------|---------|------|
| Micro-trame | Numéro seul (`Ex 0101`) | ~700 occurrences/page | 0.89 (très clair) |
| Trame ondulée | Texte complet + vagues sinusoïdales | ~40 lignes/page | 0.85–0.90 |
| Header/footer | Numéro · titre · date | 2 × haut + bas | 0.65 |

La trame est placée **derrière** le contenu original, qui reste pleinement lisible.

## Installation

```bash
make setup
source .venv/bin/activate
```

## Usage

### Appliquer sur un PDF existant

```bash
python watermark_pdf.py <source.pdf> "<numéro>" --title "<titre>" [-d <date>] [-o <sortie.pdf>]
```

Exemples :

```bash
python watermark_pdf.py document.pdf "Ex 0101" --title "Rapport évaluation"
python watermark_pdf.py contrat.pdf "Ex 003" --title "Contrat NDA" -d 2026-05-15 -o contrat_Ex003.pdf
```

### Générer une déclaration de confidentialité numérotée

```bash
python generate_exemplaire_pdf.py "<numéro>" [--title "<titre>"] [-d <date>] [-o <sortie.pdf>]
```

Exemple :

```bash
python generate_exemplaire_pdf.py "Ex 042" --title "NDA projet X" -d 2026-05-15
```

## Paramètres visuels

Les constantes en tête de `watermark_pdf.py` permettent d'ajuster l'aspect :

```python
MICRO_GRAY   = 0.89   # gris micro-trame (plus bas = plus foncé)
MICRO_STEP_X = 42     # espacement horizontal du numéro (pt)
MICRO_STEP_Y = 19     # espacement vertical du numéro (pt)
WAVE_GRAY    = 0.90   # gris des lignes de vagues
TEXT_GRAY    = 0.85   # gris du texte de trame
```

## Fichiers

```
watermark_pdf.py           — script principal (watermarking)
generate_exemplaire_pdf.py — générateur de déclaration numérotée
samples/
  input/
    rapport_evaluation.pdf — PDF de test (document fictif, libre de droits)
  output/
    rapport_evaluation_Ex0101.pdf — exemple de résultat
```

## Limites

- Watermarking visible, pas stéganographique : détectable par un observateur attentif.
- Un logiciel de retouche avancé peut atténuer les couches (surtout la trame ondulée), mais la micro-trame dense est difficile à supprimer proprement sans dégrader le contenu.
- Conçu pour un usage personnel, pas pour des contextes nécessitant une sécurité documentaire professionnelle.
