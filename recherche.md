# Research Summary : le modèle clé-valeur

Équipe : David, Adam, Yo — PLD Alternative Data Models, Holberton School Toulouse

## 1. Qu'est-ce que le modèle stocke ?

Le modèle clé-valeur stocke des paires **clé → valeur**. Chaque clé est unique et sert d'unique point d'accès à sa valeur. La valeur est **opaque** : la base ne l'inspecte jamais, elle ne sait pas ce qu'il y a dedans. Il n'y a ni table, ni colonne, ni schéma imposé : on range une donnée sous une clé, et c'est tout.

Source : https://redis.io/docs/

## 2. Comment organise-t-il les données ?

Techniquement, c'est une grande **table de hachage** gardée en mémoire vive (RAM), ce qui donne un accès en temps quasi constant quelle que soit la taille de la base. Les entrées sont **indépendantes** : aucune relation entre elles. La seule organisation est la **convention de nommage des clés** (`user:42`, `session:abc`). Redis va au-delà de la simple chaîne de texte : il offre des structures riches — listes, hashes, sets, sorted sets — qui permettent files d'attente, profils, ensembles et classements.

Schéma simple :

```
"session:abc123"  -> hash ->  { "user": "Adam", "panier": [...] }
"user:42"         -> hash ->  { nom: "Adam", ville: "Toulouse" }
"rate:adam"       -> hash ->  3
```


## 3. Comment fonctionnent les opérations de base ?

Trois commandes suffisent :

```
SET user:42 "Adam"     # créer / écrire
GET user:42            # lire
DEL user:42            # supprimer
```

Deux particularités à souligner : l'**update n'existe pas** — un `SET` réécrit **toute** la valeur, pas un morceau ; et on ne peut chercher que par la **clé exacte**, jamais par le contenu d'une valeur.



## 4. Pourquoi ce modèle existe-t-il ?

Certains accès (sessions, cache, compteurs) n'ont besoin d'**aucune** capacité du SQL, mais d'une **vitesse extrême** sous forte charge. À chaque requête, le SQL paie le prix de sa puissance : parser, planifier, vérifier le schéma, verrouiller. Le clé-valeur supprime tout cela et ne garde que l'accès direct : latence inférieure à la milliseconde, et mise à l'échelle horizontale facile car il n'y a aucune relation à coordonner entre les nœuds.



## 5. Forces, limites, cas d'usage

**Forces :**
- **Vitesse mesurée dans notre POC** : le bloc « cache » passe de **~2 s** (requête SQL simulée) à **~1 ms** (lecture Redis), soit un facteur ~2000.
- **TTL natif** : les clés expirent automatiquement (notre potion disparaît seule après 5 s), là où le SQL demanderait un cron + un `DELETE`.
- **INCR atomique** : compteur sûr sans verrou ni transaction (notre rate limiter : 5 attaques par minute).

**Limites :**
- **Pas de recherche par contenu** : impossible de répondre à « toutes les sessions d'Adam » sans connaître les clés.
- **Update = écrasement total** de la valeur (vu au bloc 1 du POC).
- **Données en RAM** : risque de perte en cas de crash si la persistance n'est pas activée.

**Cas d'usage :** cache, sessions web, compteurs et rate limiting, files d'attente, leaderboards.

**Persistance et clustering** (à savoir expliquer, pas à mettre en place) :
- Par défaut tout est en RAM : acceptable pour des données reconstructibles (cache, sessions), pas pour des données précieuses.
- RDB : snapshots périodiques sur disque, rapide mais on peut perdre les dernières minutes. AOF : journal de chaque écriture, plus sûr mais plus lourd.
- Clustering : répartition des clés sur plusieurs nœuds par hachage, facile car pas de jointures ni de transactions multi-tables à coordonner.

## 6. Comparaison avec les autres modèles (section obligatoire)

### vs relationnel (SQL)

**Plus simple :** lire/écrire un objet connu par sa clé, expirer des données automatiquement, compter à haute fréquence (les exemples de notre POC).

**Plus dur :** toute question analytique — pas de `WHERE`, pas de jointure, pas d'agrégation. Le SQL reste meilleur pour les données précieuses, les questions imprévues et la cohérence garantie.

### vs document (équipe MongoDB)

MongoDB peut interroger l'**intérieur** des valeurs (requêtes sur champs, données imbriquées) ; Redis non, mais son accès par clé est plus rapide. Le clé-valeur est d'ailleurs idéal pour **cacher les résultats** des requêtes des autres bases. (À confronter 5 min avec l'équipe document.)

### Place dans une architecture polyglotte

Le clé-valeur ne remplace **jamais** la base principale, il la **complète** : PostgreSQL = source de vérité (comptes, commandes, cohérence), Redis **devant** = cache, sessions, rate limiting. Chaque donnée va dans le modèle taillé pour son mode d'accès.

## 7. Ce qui nous a surpris

- Qu'un update **écrase toute la valeur** : pas moyen de modifier juste un bout d'une string.
- Que la base ne puisse **littéralement pas** chercher dans les valeurs : on est totalement dépendant des clés.
- La **simplicité extrême** du CRUD comparée au SQL (trois commandes contre tout un langage).

## Sources

- Documentation officielle Redis : https://redis.io/docs/
- Try Redis (tutoriel interactif) : https://try.redis.io/
- GeeksforGeeks, *Types of NoSQL Databases* : https://www.geeksforgeeks.org/dbms/types-of-nosql-databases/

