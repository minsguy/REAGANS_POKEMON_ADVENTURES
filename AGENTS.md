# Reagan's Pokémon Adventures

Camera "AR" Pokémon-catching game for Reagan (age 9). Static single-page site on GitHub Pages.

**Live site:** https://minsguy.github.io/REAGANS_POKEMON_ADVENTURES/

Design decisions, status, and the family browser-game conventions live in the Obsidian vault:
`C:\Users\minsk\Knowledge\personal\projects\reagans-pokemon-adventures.md` (and the shared
`personal/references/family-browser-game-js-design.md`). This file is only a pointer plus the
minimum needed to work on the code.

## Files

- `index.html` - the whole game (HTML, CSS, JS). Sections in the script: config, persistent
  state, session state, rules, rendering, effects, game flow, input, boot.
- `pokemon.json` - generated roster (id, name, types, generation, base-stat total, rarity tier).
  Regenerate with `python tools/build-roster.py` (one PokéAPI GraphQL call).
- `manifest.webmanifest`, `icon-*.png` - home-screen install. Icons come from `tools/make-icon.py`.

## How it works

- Rear camera is the background. Pokémon spawn at a yaw/pitch around the player; the device
  orientation sensors give the camera direction, so turning the iPad brings them into view.
  Desktop or denied sensors fall back to drag-to-look.
- Artwork loads at runtime from the PokéAPI sprites repository on GitHub; nothing is bundled.
- Flick the Pokéball upward to throw. Aim is a forgiving cone toward the nearest Pokémon.
- Progress (caught list, stats) is a versioned object in `localStorage`.

## Local testing

Serve the folder over HTTP (fetch of `pokemon.json` fails on `file://`):

```
python -m http.server 8765
```

Desktop has no motion sensors, so the game switches to drag-to-look automatically.
`window.__game.spawnNow(id, shiny)` spawns a Pokémon in front of the camera for testing.

## Deploy

Push to `main`; GitHub Pages serves the repo root. No build step.
