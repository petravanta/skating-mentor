# Skating Mentor

A browser-based skating coach. Tell it which skates you're on and where you are, and it plans a practice session, tracks how confident you are in each skill, and shows a skill map of what each skill opens up next.

## Try it

**[Open Skating Mentor → petravanta.github.io/skating-mentor](https://petravanta.github.io/skating-mentor/)**

It runs in any modern browser on phone or desktop, with no sign-up. To get started:

1. Go to **Skates, spots & styles** and edit the example skates and spots to match yours, and pick the styles you care about.
2. Open **Skill map → List & set levels** and mark the skills you already have, so suggestions start at your level.
3. On **Today**, choose your skates, spot, time and focus. After each drill, tap how it went.

Your progress stays in your browser. On a phone, use *Add to Home Screen* to open it like an app. Google Drive sync is optional; while the app's Google sign-in is in testing mode, it only works for Google accounts the owner has added as test users.

- **Styles:** Foundations, Cruising & fitness, Park, Street, Dance & artistic, Slalom & freestyle, and Off-skate training.
- **Gear and spots:** skates (inline/quad, brake, wheels, grind-ready) and spots (surface plus features like curbs, ramps, cones) decide what's practical today.
- **Tracking:** rate each attempt from "Not yet" to "On demand"; confidence builds over repeated sessions and fades slowly without practice. A skill unlocks once its prerequisites reach Developing.
- **Photos** of your skates and spots.

## Your data

Everything is stored in your browser (`localStorage`). You can also turn on **Google Drive sync** (below) to keep a copy in your own Drive and pick up on another device. Use **Export backup** under *Skates, spots & styles* to download a JSON file with your log, gear, spots and photos, and **Import backup** to restore it on any device.

## Running it

It's a single static file, `index.html`, with no build step. Open it in a browser, or serve it with GitHub Pages (Settings → Pages → Deploy from branch → `main` / root).

## Google Drive sync

Under *Skates, spots & styles → Google Drive*, **Connect Google Drive** signs you in with Google and keeps a file called `Skating Mentor data.json` in your Drive. It saves a few seconds after each change. When you connect on another device, the app merges both: every logged session is kept, and the most recently edited skates, spots and styles win. The app uses the `drive.file` permission, which means it can only see the file it creates, not the rest of your Drive.

Google sign-ins only last about an hour. After that, or after reopening the app, tap **Resume Drive sync** in the header. Everything still saves in the browser in the meantime.

### One-time setup (for whoever hosts the app)

Google needs an OAuth client ID for the site:

1. In [Google Cloud Console](https://console.cloud.google.com/), create a project (any name, e.g. *Skating Mentor*).
2. **APIs & Services → Library**: enable the **Google Drive API**.
3. **APIs & Services → OAuth consent screen**: choose *External*, fill in the app name and your email. Under scopes, add `.../auth/drive.file`. While the app is in *Testing*, add the Google accounts that will use it as test users (or publish the app; `drive.file` doesn't need Google's review).
4. **APIs & Services → Credentials → Create credentials → OAuth client ID**: type *Web application*. Under **Authorized JavaScript origins** add `https://petravanta.github.io` (and `http://localhost:8000` if you test locally).
5. Copy the client ID (it ends in `.apps.googleusercontent.com`) into `GOOGLE_CLIENT_ID` near the top of the script in `index.html`. A client ID is safe to publish; it only works from the origins you listed.

With `GOOGLE_CLIENT_ID` left empty, the Drive section says sync isn't set up and everything else works as before.
