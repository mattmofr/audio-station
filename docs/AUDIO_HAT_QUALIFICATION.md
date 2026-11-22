# Qualification audio S1 du HiFiBerry MiniAmp

Le banc S1 qualifie le chemin audio local sur Raspberry Pi 3, du PCM aux deux Visaton FR 8 réf. 2008. Le 22 novembre 2026, la préparation et les simulations ont été réalisées sur le VPS. Le Pi cible reste à confirmer. La décision est **NO-GO provisoire pour figer le PCB**, faute de mesures sur l’assemblage.

## Périmètre et faits vérifiés

Le MiniAmp est le seul amplificateur du montage. HiFiBerry annonce un DAC stéréo et une puissance de 2 × 3 W. La carte est alimentée directement par le Raspberry Pi et ne possède pas de réglage de volume intégré. Le volume doit donc être fourni par ALSA Softvol ou par l’application. L’annonce de 2 × 3 W ne constitue pas une puissance garantie dans toutes les conditions avec une charge de 8 Ω. [Source HiFiBerry MiniAmp](https://www.hifiberry.com/docs/data-sheets/datasheet-miniamp/)

La fiche MiniAmp indique `dtoverlay=hifiberry-dac`. Un changement du fichier de démarrage ne prend effet qu’après redémarrage. Le banc enregistre la configuration d’origine et la somme SHA-256 si l’application de cet overlay est autorisée. [Fiche MiniAmp](https://www.hifiberry.com/docs/data-sheets/datasheet-miniamp/) · [Documentation Raspberry Pi](https://www.raspberrypi.com/documentation/computers/config_txt.html)

Le Raspberry Pi fournit des GPIO en logique 3,3 V. Ses GPIO ne sont pas tolérants au 5 V. Pour le MiniAmp, GPIO 18 à GPIO 21 portent l’interface audio, GPIO 16 peut commander le mute de l’étage de puissance et GPIO 26 arrête cet étage. Ces lignes BCM restent réservées et ne reçoivent aucune commande du banc. [Sources Raspberry Pi](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html) et [HiFiBerry GPIO](https://dev.hifiberry.com/docs/hardware/gpio-usage-of-hifiberry-boards/)

Chaque Visaton FR 8 est un haut-parleur nominalement 8 Ω, référence 2008, donné pour 10 W nominaux et 15 W maximum. Un haut-parleur est raccordé directement à un canal du bornier réel du MiniAmp. [Source Visaton FR 8](https://www.visaton.de/en/products/drivers/fullrange-systems/fr-8-8-ohm)

## Règles de sécurité du banc

Toutes les opérations de câblage, déplacement de sonde et inspection du bornier se font hors tension. L’alimentation est coupée et débranchée avant de connecter ou déconnecter le MiniAmp, un haut-parleur ou une sonde.

Le bornier exact doit être identifié sur la carte exacte à qualifier, avec sa sérigraphie, sa photo et la documentation correspondante. Les repères fonctionnels utilisés pour le protocole sont uniquement `L+`, `L-`, `R+` et `R-`. Ils ne préjugent pas de l’ordre physique des bornes ni de leur position sur une révision donnée.

Raccorder un seul FR 8 par canal, directement à la paire correspondante du bornier réel. Garder les quatre bornes HP isolées de la masse, de la terre et du blindage. Les deux paires restent indépendantes, sans négatif commun. Traiter les sorties haut-parleur comme différentielles.

Les mesures électriques sur les sorties haut-parleur sont différentielles entre `L+` et `L-`, ou entre `R+` et `R-`, avec un instrument et une sonde adaptés à une sortie en pont. Aucune sonde référencée à la terre, aucune pince de masse reliée à une sortie haut-parleur et aucun oscilloscope de table non isolé ne sont autorisés sur ces bornes. La tension de sortie, le courant, la puissance et la saturation ne sont mesurés qu’avec une charge et une méthode compatibles avec une sortie différentielle.

Le haut-parleur ne doit pas être remplacé par une résistance improvisée pendant l’écoute. Si une charge de laboratoire est nécessaire pour un essai électrique, elle doit être explicitement évaluée pour l’impédance, la puissance dissipable et le mode différentiel avant branchement.

## Préparation avant mise sous tension

1. Photographier la face et le bornier du MiniAmp exact, relever la révision visible et recopier les repères de la carte.
2. Relever la référence de chaque FR 8 et mesurer sa résistance continue, haut-parleur débranché. Les 8 Ω désignent l’impédance nominale. La fiche donne 7,4 Ω de résistance continue, à consigner séparément de toute mesure d’impédance. [Fiche Visaton](https://www.visaton.de/sites/default/files/dd_product/fr8_8.pdf)
3. Vérifier la continuité des conducteurs et l’absence de contact entre les voies ou vers la masse, le blindage et la terre avant le branchement. Raccorder chaque haut-parleur aux deux bornes de son canal repérées sur la carte.
4. Vérifier la polarité des languettes du FR 8 d’après sa fiche et son marquage. La documentation Visaton donne une connexion positive de 4,8 × 0,8 mm et négative de 2,8 × 0,8 mm, mais le repérage du bornier MiniAmp vient de la carte exacte.
5. Vérifier l’orientation du HAT sur le connecteur 40 broches et l’absence de contact décalé. Aucun adaptateur de broches non documenté ne doit être utilisé.
6. Utiliser le fichier de test à faible niveau pour le diagnostic ALSA. Confirmer le faible volume logiciel du client et son mute initial avant d’alimenter le flux Snapcast.

## Ordre de qualification

### Diagnostic ALSA ponctuel

Le diagnostic ALSA direct utilise un signal numérique faible en session dédiée, avant de démarrer `snapclient`. Vérifier que le périphérique est libre et suspendre l’opération si un autre projet l’occupe. L’essai vérifie séparément le canal gauche, le canal droit, puis la stéréo. Consigner le périphérique, le format négocié, la fréquence, la profondeur, le nombre de canaux, le niveau du fichier et l’écoute. Vérifier la libération de la carte avant la phase Snapcast.

Ce diagnostic ne donne pas le verdict final S1. Il sert uniquement à distinguer un défaut de câblage ou de carte d’un défaut du routage Snapcast.

### Chemin obligatoire Snapcast en boucle locale

La qualification de sortie S1 passe obligatoirement par le chemin Snapcast local. Le client local se connecte à `127.0.0.1` et reste le seul détenteur ALSA du MiniAmp. Le signal PCM de test entre dans le flux local, puis le client ouvre la carte audio.

Le volume logiciel de Snapclient part d’un niveau faible. Il augmente par petits paliers jusqu’au niveau d’écoute retenu, puis le banc vérifie le mute et la reprise sonore. Confirmer les valeurs par JSON-RPC et leur effet sur le client identifié. La carte ALSA reste détenue par ce seul client.

La procédure et les commandes exactes sont fournies par la branche S1 dans [le pré-contrôle audio](../tools/audio_preflight.sh) et [la procédure de configuration S1](../config/s1/README.md). Cette fiche ne duplique ni commandes, ni sauvegarde, ni rollback.

## Matrice de preuve

| Élément | Statut | Résultat ou preuve attendue |
| --- | --- | --- |
| Prévol en lecture seule | SIMULÉ | Fixture locale pour les observations système et ALSA |
| Générateur PCM | SIMULÉ | 48 kHz, 16 bits signés little-endian, stéréo. Séparation et amplitude vérifiées sur les échantillons numériques. |
| Contrôle Snapcast | SIMULÉ | Réponses JSON-RPC injectées, seul client local sur `Music` accepté |
| Pi 3, MiniAmp et bornier | NON TESTÉ | Modèle, révision, photo et repères exacts |
| Deux FR 8 nominalement 8 Ω et câblage isolé | NON TESTÉ | Référence, résistances continues, polarité et contrôle de liaison hors tension |
| Détection ALSA et paramètres négociés | NON TESTÉ | Identifiant stable, `hw_params`, détenteur du nœud de lecture |
| Diagnostic ALSA ponctuel | NON TESTÉ | Gauche seul, droit seul, stéréo au niveau bas, libération du nœud |
| Gauche, droite et stéréo via Snapcast | NON TESTÉ | Écoute des voies, connexion locale, absence de second ouvreur ALSA |
| Volume et mute via Snapcast | NON TESTÉ | Valeurs confirmées et effet à la sortie |
| Saturation à niveaux progressifs | NON TESTÉ | Niveau d’écoute retenu et preuve adaptée sans liaison à la masse |
| Reconnexion et redémarrages | NON TESTÉ | Reprise après interruption du serveur, relance du client et redémarrage du Pi |
| Continuité d’écoute | NON TESTÉ | Durée, coupures parasites, bruits et incidents d’alimentation éventuels |
| CPU, RAM, latence et versions | NON TESTÉ | Relevés sur le chemin réel avec méthode de mesure |
| Restauration | NON TESTÉ | Sauvegarde locale, empreinte et vérification du retour à l’état initial |

Attribuer le statut **MESURÉ SUR PI** à chaque résultat physique consigné avec la date, le matériel, les versions, le niveau, la méthode et un relevé expurgé. Le verdict reste **NO-GO provisoire** jusqu’à obtention des preuves matérielles requises.

Sur le VPS, `tools/ci.sh` a passé `pip check` et les 36 tests. Les deux gabarits Snapserver, leurs URI de source et la syntaxe des commandes shell ont été contrôlés localement. Ces vérifications établissent la préparation du banc et des outils.

## Critères de passage GO

Le verdict devient **GO conditionnel S1** seulement lorsque les critères suivants sont mesurés sur le Raspberry Pi 3 avec les deux FR 8 raccordés au bornier exact.

- ALSA négocie un format connu et documenté sur le client local Snapcast.
- Un signal gauche seul est audible et mesuré sur le FR 8 du canal gauche, sans signal fonctionnel attendu sur le canal droit.
- Un signal droit seul est audible et mesuré sur le FR 8 du canal droit, sans signal fonctionnel attendu sur le canal gauche.
- La stéréo conserve la séparation et la polarité vérifiées.
- La montée de niveau ne produit pas de saturation avant le niveau d’écoute retenu. Aucune puissance de 3 W sous 8 Ω n’est déduite sans mesure dans les conditions du banc.
- Le volume logiciel du client Snapcast et le mute agissent sur la sortie locale sans ouvrir un autre chemin ALSA.
- Après un redémarrage autorisé du Pi et la relance du banc, le client retrouve la boucle locale et la lecture reprend. Les interruptions contrôlées restent distinctes des coupures parasites observées pendant la lecture continue.
- La charge CPU, la mémoire et la latence sont relevées pendant l’écoute et restent compatibles avec le fonctionnement S1.
- Les versions du noyau, d’ALSA et des composants audio sont consignées avec le résultat.
- Aucun défaut de câblage, de masse, d’échauffement ou de protection n’est observé.

Un défaut de bornier, une sortie référencée à la masse, une ouverture ALSA concurrente, une perte de canal, une saturation inexpliquée ou une reconnexion non maîtrisée maintient le verdict **NO-GO** et bloque l’intégration.

## Autorisation et limites

Confirmer le Pi de test avant intervention et obtenir un accord explicite pour l’installation, la configuration ou le redémarrage. La configuration dédiée et la sauvegarde de restauration sont décrites dans le [prototype S1](../config/s1/README.md).
