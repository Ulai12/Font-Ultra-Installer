# Ultra Font Installer (Tauri v2)

Application desktop moderne pour la gestion de polices, construite avec **Tauri (Rust)** et **SvelteKit**.

## 🚀 Fonctionnalités

- **Glassmorphism UI** : Interface fluide et transparente.
- **Variable Fonts** : Support natif et animations.
- **Rust Backend** : Performances natives pour l'analyse et l'installation via `ttf-parser`.
- **Liquid Effects** : Rendu visuel avancé (SVG Gooey).

## 🛠️ Installation

### Prérequis

- [Node.js](https://nodejs.org/) (v16+)
- [Rust](https://rustup.rs/) (v1.70+)

### Développement

```bash
# Installer les dépendances
cd v2_tauri
npm install

# Lancer en mode dévelopement (UI + Rust HMR)
npm run tauri dev
```

### Build

Pour générer l'installateur Windows (.exe / .msi) ou macOS (.dmg) :

```bash
npm run tauri build
```

Les artefacts seront dans `src-tauri/target/release/bundle/`.

## 📦 Architecture

- `src/` : Frontend SvelteKit + CSS + GSAP.
  - `components/` : Composants UI réutilisables (GlassPanel, LiquidBlob).
- `src-tauri/` : Backend Rust.
  - `src/font_ops.rs` : Logique d'analyse de police (portée de Python).
  - `src/system.rs` : Opérations système (Admin, Install).

## ⚠️ Notes de Migration (Depuis Python)

Ce repo remplace l'ancienne version PyQt/Python.

- La logique `core.py` a été réécrite en Rust (`font_ops.rs`).
- `SystemOps.ps1` est conservé pour les interactions registre bas niveau.
  Voir `migration-plan.md` pour les détails.
