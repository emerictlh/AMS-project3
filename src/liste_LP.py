"""
Tâche 2 : Liste LP (personnages)

Ce script part de la liste L (resultats/liste_L.txt), produite par
liste_L.py, et n'en garde que les noms de personnes.

Format attendu de liste_L.txt (première ligne = en-tête avec ces noms) :
    candidat<TAB>freq_milieu<TAB>freq_debut

    - candidat    : le mot ou groupe de mots (1 à 3 tokens) avec majuscule
    - freq_milieu : nombre de fois où il apparaît hors début de phrase
                    ou de dialogue
    - freq_debut  : nombre de fois où il apparaît en tout début de phrase
                    ou juste après un signe de dialogue (", -, «, —, :)

Le filtrage se fait en deux étapes.

ETAPE A : retirer le bruit "grammatical" (règles appliquées dans l'ordre)
    1. capitales        : un mot du candidat est écrit en MAJUSCULES
                          (titres de chapitres, en-têtes : "PREMIÈRE
                          PARTIE", "GALACTICA Bel Riose"...). La forme
                          normale du nom est de toute façon dans L.
    1 bis. numéro de règne : "Ier" seul (on garde "Cléon Ier")
    2. artefact         : chiffre romain, mot sans voyelle, ou dans la
                          liste noire ARTEFACTS_CONNUS (erreurs d'OCR/PDF)
    3. antidictionnaire : un des mots du candidat est un mot fonctionnel
                          français (le, la, mais, il, etc.), voir
                          ressources/fonctionnels_fr.txt
    4. vu en minuscule  : un des mots du candidat apparaît plus souvent
                          écrit en minuscule dans le corpus qu'avec une
                          majuscule en milieu de phrase. C'est donc un nom
                          commun ("Plan" / "plan", "Seconde" / "seconde").
                          On compare les deux fréquences au lieu de rejeter
                          dès la première occurrence en minuscule : sinon
                          "Mis" (Ebling Mis, 64 fois) serait perdu à cause
                          du participe "mis" (27 fois).
    5. impératif        : un mot se termine en -ez ou -ons (verbe à
                          l'impératif, ex : "Ecoutez", "Sortons")
    6. gentilé          : un mot se termine en -ien(ne)(s) ou -ites
                          (adjectif ou nom d'habitants : "Korellienne",
                          "Askoniens", "Rossemites")
    7. titre            : le candidat est seulement un titre ou une
                          fonction ("Maire", "Premier Orateur",
                          "Excellence"), pas le nom d'une personne précise
    8. mot de lieu      : le candidat contient un mot de bâtiment ou de
                          voie ("Building Hardin", "Mallow Hall")

ETAPE B : distinguer les personnes des lieux et des organisations
    Les règles de l'étape A ne font pas la différence entre "Mallow" et
    "Trantor". Pour ça on regarde le CONTEXTE de chaque mot dans le corpus
    (le mot juste avant et le mot juste après) et on compte des indices :

    Indices de PERSONNE :
        - précédé d'un verbe de parole, typique des incises de dialogue :
          "dit Mallow", "demanda Bayta", "murmura Toran", y compris avec
          un article entre les deux : "dit le Mulet"
        - précédé d'un titre : "docteur Seldon", "capitaine Pritcher"
        - suivi d'un verbe de geste : "Bayta sourit", "Mallow haussa"

    Indices de NON-PERSONNE :
        - précédé d'un article : "la Galaxie", "le Maire", "l'Empire".
          En français, un nom de personne n'a presque jamais d'article.
        - précédé d'une préposition de lieu : "sur Trantor", "à Kalgan",
          "vers Terminus", "planète Synnax"

    Décision pour un mot seul (voir classer_mot) :
        personne     si indices_personne >= 3,
                     ou si indices_personne >= 1 et >= indices_non_personne
        non-personne sinon, si indices_non_personne >= 2
        indéterminé  sinon (souvent des mots vus une seule fois)

    Décision pour un groupe de mots (bigramme ou trigramme) :
        - s'il commence par un titre ("Docteur Darell", "Dame Callia"),
          c'est une personne si le reste n'est pas une non-personne
        - sinon, c'est une personne si aucun mot n'est une non-personne
          et qu'au moins un mot est une personne ("Hari Seldon")

    Propagation : un mot seul indéterminé devient une personne s'il fait
    partie d'un groupe reconnu comme personne. Par exemple "Preem" (1 seule
    occurrence, aucun indice) est gardé grâce à "Preem Palver". C'est
    l'utilisation des co-occurrences de n-grammes suggérée par le sujet.

    Remarque : "l'Irréductible" est gardé volontairement. C'est un
    surnom de personnage ("on appelait l'Irréductible"), au même titre
    que "le Mulet".

ETAPE C : fusionner les fautes d'OCR ("Magnifiée" -> "Magnifico"),
    voir fusionner_variantes_ocr.

Ce qui reste est écrit dans resultats/liste_LP.txt.
Ce qui est rejeté (avec la raison) est écrit dans
resultats/liste_L_rejetes.txt.

Evaluation : voir src/evaluer_LP.py (précision / rappel sur les 100
candidats les plus fréquents de L, annotés dans
ressources/reference_personnes.txt).

------------------------------------------------------------------------
NOTE POUR LA TÂCHE 3 (liste LL : lieux et organisations)
------------------------------------------------------------------------
Le sujet dit : "A partir de L et LP, produire LL". L'idée est donc :

    LL  =  (L  moins  LP)  moins le bruit  moins les noms communs

1. Partir de L et retirer tout ce qui est dans LP (les personnes).

2. Retirer le bruit grammatical : réutiliser filtrer_grammatical()
   de ce fichier, mais SANS les règles 6 (gentilé), 7 (titre) et
   8 (mot de lieu), qui rejettent justement des choses utiles pour LL.
   Le plus simple : copier la fonction et enlever ces trois règles.

3. Garder les candidats qui ont des indices de lieu. On peut réutiliser
   charger_tokens_corpus() et compter_indices_contexte() : le compteur
   "non_personne" compte déjà les articles et PREPOSITIONS_LIEU ("sur
   Trantor", "planète Synnax"). Mieux vaut séparer ce compteur en deux :
       - préposition de lieu avant ("sur", "vers", "planète", "d'")
         -> lieu (planète, ville)
       - article avant ("la Fondation", "le Conseil")
         -> organisation, OU nom commun ("la Galaxie", "le Plan")
   Pour trier organisation / nom commun : un nom commun apparaît aussi
   en minuscule dans le corpus (règle 4 de filtrer_grammatical) ou
   dans un dictionnaire français.

4. Récupérer les lieux cachés dans les autres rejets de LP :
       - "gentilé" : "Korellienne" prouve que "Korell" est un lieu.
         On peut retrouver le lieu en coupant le suffixe (-ienne, -iens,
         -ites) et en cherchant le début du mot dans L.
       - "mot de lieu" : "Building Hardin", "Avenue Fleurie" sont des
         lieux, même s'ils contiennent un nom de personne de LP.
       - "indéterminé" : beaucoup de lieux cités une seule fois
         (Synnax, Hélicon, Arcturus, Santanni...). Il faudra d'autres
         indices ("la planète X", "le système de X", "né à X"...).

Pour commencer, lire resultats/liste_L_rejetes.txt : les lignes
"non-personne (contexte)" contiennent déjà la plupart des lieux
(Trantor, Kalgan, Terminus, Anacréon, Siwenna, Korell, Rossem...).
------------------------------------------------------------------------
"""

