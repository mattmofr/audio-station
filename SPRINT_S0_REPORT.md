# Compte rendu du sprint S0

## Résultat

Le premier socle d’Audio Station a été livré sur `sprint/s0-bootstrap`. Il comprend six modules Python, un profil TOML de démo et un point d’entrée CLI. L’environnement `.venv`, le PNG de démo et le graphe d’exploration sont des fichiers locaux ignorés par Git.

L’[audit de réemploi](REUSE_AUDIT.md) couvre le socle stable de la station de référence et son prototype radio. Le [contrat matériel](docs/HARDWARE_CONTRACT.md) consigne les réservations BCM, la route SPI0 candidate et les prérequis électriques et mécaniques.

## Vérifications du premier socle sur le VPS

| Vérification | Résultat |
| --- | --- |
| Installation éditable avec Python 3.12.3 et Pillow 12.2.0 dans `.venv` | Réussie, dépendances cohérentes selon `pip check` |
| `.venv/bin/python -m unittest discover -s tests -v` | 11 tests réussis. Commandes et veille simulées, arrêt du réveil, volume borné, configuration et conflits GPIO, exécution de la DEMO sous garde I/O et contrôle du PNG |
| `.venv/bin/audio-station demo --config config/demo.toml --output .demo/frame.png` | Trace complète, arrêt du réveil pendant la veille et génération d’un PNG RGB 320 × 240 |
| Lecture seule du projet de référence | Même branche, même commit et même état Git constatés avant et après l’audit |

## Reprise S0 v2

La reprise `sprint/s0-v2` part du recadrage Snapcast et complète le répertoire Audio Station existant. Elle ajoute la spécification v2, place les documents de référence sous `docs/`, prépare l’espace KiCad et fournit une CI locale. Le code de configuration et d’assemblage est désormais dans `src/audio_station/infra`. Les anciens chemins d’import et les liens des documents racine redirigent vers leur emplacement de référence.

Le dépôt proposé `mattmofr/audio-station` est déjà public et configuré comme `origin`. Les changements de ce sprint sont livrés sur la branche locale.

### Choix et variantes

- Réimplémenter les abstractions utiles d’après la référence consultée en lecture seule. Les droits de son code et de ses tests restent à clarifier avant tout réemploi direct. La police Inter a une licence propre. [Audit de réemploi](REUSE_AUDIT.md)
- Composer avec un serveur Snapcast dédié et son client local, seul utilisateur de la sortie MiniAmp en production. La FIFO est le premier choix pour Spotify. Le processus qui émet du PCM sur stdout reste une variante. [Contrat Snapcast](docs/SNAPCAST_ARCHITECTURE.md)
- Garder le rendu et le lecteur DEMO pour les validations sur VPS. La garde statique rejette les accès ALSA directs détectables dans le code Python. La vérification des processus qui ouvrent réellement le périphérique relève de S1. [Architecture](docs/ARCHITECTURE.md)

### Vérifications S0 v2

La CI locale a passé `pip check` et 24 tests, dont la simulation sous garde réseau et périphériques, la garde ALSA et la compatibilité du chemin d’import historique. Le point d’entrée installé a exécuté le scénario et produit un PNG RGB 320 × 240.

### Points ouverts

S1 commence par l’inventaire du Pi et la qualification réelle de `Music → snapserver → snapclient → MiniAmp`. L’installation éventuelle et les changements de configuration exigent un accord explicite. L’identification du tactile, les mesures électriques et le brochage précèdent le routage du PCB. La synchronisation des clients physiques devra être mesurée en S11. [Plan S0 à S11](docs/SPRINTS.md) · [Déploiement](docs/DEPLOYMENT.md)
