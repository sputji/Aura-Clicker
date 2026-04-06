<p align="center">
  <img src="aura_clicker/assets/logo_aura_clicker.png" width="160" alt="Aura-Clicker Logo"/>
</p>

<h1 align="center">Aura-Clicker</h1>

<p align="center">
  <strong>Automatiseur de souris & clavier intelligent — par Aura Néo</strong><br/>
  <a href="https://github.com/sputji/Aura-Clicker/releases/latest"><img src="https://img.shields.io/github/v/release/sputji/Aura-Clicker?style=flat-square&color=6C63FF&label=version" alt="Version"/></a>
  <a href="https://github.com/sputji/Aura-Clicker/releases"><img src="https://img.shields.io/github/downloads/sputji/Aura-Clicker/total?style=flat-square&color=00C8B4" alt="Downloads"/></a>
  <a href="https://auraneo.fr"><img src="https://img.shields.io/badge/site-auraneo.fr-6C63FF?style=flat-square" alt="Site"/></a>
</p>

---

## Présentation

**Aura-Clicker** est un outil d'automatisation bureau puissant et intuitif. Il permet de simuler des clics de souris répétitifs, des séquences d'actions complexes et des pressions de touches — le tout sans aucune ligne de code.

Conçu pour les joueurs, les testeurs, les automatiseurs et les utilisateurs professionnels souhaitant gagner du temps sur des tâches répétitives.

---

## Fonctionnalités

### 🖱️ Auto-clic simple
- Clic gauche / droit / milieu configurable
- Intervalle personnalisable (millisecondes à secondes)
- Nombre de répétitions limité ou infini
- Position fixe ou position courante du curseur
- Jitter temporel optionnel (min / max en secondes) pour des rythmes plus naturels

### 🔄 Séquences d'actions avancées
- Enregistrement de séquences multi-étapes
- Délais précis entre chaque action
- Mélange clics + touches + déplacements
- Import / Export de séquences au format `.aura_profile.json`
- Répétition continue de la séquence avec délai configurable entre chaque boucle
- Mode humanisé (jitter spatial) et jitter temporel min / max
- Action "Cliquer sur une image" avec détection à l'écran (`confidence=0.8`)
- Journalisation structurée des échecs de détection image

### 🎥 Enregistrement de macro à la volée
- Bouton dédié dans le mode avancé
- Capture en temps réel des clics souris et frappes clavier
- Insertion immédiate dans la séquence
- Arrêt rapide via `F9`

### ⌨️ Presseur de touches
- Simulation de frappes clavier automatisées
- Touche simple ou combinaison (Ctrl+C, Alt+Tab, etc.)
- Intervalle et répétitions configurables

### 🎯 Gestionnaire de profils
- Sauvegarde et chargement de profils complets
- Export / Import entre machines
- Plusieurs profils simultanés

### ⌨️ Raccourcis globaux (hotkeys)
| Action | Touche par défaut |
|--------|-------------------|
| Démarrer auto-clic | `F6` |
| Arrêter auto-clic | `F7` |
| Basculer on/off | `F8` |
| Démarrer séquence avancée | `F3` |
| Arrêter séquence avancée | `F4` |
| Démarrer presseur de touches | `F1` |
| Arrêter presseur de touches | `F2` |

> Toutes les hotkeys sont **entièrement personnalisables** depuis les paramètres.

### 📋 Historique des actions
- Journal complet de toutes les actions effectuées
- Horodatage précis
- Export du journal

### 🛡️ Journal d'erreurs structuré
- Logs JSONL par fichier source
- Diagnostics facilités en cas de problème
- Dossier `logs/errors/` contenant les journaux

---

## Téléchargement

### ⬇️ Dernière version : [Releases GitHub](https://github.com/sputji/Aura-Clicker/releases/latest)

| Plateforme | Fichier | Notes |
|-----------|---------|-------|
| **Windows** | `Aura-Clicker-Setup-x.x.x.exe` | Installateur Windows (recommandé) |
| **Windows** | `Aura-Clicker-Windows.zip` | Binaire portable, aucune installation |
| **macOS** | `Aura-Clicker-macOS.dmg` | Image disque macOS |
| **Linux** | `Aura-Clicker-Linux.tar.gz` | Binaire Linux x86_64 |

> Les releases sont générées **automatiquement** à chaque nouvelle version via GitHub Actions.

---

## Interface

L'application est organisée en **onglets** :

```
┌──────────────────────────────────────────┐
│  🖱️  Auto-Clic    ⌨️  Séquences   🔑  Touches  │
├──────────────────────────────────────────┤
│  Paramètres de clic / séquence / touche  │
│  Bouton Démarrer / Arrêter               │
│  Statut en temps réel                    │
├──────────────────────────────────────────┤
│  📋 Historique des actions               │
└──────────────────────────────────────────┘
```

Fenêtres additionnelles accessibles via la barre de menu :
- **Paramètres hotkeys** — personnaliser tous les raccourcis
- **Mode avancé** — séquences complexes multi-étapes
- **Presseur de touches** — automatisation clavier

---

## Configuration

Les paramètres sont sauvegardés automatiquement dans `settings.json` à côté de l'exécutable.

Les profils sont stockés en `.aura_profile.json` et peuvent être partagés entre machines.

---

## Système requis

| Plateforme | Version minimale |
|-----------|-----------------|
| Windows | Windows 10 64-bit |
| macOS | macOS 12 (Monterey) |
| Linux | Ubuntu 22.04 / Debian 11 |

---

## Raccourcis clavier dans l'interface

| Raccourci | Action |
|-----------|--------|
| `Ctrl+S` | Sauvegarder le profil |
| `Ctrl+O` | Ouvrir un profil |
| `Échap` | Arrêter toutes les automatisations |

---

## Sécurité

- L'application ne communique pas avec internet
- Aucune donnée personnelle collectée
- Les profils restent entièrement locaux

---

## Changelog

### v0.1.4 — 2026-04-07
- Correction du mode "Répéter la séquence continuellement" (bug de fin de boucle)
- Ajout du délai entre répétitions de séquence (mode avancé)
- Ajout du jitter temporel (fenêtre principale + mode avancé)
- Ajout de l'enregistrement de macro à la volée (stop via `F9`)
- Ajout de l'action "Cliquer sur une image" (OpenCV + PyAutoGUI, `confidence=0.8`)
- Amélioration de la gestion des fenêtres secondaires (auto-size + ouverture au premier plan)
- Passage de la version application en `0.1.4`

### v0.1.2 — 2026-04-06
- Nouveau logo Aura Néo officiel
- Pipeline de release automatique GitHub Actions (Windows / macOS / Linux)
- Amélioration de la robustesse des workers d'automatisation
- Journal d'erreurs structuré (JSONL) par fichier source
- Installateur Windows (Inno Setup) inclus dans la release

### v0.1.1b
- Système de logs structurés JSONL
- Tests d'endurance (3, 5, 10 min validés)
- Icône appliquée sur toutes les fenêtres
- Packaging installable Inno Setup

### v0.1.1
- Gestion des profils (import/export)
- Historique des actions
- Thème Aura Néo
- Robustesse des workers

### v0.1.0
- Première version publique
- Auto-clic, séquences, presseur de touches
- Hotkeys globaux configurables

---

<p align="center">
  Fait avec ❤️ par <a href="https://auraneo.fr"><strong>Aura Néo</strong></a>
</p>