import re
import os
from collections import Counter

DOSSIER_TXT = "corpus_txt"
DOSSIER_RESULTATS = "resultats"
CHEMIN_ANTIDICO = os.path.join("ressources", "fonctionnels_fr.txt")

# Les 3 livres du sujet, dans le même ordre que dans liste_L.py
LIVRES = [
    "Fondation_impaires.txt",
    "Fondation_et_empire_impaires.txt",
    "Seconde_Fondation_impaires.txt",
]

# Chiffres romains courants, pour repérer les numéros de chapitre
# capturés par erreur comme des noms (ex : "II").
CHIFFRES_ROMAINS = {"I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
                     "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX"}

VOYELLES = set("aeiouyàâéèêëîïôûùüœ")

# Artefacts d'extraction PDF repérés à l'oeil en lisant liste_L.txt
# (mots sans sens, dus à un problème d'encodage ou d'OCR), ou formes
# irrégulières non couvertes par se_termine_imperatif (ex : "Etes").
ARTEFACTS_CONNUS = {"FRQWUHF", "XYUDLHQW", "GHOj", "Etes"}

# Titres et fonctions (en minuscule). Servent à deux choses :
#   - un candidat qui n'est QUE un titre est rejeté ("Maire")
#   - un mot précédé d'un titre est un indice de personne ("maire Hardin")
TITRES = {
    "docteur", "capitaine", "maire", "seigneur", "dame", "commodore",
    "oncle", "tante", "général", "lieutenant", "colonel", "amiral",
    "sergent", "sire", "maître", "orateur", "procureur", "excellence",
    "majesté", "altesse", "empereur", "impératrice", "roi", "reine",
    "prince", "princesse", "ministre", "citoyen", "professeur",
    "monsieur", "madame", "mademoiselle", "haut", "maman", "papa",
    "commandant", "patron", "chef", "secrétaire", "lord", "marchand",
}

