# Prompts de sprint Audio Station

Ce document contient douze prompts lançables, de S0 à S11. Chaque sprint est réalisé sur une branche indépendante nommée `sprint/sN-...`. Le sprint suivant ne reprend les résultats qu’après validation du sprint courant et report de ses livrables dans sa branche propre.

## Préambule commun à appliquer à chaque prompt

Tu travailles uniquement dans le dépôt Audio Station et dans le périmètre explicitement autorisé. Les services dédiés au sprint sont isolés des autres services et projets. N’installe aucun service et ne modifie aucune configuration système sans autorisation explicite préalable. Le VPS sert au développement et aux simulations. Le Raspberry Pi 3 sert à la qualification matérielle. N’ouvre aucun port vers le WAN. Les essais réseau restent limités au LAN de développement ou à un réseau de qualification contrôlé.

Le Raspberry Pi 3 héberge le `snapserver` dédié et le premier `snapclient`, connecté à `127.0.0.1`. Le client possède seul la sortie ALSA du MiniAmp. Les producteurs écrivent du PCM vers `Music`, `Spotify` et `Alarm`. Le contrôle utilise l’API JSON-RPC officielle et le streaming LAN permet l’écoute synchronisée. Suis le [contrat Snapcast](SNAPCAST_ARCHITECTURE.md), le [plan de sprints](SPRINTS.md) et la [procédure de déploiement](DEPLOYMENT.md).

Pour chaque sprint, commence par créer ou utiliser la branche indépendante demandée. Lis les fichiers concernés avant modification. Travaille avec des interfaces simulables sur le VPS et documente clairement les limites de la simulation. Toute commande qui nécessiterait une installation, un service, une règle réseau ou une modification système doit être préparée comme proposition et soumise à autorisation. Termine par les tests appropriés, un compte rendu des changements et des points ouverts.

Vérifie du PCM S16LE stéréo à 48 kHz pour Music et Alarm, et à 44,1 kHz pour Spotify si la capture de la version retenue le confirme. Toute conversion doit être mesurée et documentée. Les critères de sortie distinguent preuve logicielle, simulation VPS et essai sur Raspberry Pi 3.

## S0 — socle v2, audit et simulation

### Objectif

Prépare un socle testable et indépendant autour de Snapcast. Si le répertoire existe déjà, crée une branche propre et conserve le travail validé.

### Action

Audite la référence en lecture seule, y compris les règles, l’architecture, les GPIO, le tactile, le navigateur, l’audio et les tests. Distingue les abstractions utiles, la DEMO et les essais physiques. Vérifie les droits avant toute copie. Prépare les packages sous `src/audio_station`, la configuration, `hardware/kicad` et la CI locale. Décris l’instance Snapcast dédiée, la sortie MiniAmp exclusive et la répartition des preuves entre VPS et Pi.

### Validation

Exécute la DEMO sans réseau ni GPIO et la CI locale. Ajoute un test d’architecture contre les accès ALSA des producteurs Python et un cas valide pour le lancement externe de `snapclient`. Confirme les liens entre le backlog et les jalons S1 et S11.

### Livrables

- Arborescence, CI locale et DEMO
- Spécification v2, architecture et contrats matériel et Snapcast
- Audit de réemploi, backlog, plan de sprints et tests
- Compte rendu S0 avec options, résultats et points ouverts

## S1 — premier client Pi réel et stéréo loopback exclusive

### Objectif

Obtenir le premier chemin audio réel sur Raspberry Pi 3 avec `snapclient` loopback, sortie stéréo et accès exclusif au MiniAmp.

### Action

Préparer le protocole de qualification puis réaliser, après autorisation explicite, le raccordement `snapserver` vers `snapclient` loopback et la sortie ALSA MiniAmp. Vérifier l’absence de second ouvreur ALSA. Utiliser uniquement une source Music déterministe produisant un signal PCM connu, avant toute qualification Spotify ou Alarm.

### Validation

