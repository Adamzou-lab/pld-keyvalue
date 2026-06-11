# POC clé-valeur — Redis

PLD Alternative Data Models — Holberton School Toulouse.
Démonstration du modèle clé-valeur avec Redis : CRUD, structures de données, TTL, rate limiter et cache.

## Lancer le POC

```bash
docker run --name redis -p 6379:6379 -d redis:latest
pip3 install redis
python3 poc.py
```

Si le conteneur existe déjà : `docker start redis`.

## Contenu de poc.py

1. CRUD : créer, lire, écraser, supprimer une session (SET, GET, DEL)
2. Structures de données : hash (profil utilisateur) et liste (file FIFO)
3. TTL : une clé qui expire toute seule
4. Rate limiter : 5 requêtes par minute avec INCR atomique + EXPIRE
5. Cache devant une base SQL simulée : 2 s en cache miss, 2 ms en cache hit

## Fichiers

- `poc.py` : le proof of concept
- `recherche.md` : le research summary (livrable écrit)
