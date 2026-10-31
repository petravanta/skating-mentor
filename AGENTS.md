# Notes for coding agents

Follow the shared standards in https://github.com/petravanta/general/blob/main/STANDARDS.md (hub link, theme switch, shared look, phone and desktop layouts, light and dark themes, storage). This file only adds what's specific to Skating Mentor.

- The app is `index.html` with no build step. Serve the folder (`python3 -m http.server`) to run it; `data/` can't load from `file://`.
- The skill graph is data, not code: it lives in `data/skills.json` with its schema in `data/schema/skills.schema.json`. Add or change skills there, never as literals in `index.html`. The loader at the top of the script maps the readable JSON field names onto the short internal ones (`st`, `n`, `d`, `req`, …) and style names onto the one-letter codes saved in profiles.
- Skill ids are stored in people's practice logs. Never rename or reuse one.
- Focus themes are data too: `data/themes.json` (schema `data/schema/themes.schema.json`). Theme ids are saved in `profile.themes`, so never rename or reuse one. `buildPlan` reserves about 60% of a session for chosen themes, alternating between them, after priorities.
- A new style, spot feature, surface or skate setup is a code change: update `STYLES`, `FEAT`, `SURF` or `EQ` in `index.html` and the enums in the schema together.
- Run `node scripts/check-data.js` and the ajv command in CONTRIBUTING.md after editing data.
