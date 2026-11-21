# Déploiement Snapcast sur Raspberry Pi 3

Cette procédure prépare les essais et la mise en service d’une instance dédiée à Audio Station. L’installation de paquets, la création ou l’activation d’unités, les changements de démarrage et les règles réseau exigent l’autorisation explicite de l’utilisateur. Les commandes ci-dessous sont des gabarits à adapter au banc et à la version retenue.

## Inventorier le Pi et préparer le retour arrière

1. Relever l’image du Pi, son architecture, les versions de Snapcast disponibles, le MiniAmp effectivement monté et le câblage des deux Visaton. Vérifier le périphérique PCM avec `aplay -l` et `snapclient --list` quand les binaires sont présents.
2. Relever les services et sockets existants avec `systemctl list-units` et `ss -ltnp`. Réserver des unités, des fichiers de configuration et des répertoires de données propres à Audio Station. Arrêter la préparation en cas de collision avec un autre projet.
3. Comparer la configuration au manuel et à l’aide des binaires retenus. En particulier, `snapclient --help` donne la syntaxe de connexion et les sorties disponibles, qui varient selon la version et la compilation. Vérifier les effets d’une installation de paquets sur le démarrage automatique et les interfaces avant de la soumettre à autorisation. [Documentation Snapcast](https://github.com/snapcast/snapcast/blob/develop/README.md), [Options du client Snapcast](https://github.com/snapcast/snapcast/blob/develop/client/snapclient.cpp#L147)
4. Avant un changement autorisé, conserver un instantané daté des fichiers, unités, état et règles propres à Audio Station. Pour revenir en arrière, arrêter ses seules instances, restaurer cet instantané et contrôler leur état et leurs écoutes. Conserver le diagnostic et chaque sauvegarde.

## Préparer la configuration dédiée

Le profil S1 écoute exclusivement sur la boucle locale. Le gabarit ci-dessous repose sur la syntaxe de l’amont actuel. Vérifier chaque section, option et port sur la version cible. Créer après autorisation le répertoire d’état et les FIFO avec des droits limités aux instances dédiées. Le mode `read` suppose des FIFO déjà créées. Pour le banc minimal S1, garder uniquement la source `Music` active. Ajouter `Spotify` en S4 et `Alarm` en S6. [Exemple de configuration Snapserver](https://github.com/snapcast/snapcast/blob/develop/server/etc/snapserver.conf), [Sources Snapcast](https://github.com/snapcast/snapcast/blob/develop/doc/configuration.md#sources)

```ini
[server]
datadir = /var/lib/audio-station/snapserver
mdns_enabled = false

[http]
enabled = false
ssl_enabled = false

[tcp-control]
enabled = true
bind_to_address = 127.0.0.1
port = 1705

[tcp-streaming]
enabled = true
bind_to_address = 127.0.0.1
port = 1704

[stream]
source = pipe:///run/audio-station/music.fifo?name=Music&mode=read&sampleformat=48000:16:2
source = pipe:///run/audio-station/spotify.fifo?name=Spotify&mode=read&sampleformat=44100:16:2
source = pipe:///run/audio-station/alarm.fifo?name=Alarm&mode=read&sampleformat=48000:16:2
default_source = Music
```

Conserver `Music` en première source, y compris sur une version qui ne prend pas en charge `default_source`. Après chaque ajout, vérifier la présence et le format de toutes les entrées attendues dans `Server.GetStatus`. Les trois formats sont du PCM brut S16LE entrelacé. Vérifier les octets produits et la durée de lecture avec un signal stéréo de référence. Le format d’entrée Snapserver et le format négocié par ALSA sont deux mesures distinctes. [Configuration des sources Snapcast](https://github.com/snapcast/snapcast/blob/develop/doc/configuration.md#sources)

Configurer go-librespot séparément en S4. Le fichier de configuration local et ses données d’authentification sont accessibles uniquement à leur compte de service. Le lecteur amont utilise 44 100 Hz et deux canaux. Vérifier la cadence et l’encodage effectivement émis par la version retenue. Confirmer la présence de `audio_output_pipe_wait_for_reader` dans son schéma et tester le démarrage sans lecteur FIFO. Une variante `process` reste possible si le processus auxiliaire fournit du PCM seul sur stdout. [Schéma go-librespot](https://github.com/devgianlu/go-librespot/blob/master/config_schema.json), [Lecteur go-librespot](https://github.com/devgianlu/go-librespot/blob/master/player/player.go#L28), [Source process Snapcast](https://github.com/snapcast/snapcast/blob/develop/doc/player_setup.md#process)

```yaml
audio_backend: pipe
audio_output_pipe: /run/audio-station/spotify.fifo
audio_output_pipe_format: s16le
audio_output_pipe_wait_for_reader: true
```

## Démarrer et qualifier le premier client en S1

1. Sous autorisation, démarrer les deux processus dédiés au premier plan avec un état isolé, sans lancer d’instance en double. Remplacer les variables du gabarit par les valeurs relevées sur le Pi. Choisir un PCM ALSA direct du MiniAmp, de forme `hw:CARD=…,DEV=…`. Utiliser `--hostID` si la version le supporte et vérifier l’identité effective dans `Server.GetStatus`. Les versions antérieures peuvent documenter `--host` à la place de l’URI. [Options du client Snapcast](https://github.com/snapcast/snapcast/blob/develop/client/snapclient.cpp#L147)

   ```sh
   # Terminal du serveur dédié
   snapserver -c "$AUDIO_STATION_SNAPSERVER_CONF"

   # Terminal du client dédié
   snapclient --player alsa --soundcard "$AUDIO_STATION_PCM_DEVICE" \
     --hostID "$AUDIO_STATION_CLIENT_ID" tcp://127.0.0.1:1704
   ```

2. Injecter dans `Music` un signal PCM déterministe à faible niveau avec gauche et droite distinctes. Écouter les deux Visaton et vérifier la cadence, la durée et l’ordre des canaux. En phase de lecture, relever les paramètres ALSA effectivement négociés dans le fichier `hw_params` sous `/proc/asound`. Identifier le détenteur du périphérique de lecture sous `/dev/snd` avec `fuser -v` ou les descripteurs du processus.
3. Contrôler avec `ss -ltnp` le périmètre des écoutes. Lire `Server.GetStatus` via le contrôle local, puis vérifier la connexion du seul client cible, son identité, le flux `Music` et la reconnexion après l’interruption contrôlée de l’instance dédiée. [API JSON-RPC Snapcast](https://github.com/snapcast/snapcast/blob/develop/doc/json_rpc_api/control.md)
4. Consigner les versions, mesures et résultats dans le compte rendu S1, puis arrêter les processus de vérification. Si la mise en service persistante a été autorisée, démarrer ensuite les seules unités dédiées et vérifier leurs journaux et les mêmes invariants de flux et d’écoute.

## Étendre au LAN pour S10 et S11

S10 prépare le profil LAN et le protocole de mesure. Sous autorisation, ajouter uniquement l’interface du LAN de confiance à l’écoute streaming en conservant la boucle locale. Si la version accepte plusieurs `bind_to_address`, les utiliser dans `[tcp-streaming]`. Réserver le contrôle TCP à la boucle locale et maintenir HTTP et HTTPS désactivés. Vérifier les écoutes IPv4 et IPv6 et leurs règles d’accès. La découverte des clients dans Audio Station passe par l’API locale. La publication mDNS du service de streaming reste facultative et doit être limitée au LAN autorisé. [Configuration Snapserver](https://github.com/snapcast/snapcast/blob/develop/server/etc/snapserver.conf)

Vérifier l’absence de port Snapcast accessible depuis Internet, notamment via redirections, UPnP ou exposition IPv6. La connectivité Internet sortante reste utilisable par les radios et Spotify. Toute modification de pare-feu ou de routeur demande un accord explicite. Avant d’activer `Alarm`, vérifier que seul le contrôleur Audio Station peut modifier le routage dans le profil retenu. La restriction à la boucle locale couvre les accès réseau et exige aussi de maîtriser les processus locaux qui pourraient écrire.

S11 utilise au moins deux clients physiques avec le même flux `Music` et une référence de mesure commune. Consigner le décalage, sa dispersion, les ruptures et la reconnexion par rapport aux seuils fixés en S10. Tester `Alarm` séparément en confirmant l’absence de sonnerie et la continuité du flux sur les autres clients. Voir le [contrat Snapcast](SNAPCAST_ARCHITECTURE.md).

## Conserver les preuves

Séparer les tests VPS, les essais réels du chemin PCM et les mesures sur sorties physiques. Conserver localement les traces brutes et ne partager qu’une copie expurgée des noms d’hôte, adresses LAN, identifiants, chemins privés, jetons et données d’authentification. Les comptes rendus peuvent reprendre la boucle locale `127.0.0.1`, les versions, les formats PCM et les verdicts.
