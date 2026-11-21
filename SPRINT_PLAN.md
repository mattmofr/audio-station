# Plan de sprints

Créer une branche indépendante par sprint à partir de la base d’intégration validée. Pour chaque livraison, fournir les tests, la documentation et un compte rendu. Le statut d’un essai matériel se fonde sur des observations consignées sur le Raspberry Pi 3 cible.

| Sprint | Livrable | Critère de sortie |
| --- | --- | --- |
| S0 · Socle | Dépôt indépendant, audit de réemploi, six modules, environnement Python, DEMO et contrat matériel | Tests hors ligne, trace reproductible et PNG 320 × 240 |
| S1 · Interface et commandes | Rendu Pillow avec Inter, écrans de lecture et de réglage, gestes et commandes injectés, simulateur interactif de développement | Parcours simulés avec coordonnées 320 × 240 et séquences de rebond/quadrature |
| S2 · Audio local et radio | Choix du moteur de lecture, playlist locale, stations radio, volume et gestion des erreurs | Décodage et transitions testés sur fixtures et flux contrôlés, chemin stéréo prêt pour le banc Pi |
| S3 · Réveil | Horloge injectable, programmation, persistance et commande d’arrêt capacitive, sonnerie locale de secours | Cas de redémarrage, changement d’heure, perte de réseau et arrêt testés avec une horloge simulée |
| S4 · Banc Raspberry Pi | Identifier les révisions et broches, valider niveaux et alimentation, mettre en service TFT, tactile, commandes et MiniAmp sur le montage réel | Matrice de brochage relevée, mesures électriques, preuves de commande et d’écoute stéréo consignées |
| S5 · PCB | Schéma, empreintes, implantation et routage du PCB d’interconnexion avec connecteurs de commandes en bord | Revue du schéma, ERC/DRC, vérification mécanique et plan de qualification du prototype |
| S6 · Autonomie | Recette longue durée sur le Pi, prise en charge des redémarrages et procédure de mise en service | Tests sur montage final et procédure de démarrage revue. Toute installation ou modification système exige l’autorisation explicite de l’utilisateur. |

Le schéma S5 dépend des identifications et mesures de S4. La sélection du moteur et le comportement de l’alarme sont validés séparément des mesures électriques. La publication GitHub fait l’objet d’une proposition avant toute création ou publication distante.