Sur Pi 3, le signal Music déterministe est audible sur les deux canaux distincts. Vérifie la reconnexion du client sur la boucle locale après interruption contrôlée de l’instance dédiée. Relève la version, le PCM en entrée, le format ALSA négocié et le processus qui détient la sortie. Le VPS couvre le scénario simulé. Consigne séparément les preuves du montage réel.

### Livrables

- Configuration et contrat du premier client
- Test PCM stéréo simulé
- Procès-verbal d’essai Pi 3 avec preuve matérielle loopback, version et PCM observés, canaux distincts et accès ALSA exclusif
- Compte rendu S1 et branche indépendante

## S2 — JSON-RPC, états, groupe, volume, mute et reconnexion

### Objectif

Définir et vérifier le contrôle Snapcast par JSON-RPC pour les états, le groupe, le volume, le mute et la reconnexion.

### Action

Implémente un client JSON-RPC isolé et simulable. Pars de `Server.GetStatus`, traite les notifications de présence, de groupes et de flux, puis relis l’état à la reconnexion. Implémente les affectations avec `Group.SetClients` et `Group.SetStream`, le mute via `Group.SetMute`, le volume et mute individuels via `Client.SetVolume`, et le volume de groupe via les membres confirmés. Vérifie chaque réponse, même en lot.

### Validation

Les tests simulés couvrent succès, réponse invalide ou partielle, perte de connexion, reconnexion, groupe disparu, état périmé et réglage individuel et de groupe. Une trace permet de relier chaque commande à son état final.

### Livrables

- Contrat JSON-RPC documenté
- Client et machine d’état testables sur VPS
- Suite de tests d’erreurs et de reconnexion
- Procédure de vérification Pi 3 et compte rendu S2

## S3 — Music, radio, fichiers et décodage PCM

### Objectif

Faire parvenir les sources Music, radio et fichiers au pipeline PCM avec une qualification séparée et des formats prouvés.

### Action

Définir les adaptateurs Music pour radio et fichiers. Détecter ou convertir les flux vers le format candidat Music en PCM 48 kHz, 16 bits, stéréo. Capturer les métadonnées, les erreurs de décodage, les silences et les changements de piste. Garder une source de test déterministe pour les simulations.

### Validation

Chaque adaptateur produit des trames PCM vérifiées par fréquence d’échantillonnage, profondeur et canaux. Les tests couvrent fichier valide, radio interrompue, format inconnu et reprise. La preuve du format final et tout rééchantillonnage sont consignés séparément de la qualification Spotify et Alarm.

### Livrables

- Adaptateurs Music radio et fichiers
- Jeu de tests et données audio autorisées
- Rapport de preuve PCM Music 48 kHz, 16 bits, stéréo
- Compte rendu S3 avec limites de la simulation

## S4 — go-librespot, pipe, processus et PCM

### Objectif

Intégrer Spotify via go-librespot en contrôlant son processus, son pipe PCM et sa séparation avec Music et Alarm.

### Action

Décrire le lancement contrôlé de go-librespot, son cycle de vie, ses sorties standard et son pipe PCM. Prévoir arrêt, redémarrage, fermeture propre, perte réseau et reprise. Vérifier le format candidat Spotify en PCM 44,1 kHz, 16 bits, stéréo selon preuve, puis documenter toute conversion vers le pipeline commun.

### Validation

Les tests VPS utilisent un processus factice et vérifient pipe fermé, données invalides, sortie prématurée, temporisation et nettoyage. Une qualification Spotify autorisée sur Pi 3 établit la preuve du format et de la latence sans partager l’état des sources Music ou Alarm.

### Livrables

- Gestionnaire go-librespot et contrat du pipe
- Processus factice et tests de cycle de vie
- Rapport de preuve Spotify et conversions PCM
- Compte rendu S4 avec prérequis d’accès au compte et au réseau

## S5 — TFT multiroom et encodeur local

### Objectif

