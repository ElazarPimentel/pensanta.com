# Repository Guidelines

## Project Structure & Module Organization
Single-page static site, no build step, zero dependencies. `index.html` is the Spanish homepage at the repo root; `en/index.html` is the English version. All styles live in `styles.css`; client-side behavior (menu, tracking, reduced-motion, password generator, IP detector) is in `site.js`. Portfolio video previews sit in `videos/*.mp4` with `portfolio-poster.svg` as fallback. `vercel.json` handles redirects from legacy URL paths. `public_html/` preserves the old multi-page site for reference and is not deployed. `scripts/` contains legacy portfolio tooling not used in the current flow.

## Build, Test, and Development Commands
No install, no build. Open `index.html` directly in a browser to preview changes — do not run dev servers. Deploy with `gitpush.sh`, which commits and pushes; Vercel auto-deploys on push to `main`.

## Coding Style & Naming Conventions
HTML, CSS, and JS use 2-space indentation. CSS variables for the design tokens (`--color-cream`, `--color-charcoal`, `--color-accent`, `--color-accent-hover`, `--color-gold`, `--color-sage`) are defined at the top of `styles.css` — reuse them instead of hard-coded hex values. Typography: Cormorant Garamond (display) + DM Sans (body), loaded from Google Fonts. Filenames are kebab-case (`lo-de-victor.mp4`). Keep `site.js` dependency-free; no module bundler runs over it.

## Testing Guidelines
No automated tests. After content or layout changes, open `index.html` and `en/index.html` in the browser and verify both locales render consistently. Check responsive behavior in Chrome DevTools (mobile + desktop widths). Verify tracking still fires for WhatsApp, portfolio, and tool-usage events via the browser console or GTM preview.

## Commit & Pull Request Guidelines
Commit history follows a `YYYY-MM-DD-HHmm` timestamp convention (e.g. `2026-02-15-2344`), optionally with a short descriptor. Keep the prefix. `gitpush.sh` handles the commit + push in one step. PRs should list touched files, note any redirect/routing changes in `vercel.json`, and include a before/after screenshot for visual shifts.

## Security & Configuration Tips
Never commit `.env*`, `gsc-service-account.json`, or `.vercel/` — all are gitignored. Analytics IDs (GTM-PBM2Z8BN, GA4 G-5ZVYDQXCG7) and the WhatsApp number (5491137990312) are embedded in the HTML; update them in both `index.html` and `en/index.html` together to keep locales in sync.
