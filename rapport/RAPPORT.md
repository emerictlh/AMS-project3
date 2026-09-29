# Génération automatique de graphes de personnages : détection d'entités nommées

**Binôme :** ESSID Youssef, TALAHA Emeric
**Langage :** Python 3 (plus la bibliothèque `pdfplumber` pour lire les PDF)

---

## 1. Ce qu'on devait faire

Le but du projet est de retrouver automatiquement les **personnages** et les **lieux** des trois romans *Fondation*, *Fondation et Empire* et *Seconde Fondation* d'Asimov. Plus tard, ces listes serviront à construire un graphe des personnages.

Le travail se fait en trois étapes, avec une liste produite à chaque étape :

| Liste | Ce qu'elle contient | Script | Nombre d'entrées |
|---|---|---|---:|
| **L** | tous les mots (ou groupes de mots) qui commencent par une majuscule | `src/liste_L.py` | 1 415 |
| **LP** | uniquement les personnages, triés à partir de L | `src/liste_LP.py` | 173 |
| **LL** | les lieux et les organisations, à partir de L et LP | `src/liste_LL.py` | 42 |

On n'a pas utilisé d'outil tout fait, comme un étiqueteur grammatical ou un modèle déjà entraîné. On a préféré écrire nos propres règles, pour pouvoir expliquer chaque décision. Pour chaque mot rejeté de LP, on a d'ailleurs noté la raison du rejet dans `resultats/liste_L_rejetes.txt`.

## 2. Le corpus

On a d'abord transformé les PDF en fichiers texte avec `pdfplumber` (`src/extraire_texte.py`). On ajoute une ligne `=== PAGE N ===` au début de chaque page et on enlève les numéros de page.

| Livre | Pages | Mots | Phrases |
|---|---:|---:|---:|
| Fondation | 108 | 35 114 | 3 121 |
| Fondation et Empire | 116 | 38 962 | 3 318 |
| Seconde Fondation | 120 | 39 677 | 3 130 |
| **Total** | **344** | **113 753** | **9 569** |

**Attention, le corpus ne contient qu'une page sur deux** (les pages impaires). Une phrase peut donc être coupée en bas d'une page et « continuer » sur une page qui n'a rien à voir. Pour éviter de coller des mots qui ne vont pas ensemble, on traite **chaque page séparément**. On recolle aussi les mots coupés en fin de ligne (« Anacré- / on » devient « Anacréon »).

**Faut-il enlever la ponctuation ?** On a choisi de la garder, parce qu'elle nous aide :
- un point indique le début d'une nouvelle phrase, et un guillemet ou un tiret le début d'une réplique. Dans les deux cas, le premier mot prend une majuscule même si ce n'est pas un nom propre ;
- l'apostrophe permet de voir qu'il y a un article ou une préposition devant un nom (*l'Empire*, *d'Anacréon*), ce qui nous sert beaucoup pour les tâches 2 et 3.

## 3. Tâche 1 : la liste L

**Idée :** en français, un nom propre commence par une majuscule. On récupère donc tous les mots qui commencent par une majuscule.

On découpe chaque page en phrases, puis en mots. Pour chaque mot avec une majuscule, on garde :
- le mot seul : « Hari » ;
- le mot avec le suivant, s'il a aussi une majuscule : « Hari Seldon » ;
- le groupe de trois mots, si le troisième a aussi une majuscule : « Commodore Asper Argo ».

C'est ce qu'on appelle des **n-grammes** : des suites de 1, 2 ou 3 mots. On ignore les lettres seules, comme le « L » de *L'homme* ou le « C » de *C'est*.

**Problème :** en début de phrase, tous les mots ont une majuscule (« Mais », « Ecoutez »…). Au lieu de les jeter, on compte deux nombres pour chaque candidat :
- `freq_milieu` : le nombre de fois où il apparaît **au milieu d'une phrase**. Là, la majuscule veut vraiment dire quelque chose ;
- `freq_debut` : le nombre de fois où il apparaît **en début de phrase ou de réplique**.

Par exemple, « Seldon » apparaît 175 fois en milieu de phrase, alors que « Ecoutez » n'y apparaît jamais. Cette information servira à trier la liste à l'étape suivante.

