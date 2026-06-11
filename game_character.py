#!/usr/bin/python3
# ==================================================================
# POC Redis (clé-valeur) : la vie d'un personnage de jeu vidéo
#
# 6 blocs qui couvrent toutes les demandes du sujet :
#   1. Sauvegarde (string)     -> CRUD complet + écrasement total
#   2. Fiche perso (hash)      -> structure au-delà des strings
#   3. File de quêtes (liste)  -> file FIFO
#   4. Potion (TTL)            -> la feature distinctive
#   5. Anti-spam (rate limit)  -> le "small service" demandé
#   6. Classement (cache)      -> la persistance polyglotte en live
#
# Chaque "# TODO" est un trou à compléter par l'équipe.
# L'indice juste au-dessus dit quelle commande Redis utiliser.
# Lancer avec : python3 game_character.py (voir README.md)
# ==================================================================

import json
import time

import redis

# --- Connexion à Redis ---
# decode_responses=True : on reçoit du texte lisible, pas des octets bruts
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
print("Connexion Redis :", r.ping())
r.flushdb()  # base vide à chaque lancement, pour une démo reproductible


# ==================================================================
# 1) SAUVEGARDE DU JEU  ->  string : le CRUD de base
#    Une clé, une valeur. La base ne regarde JAMAIS dans la valeur.
#    Point clé à montrer : un update est un SET qui ÉCRASE TOUT.
#    Clé conseillée : "save:1"
# ==================================================================
print("\n=== 1. Sauvegarde (CRUD string) ===")

# --- CREATE : sauvegarder la partie ---
# Indice : save = {"zone": "forêt", "or": 100}
#          r.set("save:1", json.dumps(save))
# TODO :


# --- READ : recharger la partie ---
# Indice : r.get("save:1") puis json.loads(...). Affiche le résultat.
# TODO :


# --- UPDATE : le perso ramasse 50 pièces d'or ---
# Indice : il n'y a PAS de commande update : modifie le dict en Python
#          puis refais un r.set(...) : l'ancienne valeur est écrasée
#          EN ENTIER. C'est LA particularité du modèle à dire à l'oral.
# TODO :


# --- DELETE : effacer la sauvegarde, et le prouver ---
# Indice : r.delete("save:1") puis r.get("save:1") qui rend None.
# TODO :


# ==================================================================
# 2) FICHE DU PERSONNAGE  ->  structure HASH
#    Un hash = plusieurs champs rangés sous UNE seule clé.
#    C'est le remède à l'écrasement total vu au bloc 1 :
#    on peut lire/modifier UN champ sans toucher au reste.
#    Clé conseillée : "perso:1"
# ==================================================================
print("\n=== 2. Fiche perso (hash) ===")

# --- CREATE : créer la fiche ---
# Indice : r.hset("perso:1", mapping={"name": ..., "classe": ...,
#          "level": 1, "hp": 100})
# TODO :


# --- READ : lire toute la fiche ---
# Indice : r.hgetall("perso:1") renvoie un dictionnaire. Affiche-le.
# TODO :


# --- UPDATE : le perso monte d'un niveau ---
# Indice : r.hincrby("perso:1", "level", 1) ajoute 1 au champ "level"
#          sans toucher aux autres champs. Affiche le nouveau niveau.
# TODO :


# ==================================================================
# 3) FILE DE QUÊTES  ->  structure LISTE (file FIFO)
#    On empile les quêtes d'un côté, on les traite dans l'ordre
#    de l'autre. Une file d'attente en 2 commandes.
#    Clé conseillée : "perso:1:quetes"
# ==================================================================
print("\n=== 3. File de quêtes (liste) ===")

# Indice : r.rpush("perso:1:quetes", "tuer le dragon", "sauver le village",
#          "trouver le trésor") ajoute en fin de file.
# TODO :


# Indice : r.lpop("perso:1:quetes") retire et renvoie la PREMIÈRE quête.
#          Fais-le 3 fois dans une boucle : l'ordre d'arrivée est respecté.
# TODO :


# ==================================================================
# 4) BOIRE UNE POTION  ->  clé avec TTL (Time To Live)
#    La clé s'AUTODÉTRUIT après X secondes : l'effet de la potion
#    disparaît tout seul, sans cron, sans DELETE, sans rien.
#    En SQL il faudrait un script de ménage planifié.
#    Clé conseillée : "perso:1:potion:vitesse"
# ==================================================================
print("\n=== 4. Potion de vitesse (TTL) ===")

# Indice : r.set("perso:1:potion:vitesse", "active", ex=5)
#          ex=5 : la clé ne vit que 5 secondes.
# TODO :


# Indice : r.ttl("perso:1:potion:vitesse") = secondes restantes.
#          Affiche-le, puis time.sleep(6), puis r.get(...) qui rend
#          None : l'effet a disparu tout seul. (-2 = clé déjà disparue)
# TODO :


# ==================================================================
# 5) ANTI-SPAM D'ATTAQUES  ->  le "small service" : rate limiter
#    Règle du jeu : 5 attaques max par minute.
#    INCR est ATOMIQUE : deux attaques simultanées ne se marchent
#    jamais dessus, sans verrou ni transaction (en SQL il faudrait
#    une transaction). INCR + EXPIRE = un rate limiter en 4 lignes.
# ==================================================================
print("\n=== 5. Anti-spam d'attaques (rate limiter) ===")


def peut_attaquer(perso, limite=5):
    """Renvoie True si le perso a encore le droit d'attaquer."""
    cle = f"rate:attaque:{perso}"
    n = r.incr(cle)        # compteur atomique (part de 0 si la clé n'existe pas)
    if n == 1:
        r.expire(cle, 60)  # la fenêtre d'une minute démarre au premier coup
    return n <= limite


# Indice : boucle de 7 appels à peut_attaquer("perso:1").
#          Affiche "attaque i : OK" ou "attaque i : BLOQUÉE".
#          Attendu : 5 OK puis 2 BLOQUÉE.
# TODO :


# ==================================================================
# 6) CLASSEMENT DE LA GUILDE  ->  cache : la polyglotte en live
#    Le classement est calculé par la base SQL du jeu (lent : jointures,
#    agrégations). Redis ne REMPLACE pas le SQL : il se met DEVANT.
#    1er appel ~2 s (cache miss), 2e appel ~2 ms (cache hit).
#    C'est le message central du cours, démontré avec un chrono.
# ==================================================================
print("\n=== 6. Classement de guilde (cache) ===")


def calcul_sql_lent():
    """Simule la requête SQL coûteuse qui calcule le classement."""
    time.sleep(2)
    return json.dumps([{"perso": "Adam", "score": 980},
                       {"perso": "Sarah", "score": 940}])


def classement():
    """Renvoie le classement, via le cache Redis si possible."""
    en_cache = r.get("cache:classement")
    if en_cache is not None:
        return en_cache, "cache HIT (Redis)"
    resultat = calcul_sql_lent()
    r.set("cache:classement", resultat, ex=60)  # le cache expire tout seul
    return resultat, "cache MISS (requête SQL exécutée)"


# Indice : appelle classement() deux fois en chronométrant chaque appel :
#          debut = time.perf_counter()
#          resultat, source = classement()
#          duree = time.perf_counter() - debut
#          Affiche la source et la durée. Attendu : ~2 s puis ~0.002 s.
# TODO :
