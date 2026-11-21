# AGENTS.md — Audio Station

Ces instructions s’appliquent à tout le dossier Audio Station. Elles complètent le `AGENTS.md` global, qui reste applicable.

## Objectif

Développer un lecteur musical stéréo, un radio-réveil autonome et une station multiroom Snapcast sur Raspberry Pi 3 en s’appuyant sur les principes logiciels étudiés dans le projet de référence.

## Périmètre de travail

- Consulter le projet de référence uniquement en lecture seule.
- Limiter les modifications à Audio Station. Les services et les autres projets existants sont hors périmètre.
- Réserver le VPS au développement. Le Raspberry Pi 3 est l’équipement final.
- Obtenir l’autorisation explicite de l’utilisateur avant toute installation de service ou modification de la configuration système.
- Utiliser une instance Snapcast dédiée à Audio Station. Les serveurs Snapcast des autres projets sont hors périmètre.
- Limiter le contrôle Snapcast à la boucle locale et la diffusion au réseau local autorisé. Toute exposition de ports Snapcast sur Internet est interdite.

## Matériel disponible

- Raspberry Pi 3.
- Écran TFT ILI9341 SPI de 3,2 pouces, 320 × 240, en paysage, avec contrôleur tactile intégré.
- Encodeur rotatif avec poussoir.
- Quatre boutons momentanés pour les commandes précédent, lecture/pause, suivant et veille. Le bouton de veille intègre une LED.
- Modules capacitifs, dont un dédié à l’arrêt du réveil.
- HiFiBerry MiniAmp stéréo I²S.
- Deux haut-parleurs Visaton FR 8, réf. 2008, de 8 Ω.

## Contraintes de conception

- Réserver GPIO18 à GPIO21, GPIO16 et GPIO26 au HiFiBerry MiniAmp (numérotation BCM).
- Utiliser le HiFiBerry MiniAmp comme seul amplificateur.
- Prévoir un PCB d’interconnexion entre le TFT, le Raspberry Pi et le MiniAmp.
- Placer tous les connecteurs des commandes en bord de PCB.
- Conserver une architecture logicielle modulaire et des tests simulés. Isoler les accès au matériel pour exécuter ces tests sur le VPS.
- Qualifier le matériel uniquement par des essais sur le montage réel avec le Raspberry Pi 3. Consigner explicitement quels résultats proviennent de simulations et quels essais ont été réalisés sur le matériel.

## Audio et Multiroom

- Héberger simultanément `snapserver` et `snapclient` sur le Pi 3. Relier le client local à `127.0.0.1` et réserver à ce seul client l’ouverture ALSA du MiniAmp. Relier les deux Visaton FR 8 au MiniAmp.
- Acheminer les radios et fichiers décodés vers `Music`, go-librespot en pipe ou en processus PCM vers `Spotify`, puis la sonnerie locale vers `Alarm`. Vérifier la cadence, la profondeur, l’ordre des octets et les canaux de chaque source. Toute source musicale passe par Snapcast.
- Utiliser l’API JSON-RPC officielle pour découvrir et suivre les clients, gérer groupes et flux, régler volumes et mutes, puis réconcilier l’état après reconnexion. Afficher ces données dans la vue Multiroom du TFT. Affecter l’encodeur au volume du seul client local.
- Maintenir la lecture des fichiers et le réveil local sans Internet. Jouer `Alarm` uniquement après confirmation de l’isolement du client local, puis arrêter le PCM et restaurer le routage de façon contrôlée en préservant les changements indépendants.
- Qualifier le premier client local en S1 et mesurer la synchronisation d’au moins deux clients physiques, dont le client local, en S11. Suivre le [contrat Snapcast](docs/SNAPCAST_ARCHITECTURE.md) et la [procédure](docs/DEPLOYMENT.md).

## Méthode de travail

- Travailler sprint par sprint, sur une branche indépendante pour chacun.
- Pour chaque sprint, produire les tests, la documentation et un compte rendu qui précise les changements, les vérifications effectuées et les points encore ouverts.
- Exécuter les tests ordinaires depuis l’environnement Python local, avec des entrées et sorties simulées.
- Utiliser le [plan S0 à S11](SPRINT_PLAN.md), son [backlog](BACKLOG.md) et les [prompts de sprint](docs/SPRINT_PROMPTS.md) pour cadrer chaque livraison.
- Soumettre la création du dépôt GitHub à l’utilisateur avant toute publication.
