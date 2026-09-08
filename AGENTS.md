# Reagan's Pokémon Adventures

Camera "AR" Pokémon-catching game for Reagan (age 9). Static single-page site on GitHub Pages.

**Live site:** https://minsguy.github.io/REAGANS_POKEMON_ADVENTURES/

Design decisions, status, and the family browser-game conventions live in the Obsidian vault:
`C:\Users\minsk\Knowledge\personal\projects\reagans-pokemon-adventures.md` (and the shared
`personal/references/family-browser-game-js-design.md`). This file is only a pointer plus the
minimum needed to work on the code.

## Files

- `index.html` - the whole game (HTML, CSS, JS module). Script sections: config, persistent state,
  session state, rules, 3D scene, rendering, effects, game flow, input, boot.
- `3d.html` - the standalone 3D prototype with a tuning panel and sensor diagnostics. Kept for
  judging models and debugging orientation on a phone.
- `pokemon.json` - generated roster: id, name, types, generation, base-stat total, rarity tier,
  height in metres, and the size in KB of the regular / shiny 3D model (0 = none). Also records the
  pinned commit of the model repository. Regenerate with `python tools/build-roster.py` (one PokéAPI
  GraphQL call plus one GitHub tree-listing call; no model files are downloaded).
- `cries/{id}.m4a` - real Pokémon cries, converted from PokéAPI's OGG by `tools/build-cries.py`.
- `manifest.webmanifest`, `icon-*.png` - home-screen install. Icons come from `tools/make-icon.py`.

## How it works

- Rear camera is the background. A three.js scene (pinned r170 from jsdelivr) renders on top with a
  transparent canvas. The phone's orientation sensors drive the camera; the screen rotation is
  derived from gravity so landscape and portrait both work.
- Pokémon are 3D models placed on an invisible floor at their real Pokédex height, at a distance
  that scales with height, facing the player, with a cast shadow. Smaller ones spawn closer.
- Models load at runtime from the Pokemon-3D-api assets repository at the commit pinned in
  `pokemon.json` (data files only; none of that repository's scripts are used). Models under 12 KB
  (placeholders) or over 2.5 MB are skipped and the Pokémon falls back to its 2D official artwork,
  drawn with feet on the floor and a contact shadow. Loading failures fall back the same way.
- An animation clip plays only if its name looks like an idle; otherwise the model breathes gently.
- Flick the Pokéball upward to throw. Aim is a forgiving cone toward the nearest on-screen Pokémon,
  using projected screen positions. Absorb, wobble, catch or break-free are shared by both kinds.
- Progress (caught list, stats) is a versioned object in `localStorage`.

## Security stance for third-party assets

Only data files (models, images, audio) are fetched from outside repositories, always pinned to an
exact version or commit, always into the browser sandbox. Never run scripts from those repositories
and never download their files onto the development machine.

## Local testing

Serve the folder over HTTP (fetch of `pokemon.json` fails on `file://`):

```
python -m http.server 8765
```

Desktop has no motion sensors, so the game switches to drag-to-look automatically.
`window.__game.spawnNow(id, shiny, force2d)` spawns a Pokémon in front of the camera;
`window.__game.throwBall({x: 0, y: -1})` throws straight up at it.

## Deploy

Push to `main`; GitHub Pages serves the repo root. No build step.
