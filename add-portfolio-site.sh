#!/bin/bash
# Add a site to portfolio - automated screenshot + YAML update

if [ -z "$1" ]; then
    echo "Usage: ./add-portfolio-site.sh <URL> [client-name] [description]"
    echo "Example: ./add-portfolio-site.sh https://example.com \"Client Name\" \"Brief description\""
    exit 1
fi

URL=$1
CLIENT_NAME=${2:-""}
DESCRIPTION=${3:-""}

# Generate slug from URL
SLUG=$(echo "$URL" | sed -E 's|https?://||' | sed -E 's|www\.||' | cut -d'/' -f1 | sed 's/\./-/g' | sed 's/pensanta-com//')

echo "🎯 Adding site to portfolio..."
echo "   URL: $URL"
echo "   Slug: $SLUG"
echo ""

# Create temp puppeteer script
cat > /tmp/screenshot-$SLUG.js << JSEOF
const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({headless: 'new'});
  const page = await browser.newPage();
  await page.setViewport({width: 800, height: 500});
  await page.goto('$URL', {waitUntil: 'networkidle2', timeout: 30000});
  await page.screenshot({path: 'img/portfolio/$SLUG-800x500.png'});
  console.log('✓ Screenshot saved');
  await browser.close();
})();
JSEOF

# Capture screenshot
echo "📸 Capturing screenshot..."
node /tmp/screenshot-$SLUG.js

if [ ! -f "img/portfolio/$SLUG-800x500.png" ]; then
    echo "❌ Screenshot failed"
    exit 1
fi

# Convert to WebP
echo "🔄 Converting to WebP..."
cwebp -q 85 "img/portfolio/$SLUG-800x500.png" -o "img/portfolio/$SLUG-800x500.webp" -quiet
rm "img/portfolio/$SLUG-800x500.png"

SIZE=$(ls -lh "img/portfolio/$SLUG-800x500.webp" | awk '{print $5}')
echo "✓ WebP created: $SIZE"

# Get client info if not provided
if [ -z "$CLIENT_NAME" ]; then
    echo ""
    read -p "Client name: " CLIENT_NAME
fi

if [ -z "$DESCRIPTION" ]; then
    read -p "Description: " DESCRIPTION
fi

read -p "Tech stack (comma-separated, e.g. HTML,CSS,React): " TECH_INPUT
read -p "Year [2024]: " YEAR
YEAR=${YEAR:-2024}

# Parse tech stack
IFS=',' read -ra TECHS <<< "$TECH_INPUT"

# Add to portfolio.yaml (before "# Add more projects below")
echo ""
echo "📝 Updating portfolio.yaml..."

# Create YAML entry
YAML_ENTRY="
  - id: $SLUG
    client: \"$CLIENT_NAME\"
    url: \"$URL\"
    description: \"$DESCRIPTION\"
    tech_stack:"

for tech in "${TECHS[@]}"; do
    YAML_ENTRY="$YAML_ENTRY
      - \"$(echo $tech | xargs)\""
done

YAML_ENTRY="$YAML_ENTRY
    year: $YEAR
    image: \"$SLUG-800x500.webp\"
"

# Insert before "# Add more projects below"
sed -i "/# Add more projects below/i\\$YAML_ENTRY" portfolio.yaml

echo "✅ Done! Added $SLUG to portfolio"
echo ""
echo "📁 Files created:"
echo "   - img/portfolio/$SLUG-800x500.webp"
echo "   - portfolio.yaml (updated)"
echo ""
echo "Next: Run script again for more sites, or manually add HTML card to es/portfolio/index.html"

# Cleanup
rm /tmp/screenshot-$SLUG.js
