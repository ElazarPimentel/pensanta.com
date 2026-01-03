# GSC SEO Optimization Workflow - LLM Instructions
# version 2

**CRITICAL: You MUST follow this complete workflow when optimizing a website's SEO.**

## 📋 Complete Workflow (Follow in Order)

### Step 1: Read This Guide
- You're reading it now ✓
- Understand the diagnostic criteria below
- Know which MCP tools to use

### Step 2: Read GSC Reports
**Location:** `gsc-reports/YYYY-MM-DD-HHMM-domain-gsc-report.json`

**Read and analyze:**
```bash
# Find latest report
ls -t gsc-reports/*.json | head -1

# Read the JSON report
cat gsc-reports/YYYY-MM-DD-HHMM-domain-gsc-report.json
```

### Step 3: Diagnose Issues
**Issue Type A: 0 Impressions (Not Indexed)**
- Site not appearing in Google search results
- **Cause:** Missing/broken sitemap, robots.txt blocking, not submitted to GSC, any other cause you know of or can find out. 
- **Priority:** URGENT

**Issue Type B: High Impressions + 0 Clicks (Poor CTR)**
- Site showing in search but nobody clicking
- **Cause:** Bad titles/descriptions, all the causes you know of, position >10, mismatch with search intent
- **Priority:** HIGH 

**Issue Type C: Low Position (>10)**
- Ranking poorly for target keywords
- **Cause:** Weak content, poor keywords, lack of relevance, any other you know of.
- **Priority:** MEDIUM (long-term work)

### Step 4: Analyze Website Code

**Required files to review:**
# Next.js sites - all relevant files
- run tree.sh (not ./tree.sh)
- understand the project structure
- analyze the website for:
-- SEO metadata (title, description, keywords, OG tags)
-- Main content, H1 tags, JSON-LD structured data
-- public/sitemap.xml          # Sitemap (update before you deploy with gitpush.sh (not ./gitpush.sh)
- public/robots.txt           # Ensure not blocking Googlebot

# Vite/React sites - check:
-- SEO meta tags in <head> and other relevant places of the code.
-- Main content, H1 tags and any other you find relevant. 
- public/sitemap.xml          # Sitemap (update before you deploy with gitpush.sh -not ./gitpush.sh- or any deploy shell script used for the project)
- public/robots.txt           # Ensure not blocking Googlebot

**What to look for:**
1. **Title tags** - Match top query keywords from GSC report?
2. **Meta descriptions** - Compelling? Include target keywords?
3. **H1 tags** - Include location + primary keyword?
3. **H2 tags** - Include relevant information?
5. **Keywords meta** - remove, main search engines ignore it, waste of time. 
6. **Structured data (JSON-LD)** - Present? Valid schema?
7. **Sitemap** - Exists? Includes all pages? Updated?
8. **More** - Do more to get better results. Take initiative, suggest changes. Run function date to get current year, do a web search to obtain up to date information about how to enhance SEO for this project. 

### Step 5: Configure Site URL (Critical for GSC Reports)

**Add site URL to config file so GSC report generator can verify folder mapping:**

**Option 1: package.json (recommended for Next.js/Vite):**
```json
{
  "name": "project-name",
  "version": "1.0.0",
  "homepage": "https://domain.com"  // Add this line
}
```

**Option 2: .env file (alternative):**
```bash
SITE_URL=https://domain.com
```

**Option 3: vercel.json (if using Vercel):**
```json
{
  "domains": ["domain.com"]
}
```

**Why this matters:**
- GSC report generator currently GUESSES folder by domain name
- Adding URL confirms correct folder mapping
- Prevents future errors if folders renamed

### Step 6: Enhance SEO to Address Issues

**For Issue Type A (0 Impressions):**
1. Verify sitemap exists at `/public/sitemap.xml` or is auto-generated
2. Ensure sitemap includes all pages with correct URLs, if it does not, update it. 
3. Check `robots.txt` allows Googlebot: `User-agent: * / Allow: /`
4. Add/update meta tags if missing
5. Add JSON-LD structured data (LocalBusiness/Organization schema)
6. Any other enhancement you consider worth doing, take initiative, if in doubt, ask the user.

**For Issue Type B (High Impressions, 0 Clicks):**
1. Extract top 5 queries from `data.queries_28d` with impressions but 0 clicks
2. Update page titles to include these keywords naturally only if they are related to the content of this website, when in doubt, ask user. 
3. Write compelling meta descriptions (140-160 chars) matching search intent
4. Check pages ranking position >3 - these need title/description work
5. Ensure H1 tags include primary keyword + location
6. Any other enhancement you consider worth doing, take initiative, if in doubt, ask the user.

**For Issue Type C (Low Position >10):**
1. Identify underperforming queries from `data.queries_28d` (position >10)
2. Enhance content depth - add sections addressing these queries
3. Add internal links between related pages
4. Update SEO to include long-tail variations (not keywords)
5. Improve semantic relevance throughout content
6. Any other enhancement you can think of, take initiative, if in doubt ask user.

