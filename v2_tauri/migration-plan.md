# Plan de Migration : Ultra Font Installer (Python) -> Tauri (Rust + SvelteKit)

## Objectif

Migrer l'application "Ultra Font Installer" existante (Prototype Python/PyQt + Rust CLI) vers une application native Tauri stable, performante et esthétique.

## Analyse de l'existant

L'application actuelle repose sur :

1.  **Python (`core.py`)** : Orchestration, gestion des appels système, et wrappers.
2.  **Rust (`src/rust`)** : CLI `font_tool` utilisé pour parser (valider/analyser) les fichiers de police via `ttf-parser`.
3.  **PowerShell (`bin/SystemOps.ps1`)** : Installation/Désinstallation réelle des polices dans le registre Windows.
4.  **UI (PyQt/Fluent)** : Interface utilisateur.

## Stratégie de Migration

Nous allons éliminer la couche Python au profit d'un backend Tauri purement Rust. Cela simplifie la distribution (pas d'interpréteur Python à embarquer) et améliore la sécurité.

### 1. Mapping des Modules (Logique Métier)

| Fonction Python (`core.py`) | Nouvelle Implémentation Tauri (Rust) | Détail Technique                                                                                                                                 |
| --------------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `is_admin()`                | `tauri::command`                     | Utilisation de crates standard ou `winapi` pour vérifier les privilèges.                                                                         |
| `validate_font(path)`       | `tauri::command`                     | **Code existant Rust** (`src/rust/src/main.rs`) déplacé dans `src-tauri`. Utilisation directe de `ttf_parser`.                                   |
| `analyze_font(path)`        | `tauri::command`                     | Idem. Le code de parsing Rust est réutilisé tel quel.                                                                                            |
| `is_font_installed(name)`   | `tauri::command`                     | Scan du dossier `C:\Windows\Fonts` en Rust natif (`std::fs`).                                                                                    |
| `install_font_system(path)` | `tauri::command`                     | Appel de `SystemOps.ps1` via `std::process::Command` (Sidecar ou embedded script). On garde le script PowerShell pour la compatibilité éprouvée. |
| `get_installed_fonts()`     | `tauri::command`                     | Listing de répertoire Rust natif optimisé.                                                                                                       |
| `create_preview_pixmap`     | **Supprimé**                         | Le frontend Web (Svelte) rendra la police directement via CSS `@font-face`. Plus besoin de générer des images.                                   |

### 2. Architecture Technique

**Backend (Rust)**

- `src-tauri/src/main.rs` : Point d'entrée.
- `src-tauri/src/font_ops.rs` : Logique portée de l'ancien binaire Rust (analyse/validation).
- `src-tauri/src/system.rs` : Appels PowerShell et gestion des droits.

**Frontend (SvelteKit)**

- Framework : SvelteKit + Vite.
- UI Library : Custom CSS (Glassmorphism) + GSAP.
- Composants Clés :
  - `GlassPanel` (Conteneur principal style verre).
  - `DragDropZone` (Zone d'upload interactive).
  - `FontPreview` (Rendu typographique variable).

### 3. Sécurité

- **Isolation** : Le frontend n'a pas accès direct au système de fichiers, il doit passer par les commandes Tauri explicitement autorisées.
- **Validation** : Toutes les entrées (chemins de fichiers) sont validées côté Rust avant d'être passées à PowerShell.
- **CSP** : Configuration stricte pour empêcher l'exécution de scripts non autorisés.
