# Aura-Clicker v0.1.6 — Release Notes

**Date** : 7 avril 2026  
**Auteur** : Aura Néo  

---

## 🚀 Nouveautés

### Hotkeys synchronisés avec l'interface
- **F3** (Mode Avancé) et **F6** (Auto-clic) récupèrent maintenant les valeurs actuelles des champs de la fenêtre ouverte
- Plus besoin de cliquer sur "Démarrer" pour appliquer les nouveaux paramètres — le hotkey suffit !
- Cohérence parfaite entre l'utilisation des boutons et des raccourcis clavier

### Diagnostic des modes actifs
- Affichage dans l'historique des modes actifs au démarrage :
  - `Modes actifs: Humanisé: ±3px, Jitter temporel: +0.008s-0.015s, Répétition: ON`
- Permet de vérifier instantanément que les options sont bien prises en compte

---

## 🔧 Corrections

### Calcul d'intervalle amélioré
- Conversion robuste avec `float()` au lieu de `int()` pour les valeurs d'intervalle
- Support des intervalles très courts (minimum 1ms)
- Formule : `interval_sec + (interval_ms / 1000.0)`

---

## 📋 Résumé des fonctionnalités testées et validées

| Fonctionnalité | Statut |
|----------------|--------|
| Mode humanisé (décalage pixels) | ✅ Fonctionne |
| Jitter temporel | ✅ Fonctionne |
| Répétition continue | ✅ Fonctionne |
| Intervalles personnalisés | ✅ Fonctionne |
| Hotkey F6 (Auto-clic) | ✅ Valeurs actuelles |
| Hotkey F3 (Mode Avancé) | ✅ Valeurs actuelles |
| Détection d'image | ✅ Présente |

---

## 📥 Téléchargement

- **Windows Installer** : `Aura-Clicker-Setup-0.1.6.exe`
- **Windows Portable** : `Aura-Clicker-Windows.zip`

---

## 🔄 Mise à jour depuis v0.1.5

1. Désinstallez ou supprimez l'ancienne version
2. Installez la nouvelle version
3. Vos paramètres sont préservés dans `%APPDATA%\Aura-Clicker\settings.json`

---

<p align="center">
  Fait avec ❤️ par <a href="https://auraneo.fr"><strong>Aura Néo</strong></a>
</p>
