# POC clé-valeur (Redis) : la vie d'un personnage de jeu vidéo

PLD Alternative Data Models, Holberton School Toulouse.
Équipe : David, Adam, Yo.

Démonstration du modèle clé-valeur avec Redis à travers un fil rouge jeu vidéo : sauvegarde, fiche de personnage, quêtes, potions, anti-spam et classement. Le tout illustre l'idée centrale du cours : la persistance polyglotte, où chaque type de donnée va dans la base taillée pour son mode d'accès.

## Lancer le POC

```bash
docker run --name redis -p 6379:6379 -d redis:latest
pip3 install redis
python3 game_character.py
```

Si le conteneur existe déjà : `docker start redis`.
Le script dure une dizaine de secondes (il attend volontairement l'expiration d'une clé TTL et simule une requête SQL lente).

## Contenu de game_character.py

1. Sauvegarde du jeu (string) : le CRUD de base, et la particularité du modèle (un update écrase toute la valeur)
2. Fiche du personnage (hash) : plusieurs champs sous une clé, modification d'un seul champ avec HINCRBY
3. File de quêtes (liste) : une file FIFO en deux commandes (RPUSH, LPOP)
4. Potion de vitesse (TTL) : la clé s'autodétruit toute seule, sans cron ni script de ménage
5. Anti-spam d'attaques (rate limiter) : 5 attaques par minute avec INCR atomique + EXPIRE
6. Classement de guilde (cache) : Redis devant une base SQL simulée

Résultat mesuré sur le bloc 6 : 2.003 s en cache miss (requête SQL simulée), 0.001 s en cache hit (Redis), soit un facteur 2000.

## Fichiers

- `game_character.py` : le proof of concept, complet et fonctionnel
- `recherche.md` : le research summary (livrable écrit, 1 à 2 pages)
- `presentation.key` / `presentation.pptx` : la présentation (10 slides, les 7 questions du sujet dans l'ordre)
- `Diagram_of_margaid.png` : le schéma d'ensemble des 6 concepts du POC (intégré en slide 5)
- `Mermaid_diagram.png` : diagramme du personnage
