# Repository Guidelines

## Project Structure & Module Organization
HTML entry points (`index.html`, `index-eng.html`, `about*.html`, `tools.html`) live in the repo root so `server.js` can serve them directly. Locale-specific copies live under `en/` and `es/`, reusable fragments plus YAML content (`portfolio.yaml`, `digitally-carved-pensanta.yaml`) land in `proyectos/`. Static assets follow predictable directories: `css/` for compiled styles, `img/` for hero/portfolio imagery (screenshots land in `img/portfolio/slug-size.png`), and `favicon.*` at the root. Automation helpers (`add-portfolio-site.sh`, `deploytohostinger.sh`, `batch-screenshots.js`) stay at the top level so Express’ static middleware can expose them when needed.

## Build, Test, and Development Commands
- `npm install` – install Node dependencies (Express server, PostCSS utilities, Puppeteer).
- `npm start` – runs `node server.js`, serving the static site with SPA-style fallback on port 3987 (respects `PORT` in `.env.local`).
- `node batch-screenshots.js` – captures/update 800x500 portfolio shots and writes them into `img/portfolio/`.
- `bash deploytohostinger.sh` – wraps the rsync/ftp publish flow; update credentials via `.env.local` before running.

## Coding Style & Naming Conventions
HTML and JS use 2-space indentation; CSS follows the compact format in `css/*.css`. Favor existing utility classes (e.g., `hero-section`, `cta-button`) to keep PurgeCSS efficient. Filenames stay kebab-case (`fabricamos-mochilas.html`), assets stay lowercase with slug + dimensions (`client-800x500.png`). Keep scripts CommonJS (`require`/`module.exports`) to match `server.js`. Run PostCSS manually (`npx postcss css/main.css -o css/main.min.css`) when you add new utilities so PurgeCSS can purge safely.

## Testing Guidelines
There is no automated test suite. After content or layout updates, run `npm start` and verify `/`, `/en/`, and `/es/` render consistently. Use `node batch-screenshots.js` to refresh visual baselines when portfolio entries change, then diff the PNGs before committing. Before deployment, open the main pages in Chrome’s responsive mode (800x500 and mobile) to catch regressions.

## Commit & Pull Request Guidelines
Recent history (`git log --oneline`) shows timestamp-style summaries such as `2025-11-18-0443`. Follow the `YYYY-MM-DD-HHmm` prefix, optionally adding a short descriptor (`2025-11-18-0443 update hero`). Each PR should include a scope summary, list of touched pages/scripts, screenshots for UI shifts, and references to related YAML or portfolio assets. Keep secrets in `.env.local`, check in only intended artifacts, and link deployments or tracking issues.

## Security & Configuration Tips
Store API keys, database credentials, or alternate ports in `.env.local`; `server.js` loads it via `dotenv`. Never commit `.env.local` or `logs/`. When adding automation, prefer environment variables over inline credentials so the deploy flow works locally and on Hostinger.
