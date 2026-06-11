#!/usr/bin/python3
# ==================================================================
# POC Redis (key-value) - La vie d'un personnage de jeu video
# Chaque "# TODO" est un trou a completer par l'equipe.
# L'indice juste au-dessus dit quelle commande Redis utiliser.
# ==================================================================

import redis

# --- Connexion a Redis ---
# host       = adresse de la machine (localhost = la machine d'Adam)
# port       = 6379 (le port par defaut de Redis)
# decode_responses=True => on recoit du texte lisible (pas des octets bruts)
r = redis.Redis(host='localhost', port=6379, decode_responses=True)


# ==================================================================
# 1) FICHE DU PERSONNAGE  ->  structure HASH
#    Un HASH = plusieurs champs ranges sous UNE seule cle.
#    (exactement comme une fiche perso : nom, classe, niveau, PV)
#    Cle conseillee : "perso:1"
# ==================================================================

# --- CREATE : creer la fiche ---
# Indice : r.hset("perso:1", mapping={ ... })
#          Champs a mettre : name, classe, level, hp
# TODO :


# --- READ : lire toute la fiche ---
# Indice : r.hgetall("perso:1") renvoie un dictionnaire.
#          Range-le dans une variable, puis affiche-le avec print(...).
# TODO :


# --- UPDATE : le perso monte d'un niveau ---
# Indice : r.hincrby("perso:1", "level", 1) ajoute 1 au champ "level".
#          Affiche ensuite le nouveau niveau.
# TODO :


# ==================================================================
# 2) GAGNER DE L'XP  ->  COMPTEUR atomique (INCR)
#    Un compteur qui monte tout seul, sans bug, meme si plusieurs
#    actions arrivent en meme temps.  XP = points d'experience.
#    Cle conseillee : "perso:1:xp"
# ==================================================================

# Indice : r.incrby("perso:1:xp", 50) ajoute 50 (part de 0 si la cle n'existe pas).
# TODO :


# Indice : r.get("perso:1:xp") lit la valeur du compteur. Affiche-la.
# TODO :


# ==================================================================
# 3) BOIRE UNE POTION  ->  cle avec TTL (Time To Live = duree de vie)
#    La cle s'AUTO-DETRUIT apres X secondes :
#    l'effet de la potion disparait tout seul, sans rien faire.
#    Cle conseillee : "perso:1:potion:vitesse"
# ==================================================================

# Indice : r.set("perso:1:potion:vitesse", "active", ex=10)
#          ex=10 => la cle ne vit que 10 secondes.
# TODO :


# Indice : r.ttl("perso:1:potion:vitesse") = secondes restantes.
#          (-2 veut dire : deja disparue).  Affiche le temps restant.
# TODO :


# ==================================================================
# 4) FIN : supprimer le personnage  (le D de CRUD = Delete)
#    Pour que la demo couvre bien Create/Read/Update/Delete.
# ==================================================================

# Indice : r.delete("perso:1", "perso:1:xp")
# TODO :
