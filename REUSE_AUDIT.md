# Audit de réemploi

L’audit S0 s’appuie sur la consultation en lecture seule du socle stable et d’un prototype radio du projet privé de référence. Graphify a indexé un instantané temporaire en mode code uniquement. Les conclusions reposent sur la lecture des sources et de leurs rapports de validation.

| Domaine | Constat dans le projet de référence | Décision pour Audio Station |
| --- | --- | --- |
| Architecture générale | Les interfaces desktop et web utilisent une session logique commune. Celle-ci relie l’état, le rendu et le traitement des commandes. | Reprendre cette séparation. Développer le modèle de lecture stéréo, le réveil et les écrans propres à Audio Station. |
| Rendu Pillow et Inter | Pillow produit un framebuffer RGB 320 × 240. Les primitives de dessin et l’accès à Inter sont centralisés. La provenance de la police est documentée avec sa licence OFL 1.1. | Garder un rendu natif testable par états. Créer les écrans d’Audio Station. Intégrer Inter en S1 avec sa licence et sa provenance. Le rendu S0 utilise la police de Pillow. |
| Simulateur web | La session publie des PNG et sérialise les commandes dans une file bornée. Le navigateur convertit les événements du pointeur en coordonnées 320 × 240. Le serveur contrôle les entrées, leur origine et les mutations. | Garder l’idée d’une session partagée, d’un framebuffer unique et de commandes injectées. Adapter les contrôles au produit. La prévisualisation web relève du développement. |
| Tactile et GPIO | L’acquisition, la calibration, la détection des gestes, l’anti-rebond, la quadrature et la distribution sont distincts. Un transport SPI partagé modélise la sélection des périphériques et le transfert RGB565. Le profil matériel stable est simulé. | Reprendre la séparation et les cas de test avec horloge et transport injectés. Identifier le contrôleur réel avant de développer l’adaptateur, la calibration et la table GPIO. |
| Audio et sources | Le socle stable simule les capacités des sources et la file de lecture. Un transport Snapcast optionnel permet de traiter le volume et le mute en multiroom. | Reprendre l’interface d’adaptateur, les instantanés d’état et les tests injectés. Concevoir la lecture stéréo locale et la sortie MiniAmp sans dépendance au routage multiroom. |
| Configuration | Des profils TOML distincts bornent les valeurs et différencient présence, activation et confirmation du matériel. Les secrets sont séparés des fichiers d’exemple. | Garder TOML, les défauts sûrs et la validation stricte. Écrire un schéma Audio Station. Le profil S0 valide une proposition de GPIO sans activer de matériel. |
| Tests et qualification | Les tests couvrent le rendu, les entrées, le serveur web et les transports injectés. Les smoke tests réseau utilisent des serveurs loopback éphémères. Les rapports distinguent simulations, essais logiciels et essais physiques. | Reprendre les fixtures contrôlées et la distinction des preuves. Développer un protocole de banc pour le TFT, les commandes et les deux canaux du MiniAmp. |

## Prototype radio et matériel

- Le prototype sépare les stations, les favoris SQLite et les tâches de recherche, de décodage et d’illustration. Ces responsabilités et leurs cas de test sont transférables à S2.
- Le décodeur radio utilise FFmpeg et émet du PCM stéréo. Le transport du prototype dirige ce PCM vers un listener TCP loopback pour Snapcast. Audio Station doit développer son propre adaptateur ALSA et qualifier le volume et l’audibilité stéréo sur le MiniAmp.
- Le backend Raspberry Pi de référence cible un autre écran. Sa méthode de diagnostic tactile, de collecte de mesures et d’endurance peut être adaptée après l’identification du module d’Audio Station. Les résultats de la référence ne qualifient pas le nouvel assemblage.

## Réemploi retenu

S0 transpose le framebuffer, les commandes indépendantes de leur origine, l’injection des dépendances et la validation hors ligne. Le code et les tests sont propres à Audio Station. Une reprise directe de code privé dépend de ses droits d’usage et de publication. La licence et la provenance d’Inter seront conservées lors de son intégration.