Présenter l’état multiroom sur le TFT et piloter les actions locales avec l’encodeur rotatif et son poussoir.

### Action

Définis une vue Multiroom Pillow et Inter indépendante du matériel. Affiche et rends pilotables les groupes, clients, flux, volumes et mutes. Signale connexion, déconnexion et réconciliation. Associe la rotation au seul volume du client local et prépare le protocole TFT pour S7.

### Validation

Les tests simulés à 320 × 240 couvrent rotation rapide, rebond, groupe vide, mute, reconnexion et erreurs. Vérifie que la rotation envoie `Client.SetVolume` au seul ID local configuré, y compris quand le client appartient à un groupe.

### Livrables

- Modèle d’écran multiroom et adaptateur TFT
- Simulateur d’encodeur et tests d’interaction
- Protocole TFT et encodeur pour la qualification sur Pi en S7
- Compte rendu S5

## S6 — réveil et isolement local avec reprise sûre

### Objectif

Ajouter Alarm comme source locale de réveil, isolée des autres sources, avec reprise d’état sûre après interruption.

### Action

Définir l’état Alarm, ses horaires, son arrêt local et ses transitions. Utiliser le format candidat Alarm en PCM 48 kHz, 16 bits, stéréo. Implémenter l’isolement de la source, la priorité documentée, la persistance minimale d’état et la reprise après redémarrage ou perte réseau sans lecture intempestive. Pour chaque essai, isoler explicitement le client local seul. Attendre la confirmation de son état avant toute action et couper Alarm dès qu’une dérive est détectée.

### Validation

Les tests VPS couvrent déclenchement, arrêt, report, état corrompu, redémarrage, perte de confirmation et changement concurrent. La qualification Pi 3 vérifie le réveil local. Coupe immédiatement le PCM si le routage dérive et attends la vidange vérifiée avant restauration. Restaure seulement les champs modifiés par l’alarme qui restent compatibles. Préserve le flux des autres clients et leurs modifications indépendantes. Confirme cette continuité sur deux clients en S11.

### Livrables

- Machine d’état Alarm et format de persistance
- Tests de reprise et d’isolement
- Procédure de qualification locale sur Pi 3
- Compte rendu S6 avec preuves PCM Alarm

## S7 — banc TFT, tactile et commandes GPIO

### Objectif

Qualifier séparément le banc matériel TFT, tactile, encodeur, quatre boutons et commandes GPIO.

### Action

Construire un banc de test réversible avec adaptateurs GPIO simulés sur VPS. Vérifier le TFT tactile, l’encodeur, les boutons précédent, lecture/pause, suivant et veille, la LED de veille et les modules capacitifs dont l’arrêt du réveil. Respecter les GPIO réservés au MiniAmp, de GPIO18 à GPIO21, GPIO16 et GPIO26 en BCM.

### Validation

Chaque entrée est testée au repos, à l’activation, au rebond et en combinaison avec une commande audio simulée. Le test Pi 3 confirme le câblage réel et l’absence de conflit avec le MiniAmp. Les essais matériels sont étiquetés comme tels et ne sont pas déduits des tests VPS.

### Livrables

- Matrice GPIO et protocole de banc
- Adaptateurs simulés et tests d’entrées
- Relevé de qualification TFT, tactile et commandes Pi 3
- Compte rendu S7 avec défauts et corrections proposées

## S8 — PCB

### Objectif

Préparer le PCB d’interconnexion entre Raspberry Pi, TFT, commandes et MiniAmp, avec une implantation vérifiable.

### Action

Produire le schéma, le brochage et le plan d’implantation. Placer tous les connecteurs de commandes en bord de PCB. Vérifier les GPIO réservés, l’alimentation, les masses, les signaux SPI et les contraintes mécaniques. Ne lancer aucune fabrication sans revue et autorisation explicite.

### Validation

Une revue de schéma et de brochage ne laisse aucun conflit avec MiniAmp, TFT ou commandes. Les règles de conception et les dimensions sont vérifiées dans les outils disponibles. Un contrôle visuel et une liste de risques couvrent montage, maintenance et mesure.

