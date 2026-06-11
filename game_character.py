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
# Lancer avec : python3 game_character.py (voir README.md)
# ==================================================================

import json
import time

import redis

# --- Connexion à Redis ---
# decode_responses=True : on reçoit du texte lisible, pas des octets bruts
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
print("Connexion Redis :", redis_client.ping())
redis_client.flushdb()  # base vide à chaque lancement, pour une démo reproductible


# ==================================================================
# 1) SAUVEGARDE DU JEU  ->  string : le CRUD de base
#    Une clé, une valeur. La base ne regarde JAMAIS dans la valeur.
#    Point clé à montrer : un update est un SET qui ÉCRASE TOUT.
#    Clé conseillée : "save:1"
# ==================================================================
print("\n=== 1. Sauvegarde (CRUD string) ===")

# --- CREATE : sauvegarder la partie ---
save = {"zone": "forêt", "or": 100}
redis_client.set("save:1", json.dumps(save))
print("Partie sauvegardée :", save)

# --- READ : recharger la partie ---
save = json.loads(redis_client.get("save:1"))
print("Partie rechargée :", save)

# --- UPDATE : le perso ramasse 50 pièces d'or ---
# Pas de commande "update" : on modifie en Python puis on refait un SET.
# L'ancienne valeur est écrasée EN ENTIER (point à dire à l'oral).
save["or"] = save["or"] + 50
redis_client.set("save:1", json.dumps(save))
print("Après ramassage d'or :", json.loads(redis_client.get("save:1")))

# --- DELETE : effacer la sauvegarde, et le prouver ---
redis_client.delete("save:1")
print("Après suppression (None attendu) :", redis_client.get("save:1"))


# ==================================================================
# 2) FICHE DU PERSONNAGE  ->  structure HASH
#    Un hash = plusieurs champs rangés sous UNE seule clé.
#    C'est le remède à l'écrasement total vu au bloc 1 :
#    on peut lire/modifier UN champ sans toucher au reste.
#    Clé conseillée : "perso:1"
# ==================================================================
print("\n=== 2. Fiche perso (hash) ===")

# --- CREATE : créer la fiche ---
redis_client.hset("perso:1", mapping={
    "name": "Aragorn",
    "classe": "Ranger",
    "level": 1,
    "hp": 100,
})
print("Fiche créée pour perso:1")

# --- READ : lire toute la fiche ---
fiche = redis_client.hgetall("perso:1")
print("Fiche complète :", fiche)

# --- UPDATE : le perso monte d'un niveau (sans toucher aux autres champs) ---
redis_client.hincrby("perso:1", "level", 1)
print("Nouveau niveau :", redis_client.hget("perso:1", "level"))


# ==================================================================
# 3) FILE DE QUÊTES  ->  structure LISTE (file FIFO)
#    On empile les quêtes d'un côté, on les traite dans l'ordre
#    de l'autre. Une file d'attente en 2 commandes.
#    Clé conseillée : "perso:1:quetes"
# ==================================================================
print("\n=== 3. File de quêtes (liste) ===")

# On empile 3 quêtes en fin de file.
redis_client.rpush("perso:1:quetes",
                   "tuer le dragon",
                   "sauver le village",
                   "trouver le trésor")
print("Quêtes en attente :", redis_client.lrange("perso:1:quetes", 0, -1))

# On les traite dans l'ordre d'arrivée (FIFO : premier arrivé, premier servi).
for i in range(3):
    quete = redis_client.lpop("perso:1:quetes")
    print(f"Quête traitée : {quete}")


# ==================================================================
# 4) BOIRE UNE POTION  ->  clé avec TTL (Time To Live)
#    La clé s'AUTODÉTRUIT après X secondes : l'effet de la potion
#    disparaît tout seul, sans cron, sans DELETE, sans rien.
#    En SQL il faudrait un script de ménage planifié.
#    Clé conseillée : "perso:1:potion:vitesse"
# ==================================================================
print("\n=== 4. Potion de vitesse (TTL) ===")

# ex=5 : la clé ne vit que 5 secondes.
redis_client.set("perso:1:potion:vitesse", "active", ex=5)
print("Potion bue. Temps restant :", redis_client.ttl("perso:1:potion:vitesse"), "s")

# On attend que la potion expire, puis on prouve qu'elle a disparu seule.
print("On attend 6 secondes...")
time.sleep(6)
print("Effet de la potion (None attendu) :", redis_client.get("perso:1:potion:vitesse"))
print("TTL après expiration (-2 = clé disparue) :", redis_client.ttl("perso:1:potion:vitesse"))


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
    n = redis_client.incr(cle)        # compteur atomique (part de 0 si la clé n'existe pas)
    if n == 1:
        redis_client.expire(cle, 60)  # la fenêtre d'une minute démarre au premier coup
    return n <= limite


# 7 attaques de suite : on attend 5 OK puis 2 BLOQUÉE.
for i in range(1, 8):
    if peut_attaquer("perso:1"):
        print(f"attaque {i} : OK")
    else:
        print(f"attaque {i} : BLOQUÉE")


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
    en_cache = redis_client.get("cache:classement")
    if en_cache is not None:
        return en_cache, "cache HIT (Redis)"
    resultat = calcul_sql_lent()
    redis_client.set("cache:classement", resultat, ex=60)  # le cache expire tout seul
    return resultat, "cache MISS (requête SQL exécutée)"


# Deux appels chronométrés : le 1er calcule (lent), le 2e lit le cache (rapide).
for appel in range(1, 3):
    debut = time.perf_counter()
    resultat, source = classement()
    duree = time.perf_counter() - debut
    print(f"Appel {appel} : {source} — {duree:.3f} s")

print("\n=== Démo terminée ===")
