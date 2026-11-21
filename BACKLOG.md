# Backlog Audio Station

Les éléments ci-dessous sont obligatoires pour l’architecture cible. L’avancement fonctionnel démarre de la DEMO validée en S0. Les preuves sur Pi sont ajoutées avec les comptes rendus des sprints concernés.

| ID | Travail | Critère d’acceptation | Sprint |
| --- | --- | --- | --- |
| B01 | Socle et contrat Snapcast | DEMO hors ligne, module de lecture simulé, architecture, plan, prompts et procédure disponibles | S0 |
| B02 | Serveur et premier client sur Pi 3 | `snapserver` dédié, client local identifié à `127.0.0.1`, route exclusive MiniAmp, stéréo et reprise locale prouvées sur le montage | S1 |
| B03 | Découverte et suivi des clients | Inventaire JSON-RPC, connexion, déconnexion et état incertain visibles. Un nouvel instantané réconcilie le modèle à la reconnexion. | S2 |
| B04 | Groupes et flux | Affecter les membres et le flux à partir de l’état confirmé. Relire l’état après modification et interrompre une commande ciblant un objet périmé. | S2 |
| B05 | Volume et mute individuels et de groupe | Appliquer le volume et le mute à un client. Utiliser le mute de groupe officiel et vérifier l’application du volume aux membres concernés, y compris en cas de réponse partielle. | S2 |
| B06 | Music | Radio et fichiers locaux décodés vers `Music`, avec format PCM vérifié et gestion des erreurs de source | S3 |
| B07 | Spotify | go-librespot alimente `Spotify` par pipe ou processus PCM avec format vérifié et identité/configuration gardées hors du dépôt public | S4 |
| B08 | TFT Multiroom | Clients, présence, groupes, flux, volume, mute et état de reconnexion visibles et pilotables à 320 × 240 | S5 |
| B09 | Encodeur local | Une rotation règle uniquement le volume du `snapclient` local identifié dans la configuration | S5, S7 |
| B10 | Réveil local avec sonnerie disponible hors ligne | Horaire persistant et sonnerie PCM identifiée. Démarrage uniquement après isolement confirmé. Arrêt à la commande dédiée. | S6 |
| B11 | Restauration de groupe | Arrêt du PCM et reprise contrôlée du routage. Les tests couvrent perte de contrôle, redémarrage et modification concurrente sans écraser les changements externes confirmés. | S6, S11 |
| B12 | Commandes et PCB | Prototyper et mesurer le TFT, le tactile, les commandes et l’alimentation. Réserver les GPIO MiniAmp et placer les connecteurs en bord de PCB. | S7, S8 |
| B13 | Autonomie et reconnexion | Fichiers locaux et sonnerie utilisables après perte d’Internet. Reprise testée après rupture d’un producteur, du serveur ou d’un client, avec sortie ALSA toujours réservée au `snapclient`. | S9 |
| B14 | Réseau Snapcast | Contrôle local et flux autorisés exclusivement sur le LAN de recette. Preuve d’absence d’exposition Internet et de non-interférence avec les autres services. | S1, S10 |
| B15 | Synchronisation multiroom | Mesure simultanée sur au moins deux clients physiques, dont le Pi local, à la connexion et après reconnexion. Vérifier l’écoute du même flux et la confidentialité du réveil vis-à-vis des clients non ciblés. | S11 |

Voir le [contrat Snapcast](docs/SNAPCAST_ARCHITECTURE.md) pour les invariants d’isolement et la [procédure de déploiement](docs/DEPLOYMENT.md) pour les essais autorisés.