### Livrables

- Schéma et brochage révisés
- Implantation PCB et nomenclature
- Rapport de vérification des contraintes
- Compte rendu S8 et décision de fabrication soumise à autorisation

## S9 — autonomie hors Internet et endurance de récupération

### Objectif

Prouver le fonctionnement local hors Internet et la récupération après pannes pendant une endurance contrôlée.

### Action

Définis les ressources locales nécessaires à Music et Alarm, le comportement de Spotify sans Internet, les délais et la reprise. Simule les pertes réseau, les redémarrages de processus, une horloge incertaine après coupure, les déconnexions ALSA et le stockage plein. Exécute ensuite l’endurance autorisée sur Pi 3 et relève les journaux et la température.

### Validation

Music et Alarm restent utilisables selon le périmètre documenté hors Internet. Spotify échoue de façon sûre et reprend après retour du réseau. Aucune récupération ne lance plusieurs clients audio ni ne perd l’état sûr. Les mesures d’endurance, incidents et limites sont horodatés.

### Livrables

- Matrice de pannes et procédures de récupération
- Tests de pannes provoquées simulés sur VPS
- Rapport d’endurance Pi 3 hors Internet
- Compte rendu S9 avec seuils d’acceptation

## S10 — recette multiroom LAN et instrumentation

### Objectif

Préparer la recette multiroom sur LAN avec une instrumentation suffisante pour diagnostiquer synchronisation, audio et contrôle.

### Action

Définis les scénarios de recette, une référence de mesure commune et les seuils d’acceptation avant la recette. Instrumente les horodatages, la latence JSON-RPC, les groupes et clients, les pertes observées, les tampons PCM, les interruptions audio et les reconnexions. Limite le trafic Snapcast à la boucle locale et au LAN de qualification.

### Validation

Chaque métrique possède une unité, une source et un seuil fixé avant la mesure à partir de la référence commune, puis un rapprochement documenté entre les clients. Un scénario de bout en bout est rejouable avec données simulées. La collecte ne révèle aucun secret et ne modifie pas les services hors périmètre. Le protocole indique ce qui doit être mesuré sur Pi 3.

### Livrables

- Plan de recette LAN multiroom
- Instrumentation et format de journaux
- Jeux de scénarios reproductibles
- Compte rendu S10 avec seuils et critères de passage

## S11 — deux clients réels synchronisés et protocole de perte

### Objectif

Valider au moins deux vrais clients Snapcast synchronisés, dont le client local, avec mesure et protocole de perte et de reconnexion.

### Action

Préparer deux Raspberry Pi 3 ou un second client matériel autorisé, en conservant le client local et l’architecture Snapcast officielle. Tester la synchronisation sur le même flux Music de référence, puis éventuellement sur Spotify selon sa preuve. Tester Alarm à part et vérifier qu’elle ne produit aucune sonnerie sur l’autre client. Mesurer synchronisation, dérive, latence, volume, mute, pertes LAN et temps de reconnexion. Injecter des pertes contrôlées et vérifier la reprise sans double ouvreur ALSA ni modification de la lecture en cours.

### Validation

Deux clients réels rendent le même flux Music stéréo avec une synchronisation mesurée et un résultat conforme aux seuils S10. Le client local est explicitement identifié. Spotify peut être ajouté si sa preuve est disponible. Alarm est vérifiée séparément avec zéro sonnerie sur l’autre client et lecture inchangée. Le protocole de perte couvre perte d’un client, perte du serveur, perte réseau et retour, avec état final attendu, journaux et verdict. Toute limite matérielle ou réseau est distinguée de la simulation VPS.

### Livrables

- Procédure de recette à deux clients
- Mesures de synchronisation, dérive, latence et reconnexion
- Rapport de perte et récupération avec preuves Pi 3
- Compte rendu S11, verdict de passage et liste de travaux restants