**Résultat :** 1 415 candidats. On y trouve bien les noms importants (Mulet, Seldon, Trantor…), mais aussi beaucoup de « bruit » : des mots courants, des titres de chapitres, des verbes, et même des erreurs de lecture du PDF (« FRQWUHF »).

## 4. Tâche 2 : la liste LP (les personnages)

On trie la liste L en trois étapes.

### Étape A : enlever le bruit

On applique 8 règles simples. Dès qu'un candidat vérifie une règle, il est rejeté.

| Règle | Exemples rejetés |
|---|---|
| 1. mot écrit tout en MAJUSCULES (titres de chapitres) | PARTIE, GALACTICA |
| 2. erreur de lecture du PDF, chiffre romain | Hmm, GHOj, II |
| 3. mot très courant (liste de 702 « mots vides » : le, mais, il…) | Mais, Il, Alors |
| 4. mot plus souvent écrit en minuscule qu'avec une majuscule | Plan, Espace |
| 5. verbe à l'impératif (terminé par *-ez* ou *-ons*) | Ecoutez, Supposons |
| 6. nom d'habitants (terminé par *-ien*, *-ienne*…) | Korellienne |
| 7. simple titre ou fonction | Maire, Premier Orateur |
| 8. nom de bâtiment ou de rue | Building Hardin |

La **règle 4** est la plus utile. Si « plan » apparaît souvent en minuscule dans le livre, alors « Plan » avec une majuscule est sûrement juste un mot en début de phrase, pas un nom propre. On compare les deux nombres au lieu de rejeter un mot dès qu'on le voit une fois en minuscule. Sinon, on aurait perdu « Mis » (le personnage Ebling Mis, 64 fois) à cause du participe « mis » (27 fois). En lisant le survey conseillé dans le sujet [6], on a vu que cette idée est une méthode connue (Mikheev, 1999).

Après cette étape, il reste 434 candidats.

### Étape B : personne ou pas ?

Les règles précédentes ne font pas la différence entre « Mallow » (un personnage) et « Trantor » (une planète). Pour ça, on regarde **les mots autour** de chaque candidat dans le texte :

- **indices de personne** :
  - un verbe de parole juste avant : « … », *dit Mallow* ;
  - un titre juste avant : *capitaine Pritcher* ;
  - un verbe de geste juste après : *Bayta sourit*.
