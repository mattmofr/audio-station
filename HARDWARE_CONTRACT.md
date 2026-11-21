# Contrat matériel S0

Ce document fixe le périmètre matériel du sprint S0 pour un lecteur musical stéréo et radio-réveil autonome autour d’un Raspberry Pi 3. Il sert de référence avant le schéma et le routage du PCB. Les résultats d’essais sur matériel réel sont encore inexistants à la date de rédaction.

## Contraintes fixes

- Le calculateur est un Raspberry Pi 3.
- L’affichage est un TFT ILI9341 SPI de 3,2 pouces, 320 × 240, utilisé en paysage.
- Le TFT comporte un contrôleur tactile intégré, dont la référence et l’interface restent à identifier.
- L’interface locale comprend un encodeur rotatif avec poussoir.
- Elle comprend quatre boutons momentanés pour précédent, lecture/pause, suivant et veille.
- Le bouton de veille intègre une LED.
- Des modules capacitifs sont présents. L’un d’eux est affecté à l’arrêt du réveil.
- Le HiFiBerry MiniAmp est le seul amplificateur. Aucun autre étage d’amplification ne doit être ajouté.
- Les haut-parleurs sont deux Visaton FR 8, référence 2008, un par canal, chacun de 8 Ω.
- En numérotation BCM, GPIO 18, GPIO 19, GPIO 20, GPIO 21, GPIO 16 et GPIO 26 sont réservés au MiniAmp et ne peuvent recevoir aucune commande utilisateur.
- Le PCB d’interconnexion se place entre l’écran, le Raspberry Pi et le MiniAmp. Tous les connecteurs des commandes sont placés en bord de PCB.
- Les validations logicielles des GPIO de commande traitent GPIO 7, GPIO 8, GPIO 9, GPIO 10 et GPIO 11 comme réservés à la route SPI candidate. Aucun de ces GPIO ne doit être attribué à une commande utilisateur.
- SPI1 est exclu de la conception S0 en raison du conflit identifié dans le périmètre du projet.
- Le VPS sert au développement et aux tests simulés. La qualification électrique et fonctionnelle se fait uniquement sur le montage réel avec le Raspberry Pi 3.

## Route SPI candidate

La route à étudier est SPI0 sur GPIO 7 à GPIO 11. CE0 est réservé à l’écran. CE1 est réservé au tactile uniquement si l’identification du contrôleur confirme une interface SPI compatible et un câblage distinct. Cette route reste candidate jusqu’à vérification du brochage réel du module TFT et de son contrôleur tactile.

| Signal | GPIO BCM | Broche physique |
| --- | --- | --- |
| SPI0 MOSI | 10 | 19 |
| SPI0 MISO | 9 | 21 |
| SPI0 SCLK | 11 | 23 |
| SPI0 CE0 | 8 | 24 |
| SPI0 CE1 | 7 | 26 |

Ce tableau décrit l’en-tête 40 broches du Pi. La broche physique 26 du SPI0 CE1 correspond au GPIO7, tandis que le GPIO26 réservé au MiniAmp est sur la broche physique 37. [Raspberry Pi, documentation matérielle](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html)

