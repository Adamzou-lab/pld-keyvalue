# POC clé-valeur (Redis) : la vie d'un personnage de jeu vidéo

PLD Alternative Data Models, Holberton School Toulouse.
Démonstration du modèle clé-valeur avec Redis à travers un fil rouge jeu vidéo : sauvegarde, fiche de personnage, quêtes, potions, anti-spam et classement.

## Lancer le POC

```bash
docker run --name redis -p 6379:6379 -d redis:latest
pip3 install redis
python3 game_character.py
```

Si le conteneur existe déjà : `docker start redis`.

## Contenu de game_character.py

1. Sauvegarde du jeu (string) : le CRUD de base, et la particularité du modèle (un update écrase toute la valeur)
2. Fiche du personnage (hash) : plusieurs champs sous une clé, modification d'un seul champ
3. File de quêtes (liste) : une file FIFO en deux commandes
4. Potion de vitesse (TTL) : la clé qui s'autodétruit toute seule
5. Anti-spam d'attaques (rate limiter) : 5 attaques par minute avec INCR atomique + EXPIRE
6. Classement de guilde (cache) : Redis devant une base SQL simulée, 2 s en cache miss, 2 ms en cache hit

Le fichier est à trous : chaque TODO est à compléter par l'équipe en suivant l'indice donné juste au-dessus.

## Fichiers

- `game_character.py` : le proof of concept
- `recherche.md` : le research summary (livrable écrit)
