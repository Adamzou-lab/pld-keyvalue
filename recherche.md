# Research Summary : le modèle clé-valeur

Équipe : [prénoms à compléter], PLD Alternative Data Models, Holberton School Toulouse

## 1. Qu'est-ce que le modèle stocke ?

[3-4 phrases. Pistes : paires clé → valeur, clé unique, valeur opaque que la base n'inspecte jamais, pas de tables ni de schéma.]

Source : [lien]

## 2. Comment organise-t-il les données ?

[3-4 phrases. Pistes : table de hachage en RAM, accès en temps constant, aucune relation entre les entrées, la seule organisation est la convention de nommage des clés (user:42, session:abc). Mentionner les structures riches de Redis : listes, hashes, sets, sorted sets.]

Schéma simple :

```
"session:abc123"  -> hash ->  { "user": "Adam", "panier": [...] }
"user:42"         -> hash ->  { nom: "Adam", ville: "Toulouse" }
"rate:adam"       -> hash ->  3
```

Source : [lien]

## 3. Comment fonctionnent les opérations de base ?

[Montrer SET / GET / DEL avec un exemple d'une ligne chacun. Particularités à souligner : l'update n'existe pas, c'est un SET qui écrase toute la valeur ; on ne peut chercher que par la clé exacte, jamais par le contenu.]

Source : [lien]

## 4. Pourquoi ce modèle existe-t-il ?

[Le problème qu'il résout : certains accès (sessions, cache, compteurs) n'ont besoin d'aucune capacité du SQL mais d'une vitesse extrême sous forte charge. Le SQL paie à chaque requête le prix de sa puissance : parser, planifier, vérifier le schéma, verrouiller. Le clé-valeur supprime tout et garde l'accès direct : latence < 1 ms, scalabilité horizontale facile car aucune relation à coordonner.]

Source : [lien]

## 5. Forces, limites, cas d'usage

À compléter pendant et après le POC avec des exemples vécus.

Forces :
- [vitesse mesurée : reporter ici le chiffre du bloc cache du POC, ex. 2 s → 2 ms]
- [TTL natif : expiration automatique, vs cron + DELETE en SQL]
- [INCR atomique : pas de race condition sans verrou ni transaction]

Limites :
- [pas de recherche par contenu : impossible de répondre à "toutes les sessions d'Adam" sans connaître les clés]
- [update = écrasement total de la valeur]
- [données en RAM : perte en cas de crash si la persistance n'est pas activée]

Cas d'usage : cache, sessions web, compteurs et rate limiting, files d'attente, leaderboards.

Persistance et clustering (à savoir expliquer, pas à mettre en place) :
- Par défaut tout est en RAM : acceptable pour des données reconstructibles (cache, sessions), pas pour des données précieuses.
- RDB : snapshots périodiques sur disque, rapide mais on peut perdre les dernières minutes. AOF : journal de chaque écriture, plus sûr mais plus lourd.
- Clustering : répartition des clés sur plusieurs nœuds par hachage, facile car pas de jointures ni de transactions multi-tables à coordonner.

## 6. Comparaison avec les autres modèles (section obligatoire)

### vs relationnel (SQL)

Plus simple : [lire/écrire un objet connu par sa clé, expirer des données, compter à haute fréquence (exemples du POC)]

Plus dur : [toute question analytique : pas de WHERE, pas de jointure, pas d'agrégation. Le SQL reste meilleur pour les données précieuses, les questions imprévues et la cohérence garantie.]

### vs document (équipe MongoDB)

[Mongo peut interroger l'intérieur des valeurs (requêtes sur champs, nested) ; Redis non, mais l'accès par clé est plus rapide. Le clé-valeur est idéal pour cacher les résultats des requêtes des autres bases. Aller voir l'équipe document 5 min pour confronter.]

### Place dans une architecture polyglotte

[Le clé-valeur ne remplace jamais la base principale, il la complète : PostgreSQL = source de vérité (comptes, commandes, cohérence), Redis devant = cache, sessions, rate limiting. Chaque donnée va dans le modèle taillé pour son mode d'accès.]

## 7. Ce qui nous a surpris

[À remplir au fil de la matinée, la consigne le demande explicitement. Premiers candidats : un update écrase toute la valeur ; la base ne peut littéralement pas chercher dans les valeurs ; la simplicité extrême du CRUD.]

## Sources

- Documentation officielle Redis : https://redis.io/docs/
- Try Redis (tutoriel interactif) : https://try.redis.io/
- GeeksforGeeks, Types of NoSQL Databases : [lien exact consulté]
- [autres sources au fil de l'eau]
