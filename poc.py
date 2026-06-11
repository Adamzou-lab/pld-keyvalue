"""POC clé-valeur (Redis) pour le PLD Alternative Data Models.

Scénario fil rouge : la session web d'un site e-commerce.
5 blocs : CRUD, structures de données, TTL, rate limiter, cache.
Lancer avec : python3 poc.py (Redis doit tourner, voir README.md)
"""

import json
import time

import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)
print("Connexion Redis :", r.ping())
r.flushdb()  # base vide à chaque lancement, pour une démo reproductible


# ---------------------------------------------------------------
# BLOC 1 : CRUD (créer, lire, mettre à jour, supprimer)
# Particularité du modèle : l'update n'existe pas, c'est un SET
# qui écrase TOUTE la valeur (la base ne voit pas l'intérieur).
# ---------------------------------------------------------------
print("\n=== BLOC 1 : CRUD ===")

# TODO Create : SET d'une session JSON sous la clé "session:abc123"
#   session = {"user": "Adam", "ville": "Toulouse", "panier": []}
#   r.set("session:abc123", json.dumps(session))

# TODO Read : GET + json.loads, afficher le résultat

# TODO Update : ajouter un article au panier côté Python,
#   puis re-SET (montrer que tout est réécrit)

# TODO Delete : DEL puis GET qui rend None (le prouver avec un print)


# ---------------------------------------------------------------
# BLOC 2 : structures de données (au-delà des strings)
# Hash : permet de lire/modifier UN champ sans tout réécrire
# (c'est le remède à la limite vue au bloc 1).
# Liste : une file d'attente FIFO en 2 commandes.
# ---------------------------------------------------------------
print("\n=== BLOC 2 : structures de données ===")

# TODO Hash : r.hset("user:42", mapping={"nom": "Adam", "ville": "Toulouse"})
#   puis r.hgetall("user:42"), puis modifier UN seul champ avec hset

# TODO Liste : r.rpush("file:emails", "mail1", "mail2", "mail3")
#   puis 3 r.lpop pour montrer l'ordre FIFO


# ---------------------------------------------------------------
# BLOC 3 : TTL, la donnée qui s'autodétruit
# En SQL il faudrait un cron + DELETE ; ici c'est natif.
# ---------------------------------------------------------------
print("\n=== BLOC 3 : TTL ===")

# TODO : r.set("session:temp", "donnee-ephemere", ex=5)
#   afficher r.ttl("session:temp") une ou deux fois (compte à rebours),
#   time.sleep(6), puis GET qui rend None


# ---------------------------------------------------------------
# BLOC 4 : rate limiter, le "small service" demandé par la doc
# INCR est atomique : deux requêtes simultanées ne se marchent
# jamais dessus, sans verrou ni transaction.
# ---------------------------------------------------------------
print("\n=== BLOC 4 : rate limiter (5 requêtes / minute) ===")


def autoriser(user, limite=5):
    """Retourne True si l'utilisateur a encore droit à une requête."""
    cle = f"rate:{user}"
    n = r.incr(cle)        # compteur atomique
    if n == 1:
        r.expire(cle, 60)  # la fenêtre d'une minute démarre
    return n <= limite


# TODO : boucle de 7 appels à autoriser("adam"),
#   afficher "requête i : OK" ou "requête i : BLOQUÉ"
#   (attendu : 5 OK puis 2 BLOQUÉ)


# ---------------------------------------------------------------
# BLOC 5 : cache, la persistance polyglotte en live
# Redis ne remplace pas la base SQL, il se met DEVANT :
# 1er appel ~2 s (cache miss), 2e appel ~2 ms (cache hit).
# ---------------------------------------------------------------
print("\n=== BLOC 5 : cache devant une base SQL ===")


def requete_sql_lente(ville):
    """Simule une requête PostgreSQL coûteuse (agrégation, jointures...)."""
    time.sleep(2)
    return json.dumps({"ville": ville, "offres_alternance": 42})


def avec_cache(ville):
    cle = f"cache:offres:{ville}"
    resultat = r.get(cle)
    if resultat is not None:
        return resultat, "cache HIT"
    resultat = requete_sql_lente(ville)
    r.set(cle, resultat, ex=60)  # le cache expire tout seul au bout d'1 min
    return resultat, "cache MISS (requête SQL exécutée)"


# TODO : appeler avec_cache("Toulouse") deux fois en chronométrant
#   avec time.perf_counter(), afficher le temps de chaque appel
#   (attendu : ~2 s puis ~0.002 s)