# "Premier Orateur", "Premier Citoyen" sont des titres, mais "premier"
# ne doit PAS compter comme indice de personne devant un mot, sinon
# "Première Fondation" ou "premier Empire" feraient passer Fondation et
# Empire pour des personnes. On ne s'en sert donc que pour la règle 7.
ORDINAUX = {"premier", "première", "second", "seconde"}

# Mots qui désignent un bâtiment ou une voie : "Building Hardin" ou
# "Mallow Hall" contiennent un nom de personne mais désignent un lieu
MOTS_LIEU = {"building", "hall", "avenue", "rue", "place", "palais",
             "salle", "temple", "musée", "bibliothèque", "port"}

# Verbes de parole des incises de dialogue ("... ", dit Mallow).
# Au passé simple, la forme que l'on trouve dans les romans.
VERBES_PAROLE = {
    "dit", "fit", "demanda", "répondit", "répliqua", "reprit", "murmura",
    "cria", "écria", "ajouta", "poursuivit", "continua", "observa",
    "déclara", "protesta", "soupira", "grommela", "lança", "interrompit",
    "tonna", "hurla", "souffla", "insista", "acquiesça", "balbutia",
    "bégaya", "rétorqua", "expliqua", "remarqua", "annonça", "coupa",
    "gronda", "chuchota", "demande", "dis", "questionna", "conclut",
    "rit", "ricana", "explosa", "objecta", "admit", "avoua", "affirma",
    "interrogea", "appelle", "appeler", "appelait", "appelée", "nommé",
    "nommée", "surnommé",
}

# Verbes de geste qui suivent un nom de personne ("Bayta sourit")
VERBES_GESTE = {
    "sourit", "hocha", "haussa", "leva", "fronça", "soupira", "ricana",
    "grimaça", "hésita", "rougit", "tressaillit", "éclata", "sursauta",
    "rit", "acquiesça", "regarda",
}

# Articles et contractions : un nom propre de personne n'en a pas
ARTICLES = {"le", "la", "les", "l", "un", "une", "des", "du", "au", "aux"}

# Prépositions et noms qui introduisent un lieu. "à" n'en fait pas
# partie : on écrit aussi bien "à Kalgan" que "dit à Salvor".
PREPOSITIONS_LIEU = {"sur", "vers", "planète", "système", "secteur",
                     "monde", "royaume", "depuis", "jusqu"}

# Numéros de règne : "Cléon Ier" est une personne, mais "Ier" seul non
NUMEROS_REGNE = {"Ier", "Ire", "Premier"}

