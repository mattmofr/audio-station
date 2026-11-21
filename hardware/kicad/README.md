# Préparation KiCad

Le dossier KiCad reste réservé à la préparation documentaire du sprint S0. Il
ne contient pas encore de schéma ni de routage validé. Le périmètre et les
contraintes de référence sont décrits dans le [contrat matériel v2](../../docs/HARDWARE_CONTRACT.md).

## Réservations S0

Le PCB d’interconnexion reliera le Raspberry Pi 3, le TFT et le HiFiBerry
MiniAmp. Les GPIO BCM18, BCM19, BCM20, BCM21, BCM16 et BCM26 sont réservés au
MiniAmp et ne doivent recevoir aucune commande utilisateur. Les affectations
de l’encodeur, de son poussoir, des boutons, de la LED et des modules
capacitifs restent à établir après vérification du matériel réel.

Tous les connecteurs des commandes doivent être placés en bord de PCB. Cette
contrainte doit être conservée dans l’implantation afin de faciliter le
câblage, les mesures et la maintenance.

## Passage aux schéma et routage

Le schéma et le routage seront réalisés en S8, après les mesures électriques
et l’identification des composants effectuées en S7 sur le montage réel. Les
mesures devront confirmer le brochage du TFT et du tactile, les niveaux
logiques, les alimentations, les masses, le courant disponible et le
connecteur du MiniAmp. Aucune empreinte ni liaison de commande ne doit être
considérée comme définitive avant cette confirmation.

Les essais sur le VPS et les simulations servent uniquement à préparer et
vérifier les contraintes. Ils ne remplacent pas les mesures réalisées sur le
Raspberry Pi 3 et le matériel effectivement retenu.
