import re
import os
from collections import Counter

DOSSIER_TXT = "corpus_txt"
DOSSIER_RESULTATS = "resultats"

# Les 3 livres du sujet, listés en dur
LIVRES = [
    "Fondation_impaires.txt",
    "Fondation_et_empire_impaires.txt",
    "Seconde_Fondation_impaires.txt",
]

# Un mot avec majuscule juste après un de ces signes commence une réplique
# ou une phrase, ce n'est pas forcément un nom propre
MARQUEURS_DIALOGUE = {'"', "-", "«", "—", "–", ":"}


def decouper_phrases(texte):
    phrases = re.split(r"(?<=[.!?])\s+", texte)
    return [p.strip() for p in phrases if p.strip()]


def tokeniser(phrase):
    return re.findall(r"\w+|[^\w\s]", phrase, re.UNICODE)


def est_majuscule(token):
    # len > 1 pour ignorer les C, L, J venant de C'est, L'homme, J'ai
    return len(token) > 1 and token[0].isupper() and token.isalpha()


def extraire_candidats(tokens):
    """Retourne deux listes : candidats en milieu de phrase, et en début."""
    milieu = []
    debut = []
    n = len(tokens)

    for i in range(n):
        if not est_majuscule(tokens[i]):
            continue

        # Début de phrase ou début de réplique de dialogue
        est_debut = (i == 0) or (tokens[i - 1] in MARQUEURS_DIALOGUE)

        # N-grammes (1, 2, 3) qui commencent à cette position
        candidats = [tokens[i]]
        if i + 1 < n and est_majuscule(tokens[i + 1]):
            candidats.append(tokens[i] + " " + tokens[i + 1])
            if i + 2 < n and est_majuscule(tokens[i + 2]):
                candidats.append(tokens[i] + " " + tokens[i + 1] + " " + tokens[i + 2])

        if est_debut:
            debut.extend(candidats)
        else:
            milieu.extend(candidats)

    return milieu, debut


def traiter_fichier(chemin):
    with open(chemin, "r", encoding="utf-8") as f:
        contenu = f.read()

    # Chaque page est traitée séparément (pages impaires, texte discontinu)
    pages = re.split(r"=== PAGE \d+ ===", contenu)

    milieu = Counter()
    debut = Counter()
    stats = {"pages": 0, "caracteres": 0, "mots": 0, "phrases": 0}

    for page in pages:
        page = page.strip()
        if not page:
            continue

        # Recolle les mots coupés en fin de ligne : "Anacré-\non" -> "Anacréon"
        page = re.sub(r"-\n(?=[a-zàâçéèêëîïôûùüÿœ])", "", page)

        stats["pages"] += 1
        stats["caracteres"] += len(page)
        stats["mots"] += len(page.split())

        for phrase in decouper_phrases(page):
            stats["phrases"] += 1
            m, d = extraire_candidats(tokeniser(phrase))
            milieu.update(m)
            debut.update(d)

    return milieu, debut, stats


def main():
    os.makedirs(DOSSIER_RESULTATS, exist_ok=True)

    total_milieu = Counter()
    total_debut = Counter()
    total = {"pages": 0, "caracteres": 0, "mots": 0, "phrases": 0}
    lignes_stats = []

    for nom in LIVRES:
        chemin = os.path.join(DOSSIER_TXT, nom)
        milieu, debut, stats = traiter_fichier(chemin)
        total_milieu.update(milieu)
        total_debut.update(debut)

        lignes_stats.append(
            f"{nom} : {stats['pages']} pages, {stats['caracteres']} caractères, "
            f"{stats['mots']} mots, {stats['phrases']} phrases"
        )
        for cle in total:
            total[cle] += stats[cle]

    # Liste L : candidat, fréquence hors début de phrase, fréquence en début
    candidats = set(total_milieu) | set(total_debut)
    tries = sorted(candidats, key=lambda c: (-total_milieu[c], -total_debut[c]))

    chemin_L = os.path.join(DOSSIER_RESULTATS, "liste_L.txt")
    with open(chemin_L, "w", encoding="utf-8") as f:
        for c in tries:
            f.write(f"{c}\t{total_milieu[c]}\t{total_debut[c]}\n")

    lignes_stats.append(
        f"TOTAL : {total['pages']} pages, {total['caracteres']} caractères, "
        f"{total['mots']} mots, {total['phrases']} phrases"
    )
    lignes_stats.append(f"Candidats uniques dans L : {len(candidats)}")

    chemin_stats = os.path.join(DOSSIER_RESULTATS, "stats_corpus.txt")
    with open(chemin_stats, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes_stats) + "\n")

    print("\n".join(lignes_stats))
    print(f"\nListe L exportée dans {chemin_L}")
    print(f"Statistiques exportées dans {chemin_stats}")


if __name__ == "__main__":
    main()