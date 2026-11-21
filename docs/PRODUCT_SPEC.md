# Spécification produit v2

Audio Station est un lecteur stéréo, radio-réveil et point de diffusion multiroom sur Raspberry Pi 3. L’utilisation locale passe par un TFT paysage de 320 × 240, un encodeur avec poussoir, quatre boutons et des commandes capacitives. Le montage utilise un HiFiBerry MiniAmp et deux haut-parleurs Visaton FR 8 de 8 Ω.

## Fonctions

| Fonction | Comportement attendu |
| --- | --- |
| Fichiers locaux et radio Internet | Le lecteur décode la source en PCM et l’envoie au flux Snapcast `Music`. Les fichiers locaux restent utilisables sans Internet. |
| Spotify | go-librespot alimente `Spotify` via une FIFO ou un processus qui émet du PCM brut. |
| Diffusion multiroom | `snapserver` est dédié à Audio Station. Le premier `snapclient` tourne sur le Pi et utilise `127.0.0.1`. Les clients autorisés du LAN peuvent écouter un même flux de façon synchronisée. |
| Commandes | La vue Multiroom du TFT indique les clients connus et connectés, leurs groupes, flux, volumes et mutes. Le contrôle JSON-RPC gère les changements et se resynchronise à la reconnexion. La rotation de l’encodeur règle le client local uniquement. |
| Réveil | Une sonnerie disponible sur le Pi alimente `Alarm` après confirmation du groupe isolé du client local. Le bouton capacitif dédié arrête la sonnerie. La restauration respecte les changements indépendants et les autres clients conservent leur lecture. |
| Audio physique | Le seul processus qui ouvre la sortie ALSA du MiniAmp en production est le `snapclient` local. Le MiniAmp alimente à lui seul les deux canaux. |

## Exigences d’exploitation

- Utiliser l’API JSON-RPC officielle de Snapcast pour gérer les clients, groupes, flux, volumes et mutes. Confirmer les changements à partir de l’état observé.
- Maintenir le contrôle sur la boucle locale et réserver la diffusion au LAN autorisé. Garder les exemplaires de configuration propres au projet dans un espace dédié. Les services des autres projets restent hors périmètre.
- Prévoir un PCB d’interconnexion avec les connecteurs de commandes sur le bord. Réserver GPIO16, GPIO18 à GPIO21 et GPIO26 au MiniAmp en numérotation BCM. [Contrat matériel](HARDWARE_CONTRACT.md)
- Réserver le VPS au développement et à la simulation sans réseau ni GPIO. Obtenir un accord explicite avant installation de services ou changement de configuration système.

## Critères de livraison

- En S0, la DEMO se déroule entièrement hors ligne et génère un PNG. La CI locale vérifie la simulation et l’invariant d’accès à ALSA.
- En S1, démontrer sur le Pi le chemin PCM → snapserver → snapclient local → MiniAmp et vérifier la stéréo, le format effectivement négocié et l’exclusivité ALSA.
- En S11, mesurer la synchronisation et la reconnexion d’au moins deux clients physiques et vérifier la sonnerie locale sur cette topologie.

Le [contrat Snapcast](SNAPCAST_ARCHITECTURE.md) détaille les flux et le réveil. Le [plan des sprints](SPRINTS.md) et le [backlog](../BACKLOG.md) relient chaque fonction à sa qualification.