# Fusion des variantes d'OCR (voir fusionner_variantes_ocr)
LONGUEUR_MIN_OCR = 5      # en dessous, trop de risques ("Lev" / "Lee")
LONGUEUR_MOT_LONG = 7     # à partir de là on tolère 2 lettres d'écart
RAPPORT_FREQ_OCR = 3      # la bonne forme doit être 3 fois plus fréquente

# Seuils de décision (voir classer_mot)
MIN_INDICES_NON_PERSONNE = 2
MIN_INDICES_PERSONNE_FORTS = 3

# Suffixes de gentilés / adjectifs dérivés de noms de lieux
REGEX_GENTILE = re.compile(r"(ien|iens|ienne|iennes|ites)$")


def est_artefact(mot):
    """
    Renvoie True si le mot est probablement un artefact d'extraction
    et pas un vrai mot français : chiffre romain, dans la liste noire,
    ou ne contenant aucune voyelle (ce qui n'arrive jamais dans un vrai
    mot français).
    """
    if mot in CHIFFRES_ROMAINS:
        return True
    if mot in ARTEFACTS_CONNUS:
        return True
    if not any(c in VOYELLES for c in mot.lower()):
        return True
    return False


def se_termine_imperatif(mot):
    """
    Détecte un verbe à l'impératif pluriel (2e personne en -ez,
    1re personne en -ons), forme qui apparaît uniquement en début
    de réplique de dialogue et n'est jamais un nom de personne.
    """
    return mot.endswith("ez") or mot.endswith("ons")


