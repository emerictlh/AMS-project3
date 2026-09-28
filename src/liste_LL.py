"""
TÂCHE 3 : LISTE LL (lieux et organisations)

Idée : pour savoir si un nom est un lieu, on regarde le mot placé JUSTE AVANT
lui dans le texte.
    "sur Kalgan", "planète Terminus"   -> c'est un LIEU
    "la Fondation", "l'Empire"         -> c'est une ORGANISATION
    "dit Hardin", "capitaine Pritcher" -> c'est une PERSONNE (on l'écarte)

Entrées  : resultats/liste_L.txt   (liste L, faite en tâche 1)
           resultats/liste_LP.txt  (liste LP, faite en tâche 2, facultative)
           ressources/fonctionnels_fr.txt (antidictionnaire)
           corpus_txt/*.txt        (les 3 livres)
Sortie   : resultats/liste_LL.txt

Lancement, depuis la racine du projet :  python src/liste_LL.py
"""
import os
import re
from collections import Counter


# ============================================================================
# ÉTAPE 0 : PARAMÈTRES
# ============================================================================
FICHIER_L = "resultats/liste_L.txt"
FICHIER_LP = "resultats/liste_LP.txt"
FICHIER_LL = "resultats/liste_LL.txt"
FICHIER_ANTIDICO = "ressources/fonctionnels_fr.txt"
LIVRES = [
    "corpus_txt/Fondation_impaires.txt",
    "corpus_txt/Fondation_et_empire_impaires.txt",
    "corpus_txt/Seconde_Fondation_impaires.txt",
]

# Mots placés juste avant un nom, qui indiquent un LIEU
PREPOSITIONS_LIEU = {"sur", "depuis"}                # "sur Trantor"
PREPOSITIONS_FAIBLES = {"de", "d'"}                  # "de Trantor", mais aussi "le plan de Seldon"
ARTICLES = {"la", "l'"}                              # "la Fondation", "l'Empire"
NOMS_DE_LIEU = {"planète", "planètes", "monde", "mondes", "système", "systèmes",
                "secteur", "secteurs", "royaume", "province", "république",
                "capitale", "ville", "cité", "université", "région", "empire",
                "station", "spatioport", "palais", "territoire", "zone"}

# Mots placés avant ou après un nom, qui indiquent une PERSONNE
TITRES = {"m", "monsieur", "madame", "mademoiselle", "dame", "docteur", "dr",
          "capitaine", "lieutenant", "commandant", "colonel", "général", "amiral",
          "commodore", "sergent", "maire", "seigneur", "sire", "roi", "reine",
          "prince", "princesse", "lord", "professeur", "ambassadeur", "orateur"}
VERBES_PAROLE = {"dit", "fit", "répondit", "demanda", "murmura", "écria", "reprit",
                 "ajouta", "répliqua", "grogna", "déclara", "lança", "cria", "souffla",
                 "interrompit", "rétorqua", "poursuivit", "soupira", "hurla", "insista"}

# Seuils de décision
MIN_OCCURRENCES = 3     # en dessous, le candidat est "rare"
MIN_SCORE = 0.25        # au moins 25 % des occurrences doivent avoir un indice de lieu
MIN_INDICES = 2         # et au moins 2 indices de lieu au total
SEUIL_FRAGMENT = 0.6    # "Seconde" est un fragment si 60 % de ses occurrences
                        # font partie de "Seconde Fondation"


# ============================================================================
# ÉTAPE 1 : LIRE LES FICHIERS D'ENTRÉE
# ============================================================================
def lire_liste(chemin):
    """Lit une liste 'candidat<TAB>fréquence<TAB>...' et renvoie l'ensemble des candidats."""
    candidats = set()
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            colonnes = ligne.rstrip("\n").split("\t")
            if len(colonnes) >= 2 and colonnes[1].isdigit():
                candidats.add(colonnes[0])
    return candidats


