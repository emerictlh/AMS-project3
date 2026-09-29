"""
Etape 0 : conversion des PDF du corpus en texte brut UTF-8

Pour chaque PDF de corpus/, écrit un fichier .txt du même nom dans
corpus_txt/. Chaque page est précédée d'un marqueur "=== PAGE N ===",
utilisé ensuite par liste_L.py pour traiter les pages séparément
(le corpus ne contient que les pages impaires : le texte est coupé
d'une page à l'autre).

Dépendance : pip install pdfplumber

A lancer depuis la racine du projet :
    python src/extraire_texte.py
"""

import os
import re
import sys

import pdfplumber

DOSSIER_PDF = "corpus"

# Numéro de page imprimé en bas de page ("± 3 ±"), à ne pas garder
REGEX_NUMERO_PAGE = re.compile(r"^± \d+ ±$", re.MULTILINE)


def extraire_pdf(chemin_pdf, chemin_txt):
    """Extrait le texte de chaque page du PDF et renvoie le nombre de pages."""
    blocs = []
    with pdfplumber.open(chemin_pdf) as pdf:
        for numero, page in enumerate(pdf.pages):
            texte = page.extract_text() or ""
            texte = REGEX_NUMERO_PAGE.sub("", texte).strip("\n")
            blocs.append(f"=== PAGE {numero} ===\n{texte}")
    with open(chemin_txt, "w", encoding="utf-8") as f:
        f.write("\n\n".join(blocs))
    return len(blocs)


def main():
    # Dossier de sortie en argument optionnel (par défaut corpus_txt)
    dossier_txt = sys.argv[1] if len(sys.argv) > 1 else "corpus_txt"
    os.makedirs(dossier_txt, exist_ok=True)

    for nom in sorted(os.listdir(DOSSIER_PDF)):
        if not nom.lower().endswith(".pdf"):
            continue
        chemin_txt = os.path.join(dossier_txt, nom[:-4] + ".txt")
        nb_pages = extraire_pdf(os.path.join(DOSSIER_PDF, nom), chemin_txt)
        print(f"{nom} : {nb_pages} pages -> {chemin_txt}")


if __name__ == "__main__":
    main()
