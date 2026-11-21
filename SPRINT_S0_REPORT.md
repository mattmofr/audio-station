# Compte rendu du sprint S0

## Résultat

Audio Station dispose d’un dépôt Git local et de la branche `sprint/s0-bootstrap`. Le fichier d’instructions existant est conservé dans le commit de base et complété sur la branche S0. Le socle contient six modules Python, un profil TOML de démo et un point d’entrée CLI. L’environnement `.venv`, le PNG de démo et le graphe d’exploration sont des fichiers locaux ignorés par Git.

L’[audit de réemploi](REUSE_AUDIT.md) couvre le socle stable de la station de référence et son prototype radio. Le [contrat matériel](HARDWARE_CONTRACT.md) consigne les réservations BCM, la route SPI0 candidate et les prérequis électriques et mécaniques. Le [plan de sprints](SPRINT_PLAN.md) couvre l’interface, la lecture locale, le réveil, les essais Pi, le PCB et la recette finale.

## Vérifications sur le VPS

| Vérification | Résultat |
| --- | --- |
| Installation éditable avec Python 3.12.3 et Pillow 12.2.0 dans `.venv` | Réussie, dépendances cohérentes selon `pip check` |
| `.venv/bin/python -m unittest discover -s tests -v` | 11 tests réussis. Commandes et veille simulées, arrêt du réveil, volume borné, configuration et conflits GPIO, exécution de la DEMO sous garde I/O et contrôle du PNG |
| `.venv/bin/audio-station demo --config config/demo.toml --output .demo/frame.png` | Trace complète, arrêt du réveil pendant la veille et génération d’un PNG RGB 320 × 240 |
| Lecture seule du projet de référence | Même branche, même commit et même état Git constatés avant et après l’audit |

## Points ouverts

Le prochain sprint approfondira le rendu Inter, la navigation et les commandes simulées. La lecture locale, la radio et la programmation du réveil restent à implémenter. Le contrôleur tactile, les niveaux électriques, les affectations GPIO individuelles, le chemin stéréo et l’interconnexion PCB restent à vérifier sur le montage Raspberry Pi 3. Tous les résultats S0 concernent le logiciel et la simulation sur le VPS. Aucun essai de qualification matérielle n’a été effectué.

Le dépôt public de destination est `mattmofr/audio-station`.

## Recadrage Snapcast

Le chemin audio réel passe désormais par un serveur Snapcast dédié et un client local propriétaire de la sortie MiniAmp. Le socle de simulation S0 sert à préparer les adaptateurs et les comportements de groupe. L’[architecture actualisée](ARCHITECTURE.md) décrit les écarts avec la DEMO. Le [plan S0 à S11](SPRINT_PLAN.md) affecte la première qualification sur Pi à S1 et la mesure de synchronisation entre deux clients physiques ou plus à S11.
