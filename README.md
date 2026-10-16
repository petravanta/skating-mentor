# Skating Mentor

A browser-based skating coach. Tell it which skates you're on and where you are, and it plans a practice session, tracks how confident you are in each skill, and shows a skill map of what each skill opens up next.

- **Styles:** Foundations, Cruising & fitness, Park, Street, Dance & artistic, Slalom & freestyle, and Off-skate training.
- **Gear and spots:** skates (inline/quad, brake, wheels, grind-ready) and spots (surface plus features like curbs, ramps, cones) decide what's practical today.
- **Tracking:** rate each attempt from "Not yet" to "On demand"; confidence builds over repeated sessions and fades slowly without practice. A skill unlocks once its prerequisites reach Developing.
- **Photos** of your skates and spots.

## Your data

Everything is stored in your browser (`localStorage`). Use **Export backup** under *Skates, spots & styles* to download a JSON file with your log, gear, spots and photos, and **Import backup** to restore it on any device.

## Running it

It's a single static file, `index.html`, with no build step. Open it in a browser, or serve it with GitHub Pages (Settings → Pages → Deploy from branch → `main` / root).
