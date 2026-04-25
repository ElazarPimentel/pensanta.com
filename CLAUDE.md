# Pensanta.com - Web Development Company

Company website for Pensanta, a web development company in Buenos Aires. Single-page static site mirroring elazarpimentel.com's design.

## Tech Stack
- Pure HTML/CSS/JS (no frameworks, no build step, zero dependencies)
- Cormorant Garamond + DM Sans (Google Fonts)
- Vercel deployment (static)

## Commands
```bash
gitpush.sh      # Commits + pushes; Vercel auto-deploys
```

**NEVER run dev servers** — open `index.html` directly in the browser.

**Auto-deploy rule:** After finishing any task the user asked for (or agreed to) in this repo, run `gitpush.sh` without asking for confirmation. Skip only if the user explicitly says not to deploy, or if there are no changes to commit.

## Design System

### Colors (CSS variables in styles.css)
- `--color-cream`: #faf8f5 (background)
- `--color-charcoal`: #1a1a1a (text, dark sections)
- `--color-accent`: #4a9eff (blue CTAs)
- `--color-accent-hover`: #2980ff
- `--color-gold`: #c9a227 (highlights)
- `--color-sage`: #7d9a78 (checkmarks)

### Typography
- Display: Cormorant Garamond (serif)
- Body: DM Sans (sans-serif)

### Aesthetic
Editorial/luxury with warmth. Same as elazarpimentel.com but with blue accent instead of terracotta.

## Structure

Single page with sections:
1. **Hero** - "Hacemos sitios web y aplicaciones para empresas reales" + laptop mockup
2. **Reassurance** - "Vos ocupate de tu negocio, nosotros nos encargamos de la tecnología"
3. **Services** - 3 cards (Sitios Web, Aplicaciones Web, E-commerce)
4. **Portfolio** - 7 projects with video previews
5. **Additional Services** - PM, Security, Training
6. **Pricing** - 3 tiers
7. **Team** - Elazar (Founder), Mauricio (Tech Lead), Victoria (Security)
8. **Tools** - Password Generator + IP Detector (client-side JS)
9. **Process** - 3 steps
10. **FAQ** - 6 questions
11. **Contact** - WhatsApp CTA box

## Key Files
- `index.html` - Spanish homepage (root)
- `en/index.html` - English version
- `styles.css` - All styles
- `site.js` - Menu, tracking, reduced motion
- `vercel.json` - Vercel config with redirects from old site paths
- `public_html/` - Old multi-page site preserved for reference (not deployed)

## Configuration
- **GTM**: GTM-PBM2Z8BN
- **GA4**: G-5ZVYDQXCG7 (via GTM)
- **WhatsApp**: 5491137990312 with tracking
- **Contact email**: elazar.pimentel@pensanta.com
- **Phone**: +54-9-11-3799-0312

### Analytics Events
- `generate_lead` (label `whatsapp_click`) - WhatsApp link clicks
- `view_item` (portfolio) - Portfolio project clicks
- `tool_usage` - Password generator / IP detector usage

## Routing
- `/` → Spanish (default)
- `/en/` → English
- Old paths redirect via `vercel.json`: `/tools/` → `/#herramientas`, `/about.html` → `/`, `/index-eng.html` → `/en/`, etc.

## Prices (same as elazarpimentel.com)
- Landing Page: $500.000 ARS (U$S 350)
- Sitio Full: $1.500.000 ARS (U$S 1.000)
- E-commerce: $2.500.000 ARS (U$S 1.700)

## SEO
- Schema.org: WebSite, ProfessionalService, FAQPage
- Open Graph + Twitter Cards
- Hreflang: es (default), en (/en/)
- `sitemap.xml`, `robots.txt`

## Portfolio Sites
1. Ayudem → ayudem.com.ar (enterprise app)
2. Dra. Andrea Esparza → draandreaesparza.com
3. Lo de Victor → lodevictor.com
4. Contenido Pensanta → contenido.pensanta.com (automation)
5. Grupo Borisiuk → borisiuk.com.ar (10+ sites)
6. Puia Dental Care → puiadentalcare.com
7. Kids Club Café → kidsclubcafe.com.ar

Videos live in `/videos/*.mp4`. Projects without a video fall back to `portfolio-poster.svg`.

## Deployment
- Target: Vercel (static, no build)
- Vercel project: `elazar-pimentel-portfolio/pensanta-com`
- Domain: pensanta.com
- Deploy: `gitpush.sh` (Vercel auto-deploys on push)

## GSC Service Account
`gsc-service-account.json` (gitignored) — shared with other sites.
