# Budget de Performance & Optimisations

Objectif : Maintenir une UI fluide (60fps) même avec des effets de flou et de liquide.

## Budget

| Métrique          | Cible   | Max          |
| ----------------- | ------- | ------------ |
| Bundle Size (JS)  | < 150KB | 300KB        |
| First Paint       | < 0.5s  | 1s           |
| Memory Usage (UI) | < 100MB | 200MB        |
| Animation FPS     | 60      | 30 (Minimum) |

## Optimisations Implémentées

### 1. Rendu

- **Layer Promotion** : Utilisation de `will-change: transform` sur les éléments animés (Liquid Blob).
- **CSS Compositing** : Animations GSAP basées sur `transform` et `opacity` uniquement (pas de changement de `top`/`left` qui cause des reflows).

### 2. Glassmorphism

- **Fallback CSS** : Si `backdrop-filter` n'est pas supporté (GPU faible), bascule automatique sur une opacité simple pour éviter le lag.
- **Réduction de Zone** : Le flou n'est appliqué que sur les panneaux nécessaires.

### 3. Logique (Rust Backend)

- **Async Commands** : Les opérations lourdes (scan de polices) sont exécutées dans des threads Rust (comportement par défaut des commandes tauri) pour ne pas bloquer l'UI main thread.
- **Parsing Natif** : Utilisation de `ttf-parser` (Rust pure) au lieu de spawn un subprocess Python, réduisant l'overhead CPU et mémoire.

### 4. Svelte

- **Reactivity** : Mises à jour ciblées du DOM via le compilateur Svelte.
- **Cleanup** : Utilisation de `onDestroy` pour tuer les timelines GSAP et listeners.

## Recommandations Futures

- **Virtual Scrolling** : Si la liste de polices dépasse 100 items, implémenter un virtual scroller.
- **Texture Cache** : Pour les previews de fonts, utiliser un cache LRU côté frontend.