def lire_antidico(chemin):
    """Lit l'antidictionnaire : un mot par ligne, les lignes '#' sont des commentaires."""
    mots = set()
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.strip()
            if ligne and not ligne.startswith("#"):
                mots.add(ligne.lower())
    return mots


def lire_corpus(chemins):
    """Lit les livres, les nettoie et renvoie la liste de tous les tokens (mots et ponctuation)."""
    tokens = []
    for chemin in chemins:
        if not os.path.exists(chemin):
            raise SystemExit(f"Fichier introuvable : {chemin} (vérifie la liste LIVRES)")
        with open(chemin, encoding="utf-8") as f:
            texte = f.read()
        texte = re.sub(r"=== PAGE \d+ ===", " ", texte)     # marqueurs de page
        texte = re.sub(r"±\s*\d+\s*±", " ", texte)            # numéros de page du PDF
        texte = re.sub(r"(\w)-\n(\w)", r"\1-\2", texte)       # mots coupés en fin de ligne
        tokens += re.findall(r"\w+(?:-\w+)*|[^\w\s]", texte)
    return tokens


L = lire_liste(FICHIER_L)
LP = lire_liste(FICHIER_LP) if os.path.exists(FICHIER_LP) else set()
antidico = lire_antidico(FICHIER_ANTIDICO)
tokens = lire_corpus(LIVRES)

# Combien de fois chaque mot apparaît en minuscules (sert à repérer les noms communs)
minuscules = Counter(t for t in tokens if t.islower())

print(f"Liste L : {len(L)} candidats | LP : {len(LP)} personnages | "
      f"antidictionnaire : {len(antidico)} mots | corpus : {len(tokens)} tokens")


# ============================================================================
# ÉTAPE 2 : ENLEVER LE BRUIT ET LES PERSONNAGES
# ============================================================================
def est_du_bruit(candidat):
    """Vrai si le candidat ne peut pas être un lieu."""
    mots = candidat.split()
    if mots[0].lower() in antidico or mots[-1].lower() in antidico:
        return True      # mot vide : "Mais", "Il", "Et Hardin"
    for mot in mots:
        if len(mot) == 1:
            return True  # lettre seule : C, L, J (de C'est, L'homme, J'ai)
        if mot.isupper():
            return True  # tout en majuscules : "II" (erreur OCR), titres "PARTIE"
    return False


candidats = [c for c in L if not est_du_bruit(c)]
print(f"Étape 2a - sans le bruit             : {len(candidats)} candidats")

candidats = [c for c in candidats if c not in LP]
print(f"Étape 2b - sans les personnages (LP) : {len(candidats)} candidats")


# ============================================================================
# ÉTAPE 3 : TROUVER OÙ CHAQUE CANDIDAT APPARAÎT DANS LE TEXTE
# ============================================================================
# positions["Seconde Fondation"] = [liste des numéros de token où il commence]
positions = {c: [] for c in candidats}
for n in (1, 2, 3):                                   # candidats de 1, 2 ou 3 mots
    for i in range(len(tokens) - n + 1):
        morceau = " ".join(tokens[i:i + n])
        if morceau in positions:
            positions[morceau].append(i)


# ============================================================================
# ÉTAPE 4 : COMPTER LES INDICES AUTOUR DE CHAQUE OCCURRENCE
# ============================================================================
def mot_avant(i):
    """Le mot juste avant la position i, en minuscules. Dans "d'Anacréon", renvoie "d'"."""
    if i == 0:
        return ""
    if tokens[i - 1] in ("'", "’") and i >= 2:
        return tokens[i - 2].lower() + "'"
    return tokens[i - 1].lower()


def mot_apres(i, n):
    """Le mot juste après un candidat de n mots qui commence en i."""
    if i + n < len(tokens):
        return tokens[i + n].lower()
    return ""


