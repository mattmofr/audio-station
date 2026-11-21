# Contrat d’architecture Snapcast

## Objet

Snapserver reçoit le PCM sur le Raspberry Pi 3 et distribue les flux synchronisés. Le snapclient local est identifié par sa configuration et sa connexion à `127.0.0.1`. Il est le seul processus autorisé à ouvrir le périphérique ALSA du HiFiBerry MiniAmp en mode exclusif stéréo. Les producteurs remettent leur PCM à snapserver.

Le réseau local sert au transport et à la synchronisation. Les groupes Snapcast déterminent quel flux est routé vers quels clients. Ils ne constituent pas une ACL réseau. La limitation des clients autorisés relève du réseau et, si nécessaire, des options de certificats de Snapcast. La synchronisation réelle et la stabilité sur le LAN restent à mesurer sur matériel.

Le profil LAN conserve la boucle locale. Le réseau de confiance limite les clients distants qui peuvent rejoindre le serveur. [Documentation Snapcast](https://github.com/snapcast/snapcast/blob/develop/README.md)

## Topologie contractuelle

```text
Sources Music, Spotify, Alarm ── PCM local ── snapserver
                                                  ├─ boucle locale 127.0.0.1 ── snapclient local ── ALSA exclusif ── MiniAmp
                                                  └─ LAN ── snapclients distants synchronisés
```

Le snapserver et le snapclient local sont sur le même Pi. La boucle locale `127.0.0.1` et les clients distants du LAN sont deux routes distinctes dans le modèle de contrôle. Le client local doit être découvert puis suivi avec son identifiant stable de configuration, son instance et sa connexion `127.0.0.1` vérifiée. Une adresse seule ne suffit jamais à déduire son identité. Toute ambiguïté d’identité ou de route met la sortie en état sûr muet.

Le flux `Alarm` cible par défaut le groupe contenant uniquement le client local. `Music` est le flux par défaut pour les nouveaux clients. Les flux `Music` et `Spotify` sont sélectionnables pour les groupes du LAN. [Configuration du serveur Snapcast](https://github.com/snapcast/snapcast/blob/develop/server/etc/snapserver.conf)

## Sources et formats PCM

| Source | Entrée | Format cible contractuel | Routage initial |
| --- | --- | --- | --- |
| Music | radio ou fichiers | `48000:16:2`, S16LE signé | groupes Music selon sélection |
| Spotify | go-librespot backend `pipe` vers FIFO | `44100:16:2`, S16LE signé, natif à confirmer pour la version déployée et son fichier de configuration | groupes Spotify selon sélection |
| Alarm | générateur PCM local | `48000:16:2`, S16LE signé | client local seul par défaut |

La notation Snapcast est `fréquence:profondeur:canaux`. Les producteurs écrivent du PCM brut signé, little-endian et entrelacé gauche/droite, sans en-tête WAV. Une trame stéréo S16LE occupe quatre octets. Le débit cible est de 192 000 octets par seconde à 48 kHz et de 176 400 à 44,1 kHz. Un producteur qui sort un autre format requiert une conversion vérifiée avant le FIFO. Le format effectivement négocié par ALSA est relevé séparément. [Formats des sources Snapcast](https://github.com/snapcast/snapcast/blob/develop/doc/configuration.md#sources)

Spotify utilise par défaut le backend `pipe` de go-librespot et une FIFO dédiée lue par snapserver. L’amont fixe 44 100 Hz et deux canaux dans le lecteur et propose `s16le` pour la sortie pipe. La version retenue, `audio_output_pipe`, `audio_output_pipe_format` et le comportement quand le lecteur FIFO est absent sont qualifiés ensemble. Une variante `process` utilise une sortie standard réservée au PCM et écrit ses diagnostics sur la sortie d’erreur. [Lecteur go-librespot](https://github.com/devgianlu/go-librespot/blob/master/player/player.go#L28), [Schéma go-librespot](https://github.com/devgianlu/go-librespot/blob/master/config_schema.json), [Source process Snapcast](https://github.com/snapcast/snapcast/blob/develop/doc/player_setup.md#process)

## API Snapcast et état

Le contrôleur utilise l’API JSON-RPC officielle sur une connexion TCP locale avec un message JSON par ligne. Il appelle `Server.GetStatus` pour obtenir un instantané complet, puis traite `Server.OnUpdate`, `Client.OnConnect`, `Client.OnDisconnect`, `Client.OnVolumeChanged`, `Group.OnMute` et `Group.OnStreamChanged`. En cas de perte, il marque l’état incertain, se reconnecte avec des délais progressifs, relit l’ensemble des clients et écarte les commandes périmées. [API JSON-RPC de contrôle Snapcast](https://github.com/snapcast/snapcast/blob/develop/doc/json_rpc_api/control.md)

Les groupes et flux sont référencés par leurs identifiants Snapcast observés. Le contrôleur conserve une révision locale de l’état et vérifie `Server.GetRPCVersion` au démarrage. Il prépare ses écritures à partir d’un état frais et vérifie leurs effets par relecture. Un changement pertinent d’identité, de groupe ou de flux invalide l’opération. La révision est locale à Audio Station. L’API amont ne fournit ici aucune écriture conditionnelle ou transaction atomique. [API JSON-RPC de contrôle Snapcast](https://github.com/snapcast/snapcast/blob/develop/doc/json_rpc_api/control.md)

L’affectation d’un groupe utilise explicitement `Group.SetClients` avec la liste complète des IDs voulus. Le flux utilise explicitement `Group.SetStream`. Le mute de groupe utilise `Group.SetMute`. Le volume applicatif est appliqué client par client avec `Client.SetVolume`. Chaque appel envoie les deux champs `percent` et `muted`. Lors d’un changement de volume, `muted` conserve sa valeur fraîche. Lors d’un changement de mute, `percent` conserve sa valeur fraîche. `Group.SetVolume` n’est pas une méthode officielle retenue. Un batch JSON-RPC peut réduire les allers-retours, mais son résultat n’est pas atomique. Le contrôleur vérifie donc chaque réponse puis relit l’état. Il préserve toute modification légitime intervenue entre deux écritures.

L’encodeur physique adresse le seul client local. Les écritures de routage sont sérialisées par Audio Station. Le déploiement doit réserver l’accès d’écriture à ce contrôleur pour activer `Alarm`. La boucle locale ne suffit pas à isoler des processus locaux tiers. Si le profil ne permet pas de maîtriser les écritures de contrôle, le producteur `Alarm` reste arrêté. [API de contrôle Snapcast](https://github.com/snapcast/snapcast/blob/develop/doc/json_rpc_api/control.md)

## Isolement et restauration de l’alarme

Une machine d’état sérialise chaque déclenchement, arrêt et restauration. Les autres clients continuent à écouter leur flux, avec leur volume et leur mute.

1. Obtenir un instantané frais et vérifier l’ID et l’instance configurés du client local ainsi que sa connexion à `127.0.0.1`.
2. Mémoriser le rattachement local, le flux précédent et les champs client que l’opération modifiera. Conserver les membres du groupe initial comme précondition de restauration.
3. Vérifier tous les groupes et flux avant écriture. Il ne doit exister aucun autre groupe Alarm actif ni aucun autre client dans le groupe Alarm prévu. Si le contrôle Snapcast ne permet pas d’imposer cette condition, bloquer l’alarme en direct.
4. Si le groupe initial contient d’autres clients, appeler `Group.SetClients` sur ce groupe avec tous ses membres actuels sauf le client local. Relire le serveur et identifier le groupe individuel créé pour le client détaché. Réutiliser le groupe actuel si le client était déjà seul. Appliquer `Group.SetStream` sur ce seul groupe vérifié, puis relire l’état.
5. Appliquer le volume du seul client local avec `Client.SetVolume` si nécessaire. Démarrer la sonnerie uniquement après confirmation de l’appartenance exclusive, du flux `Alarm`, de l’identité du client local et de l’absence de tout autre groupe sur ce flux.
6. Surveiller les changements de routage et la disponibilité du contrôle pendant l’écoute. Couper immédiatement le producteur `Alarm` en cas de dérive ou de perte de confirmation. L’arrêt de la production ne rappelle pas les trames déjà transmises.
7. À l’arrêt, couper le PCM et vider la file du producteur. Empêcher l’écoute locale résiduelle si le contrôle est disponible et attendre le délai de vidange vérifié sur la chaîne déployée avant la restauration. Relire alors l’état.
8. Restaurer seulement les champs modifiés par l’alarme dont la valeur reste compatible avec l’opération. Pour rejoindre un ancien groupe toujours compatible, conserver sa liste fraîche de membres et y ajouter uniquement le client local. Pour un client initialement seul, restaurer le flux de son groupe individuel. Si le groupe a disparu ou qu’une modification concurrente rend le rattachement incertain, conserver l’arrêt et signaler la reprise à confirmer. Vérifier le résultat par un dernier instantané.

Le comportement de détachement est vérifié sur la version retenue. L’amont crée un nouveau groupe pour un client retiré et lui transmet le flux du groupe d’origine. Un échec partiel laisse le producteur arrêté. Après redémarrage, la reprise relit l’état avant d’examiner une trace d’opération restée incomplète. [Implémentation de Group.SetClients](https://github.com/snapcast/snapcast/blob/develop/server/control_requests.cpp#L448-L517)

## Limites et qualification

S1 qualifie uniquement Music sur le Pi 3, en stéréo locale, avec reconnexion et exclusivité ALSA du MiniAmp. Le test doit vérifier le format effectivement négocié par ALSA, le nombre d’octets par trame, la cadence sur un signal et une durée connus, la séparation gauche/droite et l’absence d’un second ouvreur ALSA.

S3 qualifie le PCM des producteurs radio et fichiers de `Music`. Il vérifie les octets par trame, la cadence mesurée sur une durée connue, les canaux gauche et droit avec signaux distincts, l’absence d’en-tête et le format reçu par snapserver. Les écritures partielles sont prises en compte dans la preuve.

S4 qualifie go-librespot avec la version et le fichier de configuration retenus, le backend FIFO, le format effectivement écrit et le comportement sans lecteur. Le backend ALSA reste interdit.

S6 qualifie le PCM Alarm, sa cadence, ses canaux, son arrêt producteur et la purge du résidu avant restauration. Il vérifie aussi le blocage si l’isolement du client local ne peut pas être imposé et la continuité des autres clients dans leur flux.

S10 fixe les seuils d’acceptation avant toute mesure finale. S11 utilise au moins deux clients Snapcast réels sur le LAN et mesure la synchronisation Music et Spotify selon leur disponibilité, ainsi que l’alarme locale seule pendant que les autres clients restent en lecture. Il couvre les changements de groupe, les reconnexions, le reboot du Pi et la perte temporaire du réseau. Le critère est une mesure horodatée de dérive et de latence, pas la seule absence de défaut audible. Les résultats simulés et matériels sont séparés dans le compte rendu.
