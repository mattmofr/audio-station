# Audio Station

Audio Station est un projet de lecteur musical stéréo et radio-réveil autonome pour Raspberry Pi 3. Le sprint S0 livre un socle Python et un scénario DEMO hors ligne.

## Démarrer

Depuis la racine du dépôt, avec Python 3.11 ou plus récent et le module `venv` disponible, créer l’environnement local et y installer le projet et Pillow.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m audio_station demo --config config/demo.toml --output .demo/frame.png
```

L’installation des dépendances peut utiliser l’index Python configuré. La DEMO et les tests s’exécutent ensuite hors ligne. La commande affiche la trace d’une lecture simulée, du passage en veille, du déclenchement du réveil et de son arrêt. L’option `--output` enregistre le dernier écran au format PNG RGB 320 × 240. Sans cette option, la trace reste dans le terminal. Sans `--config`, la DEMO utilise les valeurs intégrées. La même commande est disponible sous `.venv/bin/audio-station demo`.

Dans `config/demo.toml`, `playback.volume` fixe le volume initial simulé. La table `hardware.control_pins` permet de vérifier une proposition d’affectation BCM. Elle est vide dans l’exemple et n’établit aucune connexion matérielle.

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Le backend audio de S0 conserve ses états en mémoire. Le scénario déclenche le réveil à un point fixe. La lecture de fichiers et de flux radio, la planification du réveil et l’accès au matériel relèvent des sprints suivants.

## Documentation

- [Architecture](ARCHITECTURE.md)
- [Contrat matériel](HARDWARE_CONTRACT.md)
- [Audit de réemploi](REUSE_AUDIT.md)
- [Plan de sprints](SPRINT_PLAN.md)
- [Compte rendu du sprint S0](SPRINT_S0_REPORT.md)
- [Instructions de travail](AGENTS.md)