**SEO Enhancement Checklist:**
# Update these in order:
☐ layout.tsx (Next.js) or index.html (Vite) - title, description, OG tags, canonical URL (always use https://domain.com without www)
☐ page.tsx or App.tsx - H1 tags, content keywords, JSON-LD structured data
☐ Configure www → non-www redirect (see below)
☐ Verify/update sitemap.xml with all pages
☐ Ensure robots.txt allows crawling
☐ Run pnpm build and fix any errors

**Configure WWW Redirect (Critical for SEO):**
For small sites (<10 pages), always use non-www version to avoid duplicate content.

**Vercel/Next.js sites:**
Add to next.config.js or next.config.ts:
```javascript
async redirects() {
  return [
    {
      source: '/:path*',
      has: [{ type: 'host', value: 'www.domain.com' }],
      destination: 'https://domain.com/:path*',
      permanent: true,
    },
  ]
}
```

**Vite sites on Vercel:**
Create vercel.json:
```json
{
  "redirects": [
    {
      "source": "/:path*",
      "has": [{ "type": "host", "value": "www.domain.com" }],
      "destination": "https://domain.com/:path*",
      "permanent": true
    }
  ]
}
```

**Hostinger PHP sites:**
Add to .htaccess (if accessible):
```apache
RewriteEngine On
RewriteCond %{HTTP_HOST} ^www\.domain\.com [NC]
RewriteRule ^(.*)$ https://domain.com/$1 [L,R=301]
```

Replace "domain.com" with actual domain name.


### Step 7: Update Sitemap
**Next.js sites with auto-generation:**
# Check if sitemap is auto-generated in next.config
grep -i sitemap next.config.*
# If auto-generated, rebuild:
pnpm build

**Manual sitemaps:**
# Check sitemap exists and is valid
cat public/sitemap.xml

# Verify all pages included with correct priority
# Homepage: priority 1.0
# Main pages: priority 0.8
# Secondary pages: priority 0.6, etc


**Generate sitemap (if script exists):**
# Some sites have generation script
node scripts/generate-sitemap.js
# Or in package.json prebuild hook
pnpm build  # Runs prebuild automatically
# Else
you generate it manually or update it.


### Step 8: Deploy Changes
**Vercel Deployment (Next.js/Vite sites):**

# ALWAYS use gitpush.sh (handles add, commit, push)
gitpush.sh (not ./gitpush.sh) 

# Vercel auto-deploys on push to main branch
# Wait 2-3 minutes for deployment to complete


**Hostinger Deployment (PHP/Static sites):**
# Check if deploy.sh exists
ls *deploy*.sh

# Run deployment script
(script found)


**IMPORTANT:**
- Vercel sites: Use `gitpush.sh` only (no manual `git push`)
- Hostinger sites: Use deploy script you found, else ask user
- NEVER skip deployment - changes must go live

### Step 9: Verify Site in GSC and Submit Sitemap via MCP

**Check if site exists in GSC:**
```python
# List all properties to find exact site_url format
mcp__gsc__list_properties()
# Returns: sc-domain:example.com OR https://www.example.com
```

**If site NOT in list, add and verify it (full automated workflow):**
```python
# 1. Get verification meta tag
mcp__gsc__get_verification_token(site_url="https://example.com")
# Returns: <meta name="google-site-verification" content="TOKEN" />

# 2. Add the meta tag to site's <head> section (layout.tsx or index.html)
# 3. Deploy with gitpush.sh

# 4. Verify ownership (after deployment completes)
mcp__gsc__verify_site(site_url="https://example.com")

# 5. Add to Search Console as domain property
mcp__gsc__add_site(site_url="sc-domain:example.com")
```

**If site already verified (just needs adding):**
```python
# Add domain property (recommended)
mcp__gsc__add_site(
  site_url="sc-domain:example.com"
)

# OR add URL prefix property
mcp__gsc__add_site(
  site_url="https://www.example.com"
)
```

**Check current sitemap status:**
```python
mcp__gsc__get_sitemaps(
  site_url="sc-domain:example.com"  # Use exact format from list_properties
)
```

**Submit sitemap (if missing or needs refresh):**
```python
mcp__gsc__submit_sitemap(
  site_url="sc-domain:example.com",
  sitemap_url="https://example.com/sitemap.xml"  # Full URL to sitemap
)
```

**CRITICAL:** Wait for deployment to complete BEFORE submitting sitemap!

### Step 10: Generate SEO-STATUS.txt

**ONLY after completing ALL steps above:**
```bash
echo -e "OPTIMIZED\n$(date +%Y-%m-%d)" > gsc-reports/SEO-STATUS.txt
```

**Then commit the status file:**
```bash
gitpush.sh  (no ./) # Commits and pushes SEO-STATUS.txt
```

This marks the site as optimized and prevents duplicate work.

---

## 🔧 MCP Tools Reference

**List all GSC properties:**
```python
mcp__gsc__list_properties()
```

**Get search analytics:**
```python
mcp__gsc__get_search_analytics(
  site_url="sc-domain:example.com",
  days=28,
  dimensions="query"  # or "page", "device", "country"
)
```

**Get performance overview:**
```python
mcp__gsc__get_performance_overview(
  site_url="sc-domain:example.com",
  days=28
)
```

**Inspect specific URL:**
```python
mcp__gsc__inspect_url_enhanced(
  site_url="sc-domain:example.com",
  page_url="https://example.com/"
)
```

**Batch URL inspection:**
```python
mcp__gsc__batch_url_inspection(
  site_url="sc-domain:example.com",
  urls="https://example.com/page1\nhttps://example.com/page2"
)
```

**Check indexing issues:**
```python
mcp__gsc__check_indexing_issues(
  site_url="sc-domain:example.com",
  urls="https://example.com/page1\nhttps://example.com/page2"
)
```

**Submit/manage sitemaps:**
```python
# Get current sitemaps
mcp__gsc__get_sitemaps(site_url="sc-domain:example.com")

# Submit new sitemap
mcp__gsc__submit_sitemap(
  site_url="sc-domain:example.com",
  sitemap_url="https://example.com/sitemap.xml"
)

# Delete sitemap (if needed)
mcp__gsc__delete_sitemap(
  site_url="sc-domain:example.com",
  sitemap_url="https://example.com/old-sitemap.xml"
)
```

---

## 📊 Report File Structure

**JSON Report:** `gsc-reports/YYYY-MM-DD-HHMM-domain-gsc-report.json`
```json
{
  "site_url": "sc-domain:example.com",
  "period": { "start": "2025-11-22", "end": "2025-12-20", "days": 28 },
  "data": {
    "queries_28d": [ ... ],    // Top 50 search queries
    "pages_28d": [ ... ],       // Top 50 pages
    "devices_28d": [ ... ],     // Mobile/Desktop/Tablet breakdown
    "countries_28d": [ ... ],   // Top 20 countries
    "daily_28d": [ ... ],       // Daily trends (days with traffic)
    "query_page_28d": [ ... ]   // Top 30 query+page combinations
  },
  "summary": {
    "total_clicks_28d": 41,
    "total_impressions_28d": 439,
    "average_ctr_28d": 9.34,
    "total_queries": 50,
    "total_pages": 4
  }
}
```

**HTML Report:** `gsc-reports/YYYY-MM-DD-HHMM-domain-gsc-report.html`
- Human-readable summary
- Top queries and pages tables
- Device/country breakdown
- View in browser for quick analysis

**Status File:** `gsc-reports/SEO-STATUS.txt`
```
OPTIMIZED
2025-12-20
```

---

## ⚠️ Common Mistakes to Avoid

❌ **DON'T:**
- Skip reading the GSC report JSON
- Make changes without analyzing current SEO
- Deploy without testing build locally
- Submit sitemap before deployment completes
- Submit sitemap to site not verified in GSC (add it first with mcp__gsc__add_site)
- Create SEO-STATUS.txt before finishing all steps
- Use `git push` directly (use gitpush.sh with no ./)
- Forget to commit SEO-STATUS.txt after creating it

✅ **DO:**
- Follow all steps in order
- Read actual report data, not just summary
- Test locally with `pnpm build` before deploying
- Wait for Vercel deployment (2-3 min) before sitemap submission
- Verify sitemap is accessible at https://domain.com/sitemap.xml
- Use deployment scripts (gitpush.sh or deploy script)
- Double-check SEO-STATUS.txt was pushed to repo

---

## 🎯 Priority Order

When multiple sites need optimization, tackle in this order:

1. **High impressions + 0 clicks** → Quick wins, just need better titles/descriptions
2. **0 impressions** → Need sitemap submission and indexing (takes time)
3. **Low position (>10)** → Need content work (time-consuming)
4. **Already performing well** → Can optimize later for marginal gains


---

## 🔍 Verification Checklist

Before creating SEO-STATUS.txt, verify:

☐ Read GSC JSON report and identified issues
☐ Updated title/description/keywords in code
☐ Enhanced H1 tags with target words
☐ Added/updated JSON-LD structured data
☐ Sitemap exists and includes all pages
☐ Built locally successfully (`pnpm build`)
☐ Deployed via gitpush.sh or deploy script
☐ Waited for deployment to complete
☐ Verified site exists in GSC (added with mcp__gsc__add_site if needed)
☐ Submitted sitemap via MCP
☐ Created SEO-STATUS.txt
☐ Pushed SEO-STATUS.txt to repo

**All checkboxes must be ✓ before marking site as optimized.**