def compter_indices(candidat):
    """Pour un candidat, compte les indices de lieu, d'organisation et de personne."""
    n = len(candidat.split())
    indices = Counter()
    for i in positions[candidat]:
        avant = mot_avant(i)
        trois_mots_avant = {t.lower() for t in tokens[max(0, i - 3):i]}
        apres = mot_apres(i, n)

        # Indices de lieu : on ne compte que le plus fort pour chaque occurrence
        if avant in PREPOSITIONS_LIEU:
            indices["lieu_fort"] += 1            # "sur Kalgan"
        elif trois_mots_avant & NOMS_DE_LIEU:
            indices["lieu_fort"] += 1            # "la planète Terminus"
        elif avant in ARTICLES:
            indices["organisation"] += 1         # "la Fondation"
        elif avant in PREPOSITIONS_FAIBLES:
            indices["lieu_faible"] += 1          # "de Trantor"

        # Indices de personne
        if avant in TITRES or avant in VERBES_PAROLE or apres in VERBES_PAROLE:
            indices["personne"] += 1             # "capitaine X", "dit X", "X répondit"
    return indices


# ============================================================================
# ÉTAPE 5 : DÉCIDER SI LE CANDIDAT EST UN LIEU
# ============================================================================
def est_un_lieu(candidat, nb_occ, indices):
    """Applique les règles de décision."""
    # Le faible compte pour 1/2 car "de" précède aussi des personnes ("le plan de Seldon")
    score_lieu = indices["lieu_fort"] + indices["organisation"] + 0.5 * indices["lieu_faible"]

    if nb_occ >= MIN_OCCURRENCES:
        # Candidat fréquent : assez d'indices de lieu, et beaucoup plus que de personne
        return (score_lieu >= MIN_INDICES
                and score_lieu / nb_occ >= MIN_SCORE
                and score_lieu > 2 * indices["personne"])

    # Candidat rare (1 ou 2 fois) : il faut un indice fort, aucun indice de
    # personne, et que ce ne soit pas un nom commun (écrit aussi en minuscules)
    nom_commun = any(minuscules[m.lower()] > 0 for m in candidat.split())
    return indices["lieu_fort"] >= 1 and indices["personne"] == 0 and not nom_commun


resultats = []
for c in candidats:
    nb_occ = len(positions[c])
    if nb_occ == 0:
        continue
    indices = compter_indices(c)
    if est_un_lieu(c, nb_occ, indices):
        if indices["organisation"] > indices["lieu_fort"] + indices["lieu_faible"]:
            genre = "organisation"
        else:
            genre = "lieu"
        resultats.append((c, nb_occ, genre, indices))

print(f"Étape 5  - avec des indices de lieu  : {len(resultats)} candidats")


# ============================================================================
# ÉTAPE 6 : ENLEVER LES FRAGMENTS ("Seconde" est un morceau de "Seconde Fondation")
# ============================================================================
occurrences = {c: nb for c, nb, _, _ in resultats}


def est_un_fragment(court):
    """Vrai si la plupart des occurrences de 'court' sont dans un nom plus long de la liste."""
    total_dans_plus_long = 0
    for long in occurrences:
        if len(long.split()) > len(court.split()) and f" {court} " in f" {long} ":
            total_dans_plus_long += occurrences[long]
    return total_dans_plus_long >= SEUIL_FRAGMENT * occurrences[court]


fragments = [c for c in occurrences if est_un_fragment(c)]
resultats = [r for r in resultats if r[0] not in fragments]
print(f"Étape 6  - sans les fragments        : {len(resultats)} candidats "
      f"(retirés : {', '.join(sorted(fragments))})")


# ============================================================================
# ÉTAPE 7 : ÉCRIRE LA LISTE LL
# ============================================================================
resultats.sort(key=lambda r: -r[1])          # du plus fréquent au moins fréquent
with open(FICHIER_LL, "w", encoding="utf-8") as f:
    f.write("candidat\toccurrences\ttype\tindices\n")
    for c, nb_occ, genre, indices in resultats:
        detail = ", ".join(f"{k}:{v}" for k, v in indices.most_common())
        f.write(f"{c}\t{nb_occ}\t{genre}\t{detail}\n")

print(f"Liste LL écrite dans {FICHIER_LL} ({len(resultats)} lieux et organisations)")
