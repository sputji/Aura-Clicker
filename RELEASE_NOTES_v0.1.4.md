## Aura-Clicker v0.1.4

Cette version corrige des blocages critiques du mode Avance et ajoute des outils puissants pour rendre les automatisations plus robustes et plus naturelles.

### Corrections de bugs

- Repetition de sequence (Mode Avance)
  - Correction du bug ou la sequence s'arretait apres un seul passage.
  - Le mode "Repeter la sequence continuellement" fonctionne desormais correctement.
  - Ajout d'un delai entre repetitions de sequence (en secondes) dans les parametres d'execution.

- Ajustement de la taille des fenetres secondaires
  - Les fenetres CTkToplevel s'ajustent au contenu apres rendu (update_idletasks + minsize dynamique).

- Ordre d'affichage (Z-Order)
  - Les fenetres secondaires (Auto Key Presser, Mode Avance, Hotkeys) s'ouvrent maintenant au premier plan (lift + focus + topmost temporaire).

### Nouvelles fonctionnalites

- Jitter Temporel (Time Jitter)
  - Ajout d'une option jitter temporel dans la fenetre principale et le mode Avance.
  - Parametres Min/Max (en secondes) configurables.
  - Les pauses entre actions peuvent varier automatiquement avec random.uniform(min, max).

- Enregistrement de macro a la volee
  - Nouveau bouton: "Enregistrer une macro (F9 pour Stop)" en mode Avance.
  - Enregistrement en temps reel des clics et frappes clavier via pynput.
  - Insertion immediate des actions dans la sequence.

- Reconnaissance d'image (Computer Vision)
  - Nouveau mode d'action: cliquer sur une image (PNG/JPG/JPEG/WEBP).
  - Selection d'image locale depuis l'interface.
  - Detection via pyautogui.locateCenterOnScreen(..., confidence=0.8).
  - Journalisation structuree des echecs de detection avec logique de tentatives.

### Technique

- Version application: 0.1.4
- Dependance ajoutee: opencv-python
- Dependances cle: customtkinter, pyautogui, pynput, keyboard, pillow

### Installation recommandee

```bash
pip install opencv-python pynput
```