def charger_antidico(chemin):
    """
    Charge l'antidictionnaire (un mot par ligne, tout en minuscule).
    Les lignes vides et celles qui commencent par # sont ignorées.
    """
    mots = set()
    with open(chemin, "r", encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.strip()
            if not ligne or ligne.startswith("#"):
                continue
            mots.add(ligne.lower())
    return mots


def charger_liste_L(chemin):
    """
    Relit resultats/liste_L.txt produit par liste_L.py.
    Renvoie un dict {candidat: (freq_milieu, freq_debut)}.
    """
    candidats = {}
    with open(chemin, "r", encoding="utf-8") as f:
        for ligne in f:
            parts = ligne.rstrip("\n").split("\t")
            # Ignore la ligne d'en-tête et les lignes mal formées
            if len(parts) != 3 or not parts[1].isdigit():
                continue
            candidat, freq_milieu, freq_debut = parts
            candidats[candidat] = (int(freq_milieu), int(freq_debut))
    return candidats


def charger_tokens_corpus():
    """
    Relit les 3 livres et renvoie la liste de tous les tokens (mots et
    ponctuation), avec le même découpage que liste_L.py.
    """
    tokens = []
    for nom in LIVRES:
        chemin = os.path.join(DOSSIER_TXT, nom)
        with open(chemin, "r", encoding="utf-8") as f:
            contenu = f.read()
        # On retire les marqueurs de page ajoutés à l'extraction
        contenu = re.sub(r"=== PAGE \d+ ===", " ", contenu)
        tokens.extend(re.findall(r"\w+|[^\w\s]", contenu, re.UNICODE))
    return tokens


def compter_minuscules(tokens):
    """
    Compte combien de fois chaque mot apparaît écrit tout en minuscule.
    Un vrai nom propre (ex : "Seldon") n'apparaît jamais en minuscule,
    alors qu'un nom commun ("plan") apparaît souvent sous cette forme.
    """
    return Counter(t for t in tokens if t.isalpha() and t.islower())


def position_precedente(tokens, i):
    """
    Renvoie l'indice du mot juste avant la position i, en sautant
    l'apostrophe : dans "l'Empire" le découpage donne l / ' / Empire,
    et c'est "l" qui nous intéresse. Renvoie -1 en début de corpus.
    """
    j = i - 1
    if j >= 0 and tokens[j] in ("'", "’"):
        j -= 1
    return j


def mot_precedent(tokens, i):
    """Renvoie le mot (en minuscule) juste avant la position i."""
    j = position_precedente(tokens, i)
    return tokens[j].lower() if j >= 0 else ""


def compter_indices_contexte(tokens, mots_cibles):
    """
    Parcourt le corpus une seule fois et compte, pour chaque mot de
    mots_cibles, les indices de personne et de non-personne trouvés
    dans son contexte immédiat (voir le docstring du module).

    Renvoie deux Counter : indices_personne, indices_non_personne.
    """
    personne = Counter()
    non_personne = Counter()

    for i, tok in enumerate(tokens):
        if tok not in mots_cibles:
            continue

        avant = mot_precedent(tokens, i)
        apres = tokens[i + 1].lower() if i + 1 < len(tokens) else ""

        # Deux mots avant : sert pour "dit le Mulet", où le surnom
        # prend un article mais reste le sujet d'un verbe de parole
        j = position_precedente(tokens, i)
        avant2 = mot_precedent(tokens, j) if j >= 0 else ""

        if avant in ARTICLES and avant2 in VERBES_PAROLE:
            personne[tok] += 1
            continue

        if avant in VERBES_PAROLE or avant in TITRES:
            personne[tok] += 1
        elif apres in VERBES_GESTE:
            personne[tok] += 1

        if avant in ARTICLES or avant in PREPOSITIONS_LIEU:
            non_personne[tok] += 1

    return personne, non_personne


def filtrer_grammatical(candidats, antidico, minuscules):
    """
    ETAPE A : applique les règles 1 à 7 et sépare les candidats en
    deux groupes : ceux qui passent, et les rejetés (avec la raison).
    """
    gardes = {}
    rejetes = []

    for candidat, (freq_milieu, freq_debut) in candidats.items():
        mots = candidat.split()

        # Règle 1 : un mot en capitales (titre de chapitre, en-tête,
        # y compris collé à la suite : "GALACTICA Bel Riose")
        if any(m.isupper() and len(m) > 1 for m in mots):
            rejetes.append((candidat, "capitales"))
            continue

        # Règle 1 bis : numéro de règne isolé ("Ier" sans "Cléon")
        if candidat in NUMEROS_REGNE:
            rejetes.append((candidat, "numéro de règne"))
            continue

        # Règle 2 : artefact d'extraction (chiffre romain, mot cassé...)
        if any(est_artefact(m) for m in mots):
            rejetes.append((candidat, "artefact"))
            continue

        # Règle 3 : mot fonctionnel français (le, la, mais, il...)
        if any(m.lower() in antidico for m in mots):
            rejetes.append((candidat, "antidictionnaire"))
            continue

        # Règle 4 : un des mots est plus souvent écrit en minuscule
        # qu'avec une majuscule en milieu de phrase => nom commun.
        # Pour un mot à l'intérieur d'un groupe, on utilise sa propre
        # fréquence dans L si elle existe.
        def est_nom_commun(m):
            freq_maj = candidats.get(m, (freq_milieu, 0))[0]
            return minuscules[m.lower()] > freq_maj
        if any(est_nom_commun(m) for m in mots):
            rejetes.append((candidat, "vu en minuscule"))
            continue

        # Règle 5 : verbe à l'impératif en début de réplique
        if any(se_termine_imperatif(m) for m in mots):
            rejetes.append((candidat, "impératif"))
            continue

        # Règle 6 : gentilé / adjectif dérivé d'un lieu
        if any(REGEX_GENTILE.search(m) for m in mots):
            rejetes.append((candidat, "gentilé"))
            continue

        # Règle 7 : le candidat n'est composé que de titres
        if all(m.lower() in TITRES or m.lower() in ORDINAUX for m in mots):
            rejetes.append((candidat, "titre"))
            continue

        # Règle 8 : un bâtiment ou une voie ("Building Hardin")
        if any(m.lower() in MOTS_LIEU for m in mots):
            rejetes.append((candidat, "mot de lieu"))
            continue

        gardes[candidat] = (freq_milieu, freq_debut)

    return gardes, rejetes


def classer_mot(mot, personne, non_personne):
    """
    Renvoie 'personne', 'non-personne' ou 'indéterminé' pour un mot.

    - Un lieu n'est jamais sujet d'un verbe de parole, donc à partir de
      MIN_INDICES_PERSONNE_FORTS indices de personne on garde le mot
      même s'il a aussi beaucoup d'articles ("le Mulet").
    - En cas d'égalité, on penche vers la personne ("madame Palver" /
      "les Palver").
    - Un seul indice de non-personne ne suffit pas à rejeter : il peut
      venir d'une tournure rare ou d'un mot coupé entre deux pages.
    """
    p = personne[mot]
    n = non_personne[mot]
    if p >= MIN_INDICES_PERSONNE_FORTS:
        return "personne"
    if p >= 1 and p >= n:
        return "personne"
    if n >= MIN_INDICES_NON_PERSONNE:
        return "non-personne"
    return "indéterminé"


def filtrer_personnes(candidats, tokens):
    """
    ETAPE B : garde seulement les personnes, grâce aux indices de
    contexte, puis applique la propagation groupe -> mot seul.
    """
    # Tous les mots qui composent les candidats restants
    mots_cibles = {m for c in candidats for m in c.split()}
    personne, non_personne = compter_indices_contexte(tokens, mots_cibles)

    classe = {m: classer_mot(m, personne, non_personne) for m in mots_cibles}

    LP = {}
    rejetes = []
    en_attente = {}   # mots seuls indéterminés, décidés à la fin

    for candidat, freqs in candidats.items():
        mots = candidat.split()

        if len(mots) == 1:
            c = classe[candidat]
            if c == "personne":
                LP[candidat] = freqs
            elif c == "non-personne":
                rejetes.append((candidat, "non-personne (contexte)"))
            else:
                en_attente[candidat] = freqs
            continue

        # Groupe de mots commençant par un titre : "Docteur Darell"
        if mots[0].lower() in TITRES:
            reste = [m for m in mots[1:] if m.lower() not in TITRES]
            if reste and all(classe[m] != "non-personne" for m in reste):
                LP[candidat] = freqs
            else:
                rejetes.append((candidat, "non-personne (contexte)"))
            continue

        # Groupe sans titre : "Hari Seldon", "Preem Palver"
        classes = [classe[m] for m in mots]
        if "non-personne" in classes:
            rejetes.append((candidat, "non-personne (contexte)"))
        elif "personne" in classes:
            LP[candidat] = freqs
        else:
            rejetes.append((candidat, "indéterminé"))

    # Propagation : un mot seul indéterminé est gardé s'il fait partie
    # d'un groupe de mots déjà reconnu comme personne
    mots_de_personnes = {m for c in LP if " " in c for m in c.split()}
    for candidat, freqs in en_attente.items():
        if candidat in mots_de_personnes:
            LP[candidat] = freqs
        else:
            rejetes.append((candidat, "indéterminé"))

    return LP, rejetes


def distance_edition(a, b):
    """
    Distance de Levenshtein : nombre minimal de lettres à insérer,
    supprimer ou remplacer pour passer de a à b.
    Ex : "Mulel" -> "Mulet" = 1, "Magnifiée" -> "Magnifico" = 2.
    """
    precedente = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        courante = [i]
        for j, cb in enumerate(b, 1):
            courante.append(min(precedente[j] + 1,              # suppression
                                courante[j - 1] + 1,            # insertion
                                precedente[j - 1] + (ca != cb)))  # remplacement
        precedente = courante
    return precedente[-1]


def fusionner_variantes_ocr(LP):
    """
    ETAPE C : fusionne les fautes d'OCR avec la bonne forme du nom.

    Un nom seul rare est considéré comme une variante d'un autre nom de LP
    si les deux sont très proches (distance d'édition faible), commencent
    par la même lettre, et si l'autre est au moins RAPPORT_FREQ_OCR fois
    plus fréquent. Ex : "Magnifiée" -> "Magnifico", "Stellin" -> "Stettin".

    Garde-fous (tout le risque est de fusionner deux vrais personnages) :
        - pas de fusion sous LONGUEUR_MIN_OCR lettres ("Lev" et "Lee"
          sont deux personnages différents)
        - 1 lettre d'écart maximum pour les mots courts, 2 à partir de
          LONGUEUR_MOT_LONG lettres : "Tomas" (Tomas Sutt) est à 2 lettres
          de "Toran" mais n'est pas une faute de frappe.
    Limite connue : "Cailla" (2 lettres d'écart avec "Callia", mot de 6
    lettres) n'est donc pas fusionné.

    La fréquence de la variante est ajoutée à celle de la bonne forme.
    Les groupes qui contiennent une variante ("Dame Cailla") sont gardés
    tels quels : ils désignent bien une personne.
    """
    simples = [c for c in LP if " " not in c]

    fusions = {}   # variante -> bonne forme
    for variante in simples:
        if len(variante) < LONGUEUR_MIN_OCR:
            continue
        distance_max = 2 if len(variante) >= LONGUEUR_MOT_LONG else 1
        fv = LP[variante][0]
        meilleure = None
        for cible in simples:
            if cible == variante or cible[0] != variante[0]:
                continue
            if LP[cible][0] < RAPPORT_FREQ_OCR * max(fv, 1):
                continue
            if distance_edition(variante, cible) <= distance_max:
                # En cas de plusieurs cibles possibles, la plus fréquente
                if meilleure is None or LP[cible][0] > LP[meilleure][0]:
                    meilleure = cible
        if meilleure:
            fusions[variante] = meilleure

    rejetes = []
    for variante, cible in fusions.items():
        fm, fd = LP.pop(variante)
        cm, cd = LP[cible]
        LP[cible] = (cm + fm, cd + fd)
        rejetes.append((variante, f"variante OCR de {cible}"))

    return LP, rejetes


def main():
    antidico = charger_antidico(CHEMIN_ANTIDICO)
    print(f"Antidictionnaire : {len(antidico)} mots chargés")

    chemin_L = os.path.join(DOSSIER_RESULTATS, "liste_L.txt")
    candidats = charger_liste_L(chemin_L)
    print(f"Liste L : {len(candidats)} candidats chargés")

    tokens = charger_tokens_corpus()
    minuscules = compter_minuscules(tokens)

    gardes, rejetes_A = filtrer_grammatical(candidats, antidico, minuscules)
    print(f"Après l'étape A (bruit grammatical) : {len(gardes)} candidats")

    LP, rejetes_B = filtrer_personnes(gardes, tokens)
    LP, rejetes_C = fusionner_variantes_ocr(LP)
    for variante, raison in rejetes_C:
        print(f"Fusion : {variante} -> {raison.split()[-1]}")
    rejetes = rejetes_A + rejetes_B + rejetes_C

    # Export de LP, trié par fréquence décroissante (même format que L)
    chemin_LP = os.path.join(DOSSIER_RESULTATS, "liste_LP.txt")
    with open(chemin_LP, "w", encoding="utf-8") as f:
        f.write("candidat\tfreq_milieu\tfreq_debut\n")
        for candidat, (fm, fd) in sorted(LP.items(), key=lambda x: (-x[1][0], x[0])):
            f.write(f"{candidat}\t{fm}\t{fd}\n")

    # Export du détail des rejets : candidat, raison du rejet
    chemin_rejetes = os.path.join(DOSSIER_RESULTATS, "liste_L_rejetes.txt")
    with open(chemin_rejetes, "w", encoding="utf-8") as f:
        for candidat, raison in rejetes:
            f.write(f"{candidat}\t{raison}\n")

    print(f"LP : {len(LP)} personnes retenues")
    print(f"Rejetés : {len(rejetes)}")
    for raison, n in Counter(r for _, r in rejetes).most_common():
        if not raison.startswith("variante OCR"):
            print(f"    {raison:25s} {n}")
    print(f"    {'variante OCR':25s} {len(rejetes_C)}")
    print(f"Liste LP exportée dans {chemin_LP}")
    print(f"Détail des rejets exporté dans {chemin_rejetes}")


if __name__ == "__main__":
    main()
