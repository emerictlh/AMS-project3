import re
import os
from collections import Counter


def decouper_phrases(texte):
    phrases = re.split(r'(?<=[.!?])\s+', texte)
    return [p.strip() for p in phrases if p.strip()]


def tokeniser(phrase):
    return re.findall(r"\w+|[^\w\s]", phrase, re.UNICODE)


def extraire_candidats(phrase_tokens):
    candidats = []
    n = len(phrase_tokens)

    for i in range(n):
        if i == 0:
            continue

        token = phrase_tokens[i]
        if not token[0:1].isupper() or not token.isalpha():
            continue

        candidats.append(token)

        if i + 1 < n and phrase_tokens[i + 1][0:1].isupper() and phrase_tokens[i + 1].isalpha():
            candidats.append(f"{token} {phrase_tokens[i + 1]}")

            if i + 2 < n and phrase_tokens[i + 2][0:1].isupper() and phrase_tokens[i + 2].isalpha():
                candidats.append(f"{token} {phrase_tokens[i + 1]} {phrase_tokens[i + 2]}")

    return candidats


def traiter_fichier(chemin_txt):
    """Traite un fichier texte page par page, et retourne le compteur de candidats."""
    with open(chemin_txt, "r", encoding="utf-8") as f:
        contenu = f.read()

    # On découpe le texte par page (grâce au marqueur === PAGE N ===)
    pages = re.split(r"=== PAGE \d+ ===", contenu)

    compteur = Counter()

    for page in pages:
        page = page.strip()
        if not page:
            continue

        phrases = decouper_phrases(page)
        for phrase in phrases:
            tokens = tokeniser(phrase)
            candidats = extraire_candidats(tokens)
            compteur.update(candidats)

    return compteur


def main():
    dossier_txt = "corpus_txt"
    dossier_resultats = "resultats"
    os.makedirs(dossier_resultats, exist_ok=True)

    compteur_global = Counter()

    for nom_fichier in os.listdir(dossier_txt):
        if nom_fichier.endswith(".txt"):
            chemin = os.path.join(dossier_txt, nom_fichier)
            compteur = traiter_fichier(chemin)
            compteur_global.update(compteur)
            print(f"{nom_fichier} : {len(compteur)} candidats uniques trouvés")

    # Export de la liste L, triée par fréquence décroissante
    chemin_sortie = os.path.join(dossier_resultats, "liste_L.txt")
    with open(chemin_sortie, "w", encoding="utf-8") as f:
        for candidat, freq in compteur_global.most_common():
            f.write(f"{candidat}\t{freq}\n")

    print(f"\nTotal : {len(compteur_global)} candidats uniques")
    print(f"Liste L exportée dans {chemin_sortie}")


if __name__ == "__main__":
    main()