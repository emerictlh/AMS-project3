"""
Evaluation de la liste LP (tâche 2)

Compare resultats/liste_LP.txt à une liste de référence annotée à la main
(ressources/reference_personnes.txt : les 100 candidats d'un seul mot les
plus fréquents de L, marqués P = personne ou N = pas une personne).

Mesures calculées, sur ces 100 candidats uniquement :
    - précision : parmi les candidats que LP a gardés, combien sont
                  vraiment des personnes ?
    - rappel    : parmi les vraies personnes, combien LP en a gardé ?
    - F-mesure  : moyenne harmonique des deux

Le script liste aussi les erreurs (faux positifs et faux négatifs),
utiles pour le rapport et pour améliorer les règles.

A lancer depuis la racine du projet, après liste_LP.py :
    python src/evaluer_LP.py
"""

import os

CHEMIN_REFERENCE = os.path.join("ressources", "reference_personnes.txt")
CHEMIN_LP = os.path.join("resultats", "liste_LP.txt")


def charger_reference(chemin):
    """Renvoie un dict {candidat: True si personne, False sinon}."""
    reference = {}
    with open(chemin, "r", encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.strip()
            if not ligne or ligne.startswith("#"):
                continue
            candidat, etiquette = ligne.split("\t")
            reference[candidat] = (etiquette == "P")
    return reference


def charger_LP(chemin):
    """Renvoie l'ensemble des candidats présents dans LP."""
    with open(chemin, "r", encoding="utf-8") as f:
        return {ligne.split("\t")[0] for ligne in f if ligne.strip()}


def main():
    reference = charger_reference(CHEMIN_REFERENCE)
    LP = charger_LP(CHEMIN_LP)

    vrais_positifs = [c for c, est_p in reference.items() if est_p and c in LP]
    faux_positifs = [c for c, est_p in reference.items() if not est_p and c in LP]
    faux_negatifs = [c for c, est_p in reference.items() if est_p and c not in LP]

    vp, fp, fn = len(vrais_positifs), len(faux_positifs), len(faux_negatifs)
    precision = vp / (vp + fp) if vp + fp else 0
    rappel = vp / (vp + fn) if vp + fn else 0
    f_mesure = 2 * precision * rappel / (precision + rappel) if precision + rappel else 0

    print(f"Référence : {len(reference)} candidats, "
          f"{sum(reference.values())} personnes")
    print(f"Vrais positifs  : {vp}")
    print(f"Faux positifs   : {fp}  {faux_positifs}")
    print(f"Faux négatifs   : {fn}  {faux_negatifs}")
    print(f"Précision : {precision:.1%}")
    print(f"Rappel    : {rappel:.1%}")
    print(f"F-mesure  : {f_mesure:.1%}")


if __name__ == "__main__":
    main()
