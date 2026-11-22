# Prototype réversible du banc audio S1

Ce guide concerne uniquement le Pi 3 de test confirmé et le montage [MiniAmp et Visaton](../../docs/AUDIO_HAT_QUALIFICATION.md). Attendre l’autorisation de l’utilisateur avant de copier les fichiers sur le Pi, d’installer des paquets, d’éditer la configuration ou de redémarrer. Réserver le banc à Audio Station. Si une ressource appartient à un autre projet ou si la carte audio est occupée, interrompre l’essai.

## Inventaire et restauration de Linux

Depuis la racine du projet sur le Pi autorisé, relever l’état avec `tools/audio_preflight.sh`. Vérifier la version du Pi, l’overlay actif, le système, le noyau, les binaires et les propriétaires des périphériques. L’inventaire est en lecture seule. Conserver ses résultats localement.

Utiliser de préférence une carte de démarrage dédiée au banc. Si l’overlay est déjà actif et la carte ALSA présente, conserver le fichier de démarrage. Si une modification a été autorisée, relever le fichier réellement lu par le firmware et ses éventuels fichiers inclus. Raspberry Pi OS actuel utilise `/boot/firmware/config.txt`. Un chemin ancien visible dans l’inventaire ne suffit pas à déterminer le fichier actif. [Documentation Raspberry Pi](https://www.raspberrypi.com/documentation/computers/config_txt.html)

Exemple de sauvegarde si le fichier actif confirmé est `/boot/firmware/config.txt`. Adapter le chemin si l’inventaire indique un autre fichier.

```sh
BOOT_CONFIG=/boot/firmware/config.txt
umask 077
mkdir -p .demo
S1_RESTORE_DIR=$(mktemp -d "$PWD/.demo/s1-restore.XXXXXXXX")
cp -p -- "$BOOT_CONFIG" "$S1_RESTORE_DIR/config.txt.original"
(cd "$S1_RESTORE_DIR" && sha256sum config.txt.original > SHA256SUMS)
printf 'Sauvegarde S1 à conserver hors de la partition de démarrage — %s\n' "$S1_RESTORE_DIR"
```

Après sauvegarde vérifiée, utiliser le [fragment MiniAmp](miniamp-config.fragment) pour ajouter `dtoverlay=hifiberry-dac` une seule fois dans une section active sur le Pi. Examiner les sections conditionnelles, inclusions et overlays I²S existants. Conserver les réglages indépendants. Ne pas modifier `/etc/asound.conf` ni le périphérique ALSA par défaut. Faire relire le diff et redémarrer uniquement dans le cadre approuvé. [Fiche HiFiBerry MiniAmp](https://www.hifiberry.com/docs/data-sheets/datasheet-miniamp/)

Pour revenir en arrière, arrêter d’abord les trois processus du banc depuis leurs terminaux. Vérifier l’empreinte de la sauvegarde. Si une modification tiers est intervenue, examiner le diff et préserver ce changement. Dans le cas simple où seul le changement S1 est présent, effectuer la restauration autorisée avec les variables conservées.

```sh
(cd "$S1_RESTORE_DIR" && sha256sum -c SHA256SUMS) &&
sudo cp -- "$S1_RESTORE_DIR/config.txt.original" "$BOOT_CONFIG" &&
cmp -- "$S1_RESTORE_DIR/config.txt.original" "$BOOT_CONFIG"
```

Après un redémarrage autorisé, recueillir la sortie de prévol et la comparer à l’état initial. Si le Pi ne démarre plus, restaurer le fichier sauvegardé depuis la carte de démarrage montée hors ligne ou remettre l’image de banc initiale. Les configurations et traces de restauration restent hors de Git.

## Générer les signaux et isoler la sortie

Créer le répertoire temporaire du banc sur le Pi confirmé. L’exemple choisit la syntaxe moderne. Si la version est 0.26.0 et utilise `[tcp]` et `[stream]` pour les écoutes, choisir `config/s1/snapserver-v0.26.conf.in`. Pour toute autre version, vérifier les options et le fichier amont correspondant avant de réutiliser un profil. Effectuer le premier démarrage sur un banc isolé et confirmer les écoutes avant de rétablir un lien vers un réseau partagé. [Configuration Snapcast actuelle](https://github.com/snapcast/snapcast/blob/develop/server/etc/snapserver.conf), [Configuration Snapcast 0.26.0](https://github.com/snapcast/snapcast/blob/v0.26.0/server/etc/snapserver.conf)

```sh
umask 077
S1_RUN=$(mktemp -d /tmp/audio-station-s1.XXXXXXXX)
mkdir "$S1_RUN/state"
mkfifo -m 600 "$S1_RUN/music.fifo"
S1_TEMPLATE=config/s1/snapserver.conf.in
sed "s|@RUN_DIR@|$S1_RUN|g" "$S1_TEMPLATE" > "$S1_RUN/snapserver.conf"
for mode in left right stereo silence; do
  python3 tools/audio_hat_pcm.py "$mode" --level-dbfs -42 --format raw > "$S1_RUN/$mode.raw"
  python3 tools/audio_hat_pcm.py "$mode" --level-dbfs -42 --format wav > "$S1_RUN/$mode.wav"
done
printf 'Répertoire du banc à réutiliser dans chaque terminal — %s\n' "$S1_RUN"
```

Le signal de deux secondes contient 96 000 trames de quatre octets. Le canal gauche est à 440 Hz, le droit à 660 Hz. Le mode inactif est à zéro numérique. Le niveau `−42 dBFS` est le niveau du signal numérique, indépendamment du volume logiciel et de la puissance réelle.

Relever `aplay -l` et `/proc/asound/cards` pour identifier la carte MiniAmp et le périphérique de lecture. Renseigner `S1_PCM` par le nom stable `hw:CARD=…,DEV=…`, et `S1_PCM_NODE` par le nœud de lecture `/dev/snd/pcmC…D…p` observé correspondant. Le numéro de carte sert seulement à identifier le nœud du noyau. Vérifier les propriétaires avec `fuser -v "$S1_PCM_NODE"` et le fichier `hw_params` associé dans `/proc/asound`. Si la visibilité est insuffisante ou qu’un processus occupe la sortie, suspendre le test.

## A. Diagnostic ALSA ponctuel

Après le contrôle du câblage hors tension et la remise sous tension autorisée, vérifier que le banc Snapcast est arrêté. Exécuter indépendamment les trois essais, à commencer par le bloc gauche au niveau initial. Si le premier bloc est trop fort ou produit un bruit anormal, interrompre l’essai.

```sh
aplay -D "${S1_PCM:?Nom ALSA stable requis}" "${S1_RUN:?Répertoire S1 requis}/left.wav"
aplay -D "${S1_PCM:?Nom ALSA stable requis}" "${S1_RUN:?Répertoire S1 requis}/right.wav"
aplay -D "${S1_PCM:?Nom ALSA stable requis}" "${S1_RUN:?Répertoire S1 requis}/stereo.wav"
```

Laisser chaque appel se terminer. Vérifier que la sortie est libérée avant l’étape B. Le test A confirme la route HAT seulement. Le banc Snapcast reste obligatoire.

## B. Banc Snapcast de boucle locale

Dans le terminal du serveur dédié, vérifier que les ports 17104 et 17105 sont libres et démarrer au premier plan. Observer les écoutes depuis un autre terminal. Autoriser la poursuite uniquement si les deux ports sont liés à `127.0.0.1` et si HTTP est désactivé. Le profil moderne désactive mDNS. Si le profil ancien ne le permet pas, maintenir le banc hors du réseau partagé. [Configuration Snapserver](https://github.com/snapcast/snapcast/blob/develop/server/etc/snapserver.conf)

```sh
ss -ltnp '( sport = :17104 or sport = :17105 )'
snapserver -c "$S1_RUN/snapserver.conf"
```

Dans le terminal du client, après vérification de la disponibilité du nœud ALSA, lancer le seul `snapclient` local. Vérifier `--help` sur la version retenue. Pour l’ancienne syntaxe, remplacer l’URI finale par `--host 127.0.0.1 --port 17104`. Le niveau du profil peut dépendre de la version et de l’état du serveur. Maintenir la FIFO sans son jusqu’à confirmation du volume bas par JSON-RPC. [Options Snapclient](https://github.com/snapcast/snapcast/blob/develop/client/snapclient.cpp#L147), [Options Snapclient 0.26.0](https://github.com/snapcast/snapcast/blob/v0.26.0/client/snapclient.cpp)

```sh
snapclient --player alsa --mixer software --soundcard "${S1_PCM:?Nom ALSA stable requis}" \
  --hostID audio-station-s1 tcp://127.0.0.1:17104
```

L’outil JSON-RPC est limité à `127.0.0.1:17105`. `status` vérifie l’unique client connecté sur `Music` et indique l’identifiant exact à reprendre dans `S1_CLIENT_ID`. Le réglage exige cet identifiant, conserve les champs omis et confirme la valeur par relecture. Lancer le producteur seulement après l’état initial à faible volume. En cas d’incertitude, vérifier le câblage, les écoutes et l’état du client avant de continuer. [API officielle Snapcast](https://github.com/snapcast/snapcast/blob/develop/doc/json_rpc_api/control.md)

```sh
python3 tools/audio_hat_rpc.py status
# Renseigner S1_CLIENT_ID avec le client exact relevé et confirmé.
python3 tools/audio_hat_rpc.py volume --client-id "$S1_CLIENT_ID" --percent 5 --mute on
```

Dans un troisième terminal, garder la FIFO ouverte pendant le cycle de test. Le silence entre les blocs sert à contrôler la séparation et les coupures. Arrêter le producteur par Ctrl-C et attendre la fin des données audio déjà en tampon.

```sh
while cat "$S1_RUN/silence.raw" "$S1_RUN/left.raw" "$S1_RUN/silence.raw" \
          "$S1_RUN/right.raw" "$S1_RUN/silence.raw" "$S1_RUN/stereo.raw"; do
  :
done > "$S1_RUN/music.fifo"
```

Depuis le terminal de contrôle, enlever le mute à 5 %, puis augmenter progressivement par petits paliers. À chaque palier, relever le niveau, l’écoute des deux voies, les défauts et les journaux. Vérifier ensuite le mute en cours de lecture et sa libération. Le contrôle logiciel de Snapclient garde le MiniAmp en chemin ALSA direct, sans réglage global.

```sh
python3 tools/audio_hat_rpc.py volume --client-id "$S1_CLIENT_ID" --mute off
python3 tools/audio_hat_rpc.py volume --client-id "$S1_CLIENT_ID" --percent 10
python3 tools/audio_hat_rpc.py volume --client-id "$S1_CLIENT_ID" --mute on
python3 tools/audio_hat_rpc.py volume --client-id "$S1_CLIENT_ID" --mute off
```

## Reconnexion, mesure et fermeture

- Sur `Music`, confirmer le détenteur unique du nœud de lecture et le format matériel avec `fuser -v` et `hw_params`. Relever versions, PID dédiés, CPU et RSS en KiB avec `ps -p "$S1_SERVER_PID,$S1_CLIENT_PID" -o pid=,comm=,pcpu=,rss=`. Le CPU de `ps` est une moyenne sur la vie du processus. Si `pidstat` est déjà disponible, relever aussi une série CPU/RSS pendant la lecture et indiquer la fenêtre de mesure.
- Distinguer le tampon configuré, l’aller-retour JSON-RPC et la latence audio. Pour mesurer cette dernière, horodater le début d’un bloc PCM injecté et sa détection sur une capture acoustique horodatée dans la même base de temps. Mentionner l’instrument et l’incertitude. À défaut de capture comparée, l’entrée latence audio reste **NON TESTÉ**.
- Arrêter le producteur et interrompre le serveur dédié. Laisser le client tourner pour observer la perte et la reconnexion. Redémarrer le serveur avec la même configuration, relire l’état et vérifier un niveau bas avant de reprendre le PCM. Mesurer le délai jusqu’au retour du son. Tester séparément un redémarrage du client, puis un redémarrage du Pi autorisé avec relance manuelle du banc. Après redémarrage du Pi, revalider l’identifiant ALSA et retrouver son nœud actuel avec `aplay -l` et `/proc/asound/cards`.
- Lancer une période d’écoute continue de durée consignée au volume choisi. Distinguer les silences prévus du signal, les coupures provoquées et toute coupure parasite. Relever l’absence ou la présence d’écrêtage sur une mesure adaptée et les observations d’écoute. Interrompre si distorsion, réinitialisation, échauffement ou bruit inexpliqué.
- Couper le PCM, puis arrêter le client et le serveur depuis leurs terminaux. Les fichiers d’état et journaux du banc se trouvent dans le répertoire temporaire. Conserver localement les seules traces nécessaires. Restaurer la configuration de démarrage si elle a été modifiée pour l’essai et contrôler le retour à l’état attendu.