Les affectations individuelles de l’encodeur, de son poussoir, des quatre boutons, de la LED de veille et des modules capacitifs restent à établir. La validation logicielle de S0 contrôle les collisions sur l’en-tête, dont l’exclusion de BCM0/1 réservés à l’identification des cartes. Le schéma devra aussi vérifier les fonctions alternatives effectivement activées sur le Pi. [HiFiBerry, utilisation des GPIO](https://dev.hifiberry.com/docs/hardware/gpio-usage-of-hifiberry-boards/)

## Faits constructeur à retenir

La documentation HiFiBerry décrit le MiniAmp comme un DAC et amplificateur stéréo jusqu’à 2 × 3 W, alimenté directement par le Raspberry Pi et sans réglage de volume intégré. Elle indique que GPIO 18 à GPIO 21 servent à l’interface audio, que GPIO 16 peut commander le mute de l’étage de puissance et que GPIO 26 arrête cet étage. [HiFiBerry MiniAmp, fiche technique](https://www.hifiberry.com/docs/data-sheets/datasheet-miniamp/), [HiFiBerry, utilisation des GPIO](https://dev.hifiberry.com/docs/hardware/gpio-usage-of-hifiberry-boards/)

Le Raspberry Pi documente des GPIO en logique 3,3 V et précise qu’ils ne sont pas tolérants au 5 V. Une entrée externe devra donc être démontrée compatible 3,3 V ou adaptée électriquement avant raccordement. La LED et les modules requièrent un budget de courant propre. [Raspberry Pi, documentation matérielle](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html)

Le Visaton FR 8, article 2008, est spécifié à 8 Ω, 10 W de puissance nominale et 15 W de puissance maximale. Le câblage du MiniAmp doit conserver la séparation des deux canaux et respecter la polarité des deux haut-parleurs. [Visaton FR 8, 8 Ω, article 2008](https://www.visaton.de/en/products/drivers/fullrange-systems/fr-8-8-ohm)

## Identifications électriques exigées avant le schéma

Les points suivants doivent être relevés sur les pièces effectivement disponibles et consignés avec une photo ou une référence lisible.

- Le brochage complet du TFT, les tensions d’alimentation, les niveaux logiques, la présence de résistances de tirage et le courant du rétroéclairage.
- La référence du contrôleur tactile intégré, son interface réelle, son adresse ou sa sélection de puce si applicable, et ses tensions d’entrée et de sortie.
- La correspondance entre les broches signalées par le vendeur et les signaux SPI0, notamment SCLK, MOSI, MISO, CE0, CE1, réinitialisation, commande et données.
- La nécessité éventuelle d’un convertisseur de niveau. Aucun signal 5 V ne doit parvenir directement à un GPIO du Raspberry Pi.
- Le brochage de l’encodeur, le type de contact du poussoir et le comportement électrique des boutons momentanés.
- La tension, le courant et la polarité de la LED de veille. Son raccordement ne sera arrêté qu’après calcul de la résistance et du courant autorisé.
- Pour chaque module capacitif, la tension d’alimentation, le niveau de sortie au repos et à l’activation, le type de sortie et la possibilité d’un état flottant.
- Les masses communes, les rails d’alimentation disponibles et le budget de courant du Raspberry Pi, du TFT, du rétroéclairage et des modules de commande.
- Le connecteur et le sens de câblage du MiniAmp, ainsi que les bornes de chaque FR 8, avant tout branchement de puissance.
- Les contraintes mécaniques du PCB, l’orientation paysage du TFT et l’accès en bord aux connecteurs de commande.

Une proposition de schéma qui dépend d’une de ces informations reste en attente jusqu’à obtention de la mesure ou de la fiche correspondant exactement au matériel monté.

## Plan d’essais sur le montage réel

Ce plan décrit les essais à effectuer. Aucun essai ci-dessous n’est déclaré réalisé.

1. Hors tension, comparer le brochage relevé avec le schéma prévu, contrôler les continuités de masse et vérifier l’absence de court-circuit entre rails.
2. Sous alimentation limitée, mesurer les tensions du Raspberry Pi, du TFT, du rétroéclairage et des modules capacitifs, puis relever les courants au repos et en activité.
3. Vérifier au multimètre et à l’oscilloscope les niveaux logiques du TFT, du tactile et des commandes avant connexion durable aux GPIO.
4. Tester SPI0 avec l’écran seul, puis caractériser le tactile après identification de son contrôleur. Vérifier que CE1 n’est utilisé que si le contrôleur le justifie.
5. Vérifier l’absence d’attribution logicielle de GPIO 7 à GPIO 11 et de GPIO 18 à GPIO 21, GPIO 16 et GPIO 26 aux commandes.
6. Tester l’encodeur, le poussoir, chaque bouton, la LED de veille et chaque module capacitif avec anti-rebond et états de repos documentés.
7. Tester le MiniAmp avec les deux FR 8 raccordés séparément, commencer à faible niveau et vérifier l’absence de bruit, d’échauffement anormal ou de coupure.
8. Vérifier le comportement d’arrêt du réveil et le comportement de veille dans les scénarios d’alimentation prévus.
9. Consigner pour chaque essai le matériel utilisé, les mesures, la date, le résultat et les écarts au présent contrat. Une simulation ou un test sur le VPS ne constitue pas un essai matériel réel.

## Autorisation d’exploitation

Aucune installation de service, activation de daemon, modification de configuration système, ajout d’overlay ou changement de démarrage ne fait partie de ce contrat. Toute action de ce type sur le Raspberry Pi ou sur un autre système nécessite une autorisation explicite préalable de l’utilisateur, après présentation de la modification et de son effet attendu.
