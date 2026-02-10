# Pensanta.com - Web Development Company

Company website for Pensanta, a web development company in Buenos Aires. Single-page static site mirroring elazarpimentel.com's design.

## Tech Stack
- Pure HTML/CSS/JS (no frameworks)
- Cormorant Garamond + DM Sans (Google Fonts)
- Vercel deployment (static)

## Commands
```bash
# No build step needed - static site
gitpush.sh      # Deploy to Vercel
```

**NEVER run dev servers** - use `pnpm build` or just open index.html in browser.

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
4. **Portfolio** - 7 projects with video previews (Ayudem, Esparza, Lo de Victor, Contenido, Borisiuk, Puia, Kids Club)
5. **Additional Services** - PM, Security, Training (compact list)
6. **Pricing** - 3 tiers (Landing $500k, Full $1.5M, E-commerce $2.5M)
7. **Team** - Elazar (Founder), Mauricio (Tech Lead), Victoria (Security)
8. **Tools** - Password Generator + IP Detector (client-side JS)
9. **Process** - 3 steps
10. **FAQ** - 6 questions
11. **Contact** - WhatsApp CTA box

## Key Files
- `index.html` - Spanish homepage (root)
- `en/index.html` - English version
- `styles.css` - All styles (based on elazarpimentel.com)
- `site.js` - Menu, tracking, reduced motion
- `vercel.json` - Vercel config with redirects from old site paths

## Configuration

### Configured
- **GTM**: GTM-PBM2Z8BN
- **GA4**: G-5ZVYDQXCG7 (via GTM)
- **WhatsApp**: 5491137990312 with tracking
- **Contact email**: elazar.pimentel@pensanta.com
- **Phone**: +54-9-11-3799-0312

### Analytics Events
- `whatsapp_click` (generate_lead) - WhatsApp link clicks
- `portfolio_click` (view_item) - Portfolio project clicks
- `tool_usage` - Password generator / IP detector usage

## Routing
- `/` → Spanish (default)
- `/en/` → English
- Old paths redirect: /tools/ → /#herramientas, /about.html → /, etc.

## Prices (same as elazarpimentel.com)
- Landing Page: $500.000 ARS (U$S 350)
- Sitio Full: $1.500.000 ARS (U$S 1.000)
- E-commerce: $2.500.000 ARS (U$S 1.700)

## SEO
- Schema.org: WebSite, ProfessionalService, FAQPage
- Open Graph + Twitter Cards
- Hreflang: es (default), en (/en/)
- Sitemap: sitemap.xml
- Robots: robots.txt

## Portfolio Sites
1. Ayudem → ayudem.com.ar (enterprise app)
2. Dra. Andrea Esparza → draandreaesparza.com
3. Lo de Victor → lodevictor.com
4. Contenido Pensanta → contenido.pensanta.com (automation)
5. Grupo Borisiuk → borisiuk.com.ar (10+ sites)
6. Puia Dental Care → puiadentalcare.com
7. Kids Club Café → kidsclubcafe.com.ar

## Videos
- `/videos/` - Portfolio video previews (.mp4)
- Missing videos: ayudem.mp4, borisiuk.mp4 (use poster fallback)
- Available: draandreaesparza-com.mp4, lo-de-victor.mp4, puia.mp4, kidsclubcafe.mp4

## Deployment
- Target: Vercel (static, no build step)
- Vercel project: `elazar-pimentel-portfolio/pensanta-com`
- Domain: pensanta.com
- Deploy: `gitpush.sh` (commits + pushes, Vercel auto-deploys)
- No `pnpm-lock.yaml` — static site has zero dependencies
- Previous: Hostinger via FTP (deploytohostinger.sh — deprecated)

## Migration Notes (Feb 2026)
- Redesigned from dark-themed multi-page site to single-page editorial layout
- Design cloned from elazarpimentel.com (terracotta → blue accent)
- Old site preserved in `public_html/` for reference
- Tools (password gen, IP detect) converted from PHP to client-side JS
- Emoji tool dropped (database-dependent)
- deploytohostinger.sh no longer used (kept in repo, gitignored)
- Old URL paths redirected in vercel.json (/tools/, /about.html, /index-eng.html, etc.)

## TODO
- [ ] Create Pensanta-branded favicon.svg (currently using EP monogram from elazarpimentel.com)
- [ ] Create Pensanta-branded og-image.jpg (currently reusing elazarpimentel.com image)
- [ ] Record ayudem.mp4 video for portfolio
- [ ] Record borisiuk.mp4 video for portfolio
- [ ] Submit updated sitemap to GSC

## GSC Service Account
`gsc-service-account.json` (gitignored) — shared with other sites.

---
Last updated: 2026-02-09