- **indices de non-personne** :
  - un article juste avant : *la Galaxie* (en français, on ne met pas d'article devant un prénom) ;
  - une préposition de lieu : *sur Trantor*, *planète Synnax*.

On compte ces indices sur tout le livre, et le candidat est classé du côté où il y en a le plus. Il y a un cas particulier : « le Mulet » a un article, mais il parle beaucoup (*dit le Mulet*). On a donc décidé qu'à partir de 3 indices de personne, on garde le candidat.

Pour les noms en deux mots, on s'aide des mots seuls. Par exemple, « Preem » n'apparaît qu'une fois, sans aucun indice. Mais comme « Preem Palver » est reconnu comme une personne, on garde aussi « Preem ».

### Étape C : corriger les fautes de lecture du PDF

Quelques noms sont mal lus par le PDF. Si un nom rare ressemble beaucoup à un nom fréquent (une ou deux lettres de différence), on les regroupe. Par exemple, « Magnifiée » devient « Magnifico ». On a mis des limites pour ne pas regrouper deux vrais personnages différents, comme « Lev » et « Lee ».

### Résultat

LP contient **173 entrées** : Mulet, Seldon, Hardin, Mallow, Bayta, Ebling Mis, Salvor Hardin, Bel Riose…

Pour vérifier, on a annoté à la main les 100 mots les plus fréquents de L (personnage ou non), puis on a comparé avec LP (`src/evaluer_LP.py`) :
- **précision de 100 %** : tout ce qu'on a gardé est bien un personnage ;
- **rappel de 96,2 %** : on a retrouvé presque tous les personnages.

Il ne manque que « Bay » et « Torie », les surnoms de Bayta et Toran, qui n'apparaissent que dans les dialogues.

## 5. Tâche 3 : la liste LL (les lieux)

On part de L, et on enlève le bruit, tous les personnages de LP et les mots courants (avec la même règle 4 que pour LP). Il reste 377 candidats.

Ensuite, on utilise la même idée que pour les personnes : on regarde **le mot juste avant** chaque candidat dans le texte.

| Mot juste avant | Exemple | Ce que ça indique |
|---|---|---|
| *sur*, *depuis*, *planète*, *monde*… | *sur Kalgan*, *la planète Terminus* | un lieu (indice fort) |
| *de*, *d'* | *d'Anacréon* | un lieu, mais un indice faible car on dit aussi « le plan de Seldon » |
| *la*, *l'* | *la Fondation*, *l'Empire* | une organisation |
| un titre ou un verbe de parole | *dit X* | une personne, donc pas un lieu |

Un candidat est gardé s'il a assez d'indices de lieu, et beaucoup plus que d'indices de personne. Pour les noms qui n'apparaissent qu'une ou deux fois, on demande au moins un indice fort, comme « la planète Synnax ». Ça permet de récupérer des planètes citées une seule fois.

**Résultat :** LL contient **42 entrées** (28 lieux et 14 organisations) : Trantor, Kalgan, Anacréon, Terminus, Siwenna, Fondation, Seconde Fondation, Empire Galactique…

On n'a pas eu le temps de faire une vraie évaluation comme pour LP. En vérifiant les 42 entrées une par une dans le texte, on en compte environ **35 correctes, soit ≈ 83 %**. La règle 4 nous a fait gagner des points : avant de l'ajouter, on était à ≈ 77 %. Les erreurs qui restent sont par exemple *Etat*, *Unimara* (en fait, un vaisseau) et *Korellienne* (un nom d'habitants).

## 6. Nos difficultés et les limites

En une semaine, on n'a pas tout réussi. Voici où on a bloqué :

- **Les noms avec « de » ou « des ».** Notre liste L ne colle que des mots **qui se suivent** et qui ont tous une majuscule. Des noms comme « Association des Marchands Indépendants » sont donc coupés en morceaux. Si on accepte « de » et « des » dans les noms, on récupère aussi beaucoup de faux noms (« Hardin de Terminus »). On n'a pas trouvé de bon compromis.
- **Lieu ou organisation ?** On se base seulement sur le mot d'avant. Du coup, « la Galaxie » est classée comme une organisation, parce qu'elle a un article comme « la Fondation ».
- **Les noms rares.** Environ 200 mots n'apparaissent qu'une ou deux fois, sans aucun indice autour. On ne sait pas les classer, alors qu'il y a parmi eux de vrais lieux (*Hélicon*) et des personnages secondaires. Comme il manque une page sur deux, c'est fréquent.
- **Les surnoms avec un article.** « le Mulet » est bien trouvé, mais pas « le Renard », qui est pris pour une non-personne à cause de son article.
- **Les accents.** En français, on écrit souvent les majuscules sans accent. Notre règle 4 compare donc « Etat » avec « etat » au lieu de « état », et laisse passer *Etat* dans LL.
- **Nos scores sont un peu trop optimistes.** On a construit nos règles en lisant ces mêmes livres, et on n'a testé que les mots les plus fréquents. Sur un autre roman, les résultats seraient sûrement moins bons.
- **Pour le graphe.** Un même personnage apparaît sous plusieurs noms (*Hari*, *Seldon*, *Hari Seldon*). Il faudra les regrouper avant de construire le graphe.

## 7. Fichiers rendus et lancement

- `resultats/` : les listes `liste_L.txt`, `liste_LP.txt` et `liste_LL.txt`, les rejets de LP avec leur raison (`liste_L_rejetes.txt`) et les statistiques du corpus (`stats_corpus.txt`). La première ligne de chaque liste donne le nom des colonnes.
- `ressources/` : la liste des mots vides et notre annotation manuelle pour l'évaluation.

Pour tout relancer depuis la racine du projet (avec les PDF dans `corpus/`) :

```
python src/extraire_texte.py
python src/liste_L.py
python src/liste_LP.py
python src/evaluer_LP.py
python src/liste_LL.py
```

## Références

[6] Nadeau, D. et Sekine, S. (2007). *A Survey of Named Entity Recognition and Classification*. Lingvisticae Investigationes, 30(1), pp. 3-26 (référence [6] du sujet), section 3.3.1.

Mikheev, A. (1999). *A Knowledge-free Method for Capitalized Word Disambiguation*. Proc. ACL 1999.
