# AGENTS.md — Audio Station

Ces instructions s’appliquent à tout le dossier Audio Station. Elles complètent le `AGENTS.md` global, qui reste applicable.

## Objectif

Développer un lecteur musical stéréo et radio-réveil autonome sur Raspberry Pi 3 en s’appuyant sur les principes logiciels étudiés dans le projet de référence.

## Périmètre de travail

- Consulter le projet de référence uniquement en lecture seule.
- Limiter les modifications à Audio Station. Les services et les autres projets existants sont hors périmètre.
- Réserver le VPS au développement. Le Raspberry Pi 3 est l’équipement final.
- Obtenir l’autorisation explicite de l’utilisateur avant toute installation de service ou modification de la configuration système.

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

## Méthode de travail

- Travailler sprint par sprint, sur une branche indépendante pour chacun.
- Pour chaque sprint, produire les tests, la documentation et un compte rendu qui précise les changements, les vérifications effectuées et les points encore ouverts.
- Exécuter les tests ordinaires depuis l’environnement Python local, avec des entrées et sorties simulées.
- Soumettre la création du dépôt GitHub à l’utilisateur avant toute publication.
