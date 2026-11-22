#!/usr/bin/env bash
# Lecture seule : inventaire local avant une qualification audio sur le Pi.
# Ce script ne qualifie jamais le matériel et ne démarre/arrête aucun service.
set -euo pipefail

ROOT=${AUDIO_PREFLIGHT_ROOT:-/}
readonly ROOT

say() { printf '%s\n' "$*"; }
section() { say ""; say "[$1]"; }

section "scope"
say "qualification=NON_TESTE"
say "mode=observation locale en lecture seule"
say "limite=ce rapport ne prouve ni le câblage ni le fonctionnement du MiniAmp"

section "platform"
model=""
if [ -r "$ROOT/proc/device-tree/model" ]; then
    model=$(tr -d '\000' < "$ROOT/proc/device-tree/model" || true)
elif [ -r "$ROOT/proc/cpuinfo" ]; then
    model=$(awk -F':[[:space:]]*' '$1 ~ /^(Model|model name)[[:space:]]*$/ { print $2; exit }' "$ROOT/proc/cpuinfo" || true)
fi
if [ -n "$model" ]; then say "model=$model"; else say "model=NON TESTÉ — modèle indisponible"; fi
say "kernel=$(uname -srvm 2>/dev/null || printf '%s' 'NON TESTÉ — uname indisponible')"
if [ -r "$ROOT/etc/os-release" ]; then
    awk -F= '/^(PRETTY_NAME|ID|VERSION_ID)=/ { gsub(/^"|"$/, "", $2); print $1 "=" $2 }' \
        "$ROOT/etc/os-release" || true
else
    say "os=NON TESTÉ — /etc/os-release indisponible"
fi

section "overlay_candidates"
found_overlay=0
for config in /boot/firmware/config.txt /boot/config.txt; do
    if [ -r "$ROOT$config" ]; then
        say "source=$config"
        # Limiter l'affichage aux noms et valeurs audio, sans arguments ni notes.
        while IFS= read -r line; do
            say "candidate=$line"
            found_overlay=1
        done < <(sed -nE \
            -e 's/^[[:space:]]*(#?[[:space:]]*dtoverlay)[[:space:]]*=[[:space:]]*([A-Za-z0-9_-]+).*/\1=\2/p' \
            -e 's/^[[:space:]]*(#?[[:space:]]*dtparam)[[:space:]]*=[[:space:]]*((audio|i2s)=(on|off)).*/\1=\2/p' \
            "$ROOT$config" || true)
    fi
done
[ "$found_overlay" -eq 1 ] || say "NON TESTÉ — configuration boot indisponible ou aucune ligne candidate"

section "alsa"
if command -v aplay >/dev/null 2>&1; then
    say "aplay=OBSERVE"
    aplay --version 2>&1 || true
    aplay -l 2>&1 || true
else
    say "aplay=NON TESTÉ — commande indisponible"
fi
if [ -r "$ROOT/proc/asound/cards" ]; then
    say "proc_asound_cards=OBSERVE"
    sed -n '1,120p' "$ROOT/proc/asound/cards" || true
else
    say "proc_asound_cards=NON TESTÉ — fichier indisponible"
fi
if command -v fuser >/dev/null 2>&1 && [ -d "$ROOT/dev/snd" ]; then
    for node in "$ROOT"/dev/snd/pcm*p; do
        [ -e "$node" ] || continue
        pids=$(fuser "$node" 2>/dev/null || true)
        say "${node##*/} pids_observes=${pids:-aucun (visibilité selon permissions)}"
    done
else
    say "fuser=NON TESTÉ — commande ou /dev/snd indisponible"
fi

section "software_versions"
for program in snapserver snapclient; do
    if command -v "$program" >/dev/null 2>&1; then
        say "$program=OBSERVE"
        "$program" --version 2>&1 | sed -n '1p' || true
    else
        say "$program=NON TESTÉ — commande indisponible"
    fi
done

section "throttling"
if command -v vcgencmd >/dev/null 2>&1; then
    say "vcgencmd_get_throttled=OBSERVE (valeur brute, aucune qualification déduite)"
    vcgencmd get_throttled 2>&1 || true
else
    say "vcgencmd_get_throttled=NON TESTÉ — commande indisponible"
fi

section "processes"
if command -v ps >/dev/null 2>&1; then
    say "pid_cpu_ram=OBSERVE (pid, commande, CPU %, RAM %, RSS KiB; arguments omis)"
    ps -eo pid=,comm=,pcpu=,pmem=,rss= 2>/dev/null | \
        awk '$2 == "snapserver" || $2 == "snapclient" { print }' || true
else
    say "pid_cpu_ram=NON TESTÉ — ps indisponible"
fi

section "local_listeners"
if command -v ss >/dev/null 2>&1; then
    say "ss=OBSERVE (ports locaux et périmètre, adresses supprimées)"
    ss -H -ltn 2>/dev/null | awk '{
        endpoint = $4
        port = endpoint
        sub(/^.*:/, "", port)
        scope = (endpoint ~ /^127\.0\.0\.1:/ ? "boucle-ipv4" : "autre")
        if (port ~ /^[0-9]+$/) print "port=" port " scope=" scope
    }' || true
else
    say "ss=NON TESTÉ — commande indisponible"
fi

section "result"
say "qualification=NON_TESTE"
say "next_step=consigner séparément tout essai réalisé sur le montage Pi réel"
