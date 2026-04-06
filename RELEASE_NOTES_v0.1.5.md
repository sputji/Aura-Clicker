## Aura-Clicker v0.1.5

Cette version fiabilise le timing d'execution des sequences avancees et finalise l'internationalisation runtime FR/EN pour obtenir des messages metier 100% en anglais quand la langue active est EN.

### Corrections de bugs

- Calcul de l'intervalle des sequences avancees
  - Correction du calcul applique entre actions avec la formule exacte:
    - `secondes + (millisecondes / 1000.0)`
  - Suppression des effets de bord sur le delai effectif en execution.

- Correctif repetition continue (mode Avance)
  - Reprise de boucle sequence fiable quand "Repeter la sequence continuellement" est active.
  - Normalisation robuste de la valeur booleenne de repetition.

- Correctif vitesse de clic en mode Avance
  - Suppression du double delai entre actions qui faussait la vitesse percue.
  - Le reglage secondes/ms influence maintenant de facon directe la cadence d'execution.

- Correctif jitter temporel
  - Le jitter temporel s'ajoute au delai de base au lieu de le remplacer, pour conserver la vitesse choisie.

### Nouvelles ameliorations

- Internationalisation runtime complete FR/EN
  - Traduction des messages de statut worker:
    - Auto-clic
    - Auto-touche
    - Sequence avancee
  - Traduction des messages historiques metier:
    - Demandes d'arret
    - Sauvegardes de parametres
    - Import/export de profils
    - Initialisation/fermeture de l'application
  - Traduction des messages d'erreur metier runtime.

- Fenetres UI synchronisees avec la langue active
  - Main window: statuts de capture/sauvegarde/arret
  - Advanced window: captures, sequence, macro recorder
  - Key Presser window: captures, sauvegarde, arret

- Mode humanise ajoute au clic principal
  - Option de decalage spatial (pixels) sur l'auto-clic principal.
  - Valeur recommandee par defaut: 3 pixels.

- Macro recorder localise
  - Message "enregistrement en cours"
  - Message "enregistrement arrete"

### Technique

- Version application: 0.1.5
- Fichiers principaux modifies:
  - aura_clicker/automation_workers.py
  - aura_clicker/translations.py
  - aura_clicker/windows/main_window.py
  - aura_clicker/windows/advanced_window.py
  - aura_clicker/windows/key_presser_window.py
  - aura_clicker/macro_recorder.py
  - main.py

### Packaging

- Version package Python alignee sur 0.1.5
- Installateur Inno Setup aligne:
  - `AppVersion=0.1.5`
  - `OutputBaseFilename=Aura-Clicker-Setup-0.1.5`
