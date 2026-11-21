# Audit de réemploi — S0 v2

Le projet privé de référence a été consulté en lecture seule. L’analyse Graphify a porté sur une archive Git temporaire limitée au code, avec relecture des sources et des rapports. Les noms d’instances, adresses, identifiants et chemins propres à la référence restent hors de cet audit public.

## Décisions de réemploi

| Périmètre vérifié | Preuve et limite | Décision Audio Station |
| --- | --- | --- |
| Architecture et règles de travail | La session de simulation assemble séparément état, commandes, rendu et adaptateurs. Les règles et profils de la référence isolent les services historiques. | Reprendre les frontières et les défauts sûrs dans le dépôt indépendant. Rédiger la configuration et le démarrage propres à Audio Station. |
| UI Pillow et Inter | Le rendu et ses tests génèrent des images RGB 320 × 240. Une couche de dessin centralise la police, les mises en page et les caches. | Réimplémenter les écrans et leurs tests. Intégrer Inter en S5 depuis l’amont avec licence et provenance. |
| Tactile et GPIO | La chaîne sépare l’échantillonnage, les gestes, la distribution puis le routage des commandes. Les transports SPI et les séquences de rebond se testent par injection. Les mappings et conflits sont des observations ou propositions pour la référence. | Reprendre le découpage et les scénarios. Établir le brochage, les niveaux, les polarités et la calibration sur Audio Station. |
| Simulateur navigateur | Le navigateur et la simulation locale partagent la session et le framebuffer. Les tests du serveur portent sur HTTP, commandes et conversion des coordonnées. | Réimplémenter les adaptations utiles à un outil de développement. Les preuves de rendu et d’entrées physiques relèvent de tests séparés. |
| API Snapcast | La référence démontre la corrélation des réponses JSON-RPC, la gestion du flux NDJSON, les notifications, la resynchronisation, les temps d’attente et le volume par client sur un serveur de test à boucle locale. | Réimplémenter ce contrat injectable avec l’API officielle. Audio Station doit gérer ses propres clients, groupes, flux et volumes sur son serveur dédié. |
| Producteurs audio | Le socle stable simule la lecture et les métadonnées. Le prototype radio démontre la séparation entre décodeur PCM, états du lecteur et transport vers Snapcast. | Reprendre ces responsabilités, puis vérifier les formats et le traitement des reprises selon le [plan de sprints](docs/SPRINTS.md). |

## DEMO, matériel et dépendances exclues

Les écrans, la file de lecture et une partie des intégrations audio de la référence restent des simulations. Les essais historiques Tk, HTTP, tactiles injectés et Snapcast sur serveur de test démontrent des comportements logiciels. Leur couverture ne qualifie ni le nouvel écran ni le chemin stéréo MiniAmp. Le TFT, son contrôleur tactile, le SPI, le câblage et les sorties audio sont à vérifier sur le Pi d’Audio Station.

Les unités de service, scripts de démarrage, accès aux anciens GPIO, périphériques ALSA, profils réseau et instances audio des autres projets sont exclus. **Snapcast est une dépendance fonctionnelle du nouveau produit**. Audio Station possède son `snapserver` et son premier `snapclient` sur le Pi. Le client local à `127.0.0.1` est l’unique propriétaire de la sortie ALSA du MiniAmp en production. La référence a servi à l’observation du protocole et de ses frontières, sans connexion à ses services.

## Options retenues et licences

- Réécrire les seules abstractions utiles. La documentation de référence indique que la licence de son code et ses droits de publication restent à définir. Les sources, tests, configurations et visuels d’origine restent dans la référence.
- Séparer la police Inter des autres assets. Elle pourra être intégrée depuis sa distribution officielle sous SIL OFL 1.1, avec son fichier de licence et sa provenance. Le rendu S0 utilise la police fournie par Pillow. [Licence officielle Inter](https://github.com/rsms/inter/blob/master/LICENSE.txt)
- Démarrer S1 avec un serveur et un client dédiés sur la boucle locale, puis réserver le pilotage applicatif à S2 et la qualification multiroom à S11. Le chemin Spotify cible une FIFO, avec un processus qui émet du PCM sur stdout comme variante à qualifier. [Contrat Snapcast](docs/SNAPCAST_ARCHITECTURE.md)

Les dossiers et preuves consultés couvrent `AGENTS.md`, `ARCHITECTURE.md`, `HARDWARE_MAPPING.md`, `GPIO_CONFLICTS.md`, `AUDIO_ARCHITECTURE.md`, `ASSET_LICENSES.md`, les guides du simulateur navigateur, les modules UI et tactile, les tests et les comptes rendus.
