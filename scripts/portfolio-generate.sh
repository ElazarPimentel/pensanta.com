#!/bin/bash
# Generate portfolio HTML from SQLite database

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_PATH="$SCRIPT_DIR/portfolio.sqlite"
ES_OUTPUT="$SCRIPT_DIR/../public_html/es/portfolio/index.html"
EN_OUTPUT="$SCRIPT_DIR/../public_html/en/portfolio/index.html"

if [ ! -f "$DB_PATH" ]; then
    echo "❌ Database not found. Run ./portfolio-init.sh first"
    exit 1
fi

echo "🏗️  Generating portfolio HTML from database..."
echo ""

# Function to generate HTML card
generate_card() {
    local SLUG=$1
    local NAME=$2
    local URL=$3
    local DESC=$4
    local TECH_STACK=$5
    local YEAR=$6
    local SCREENSHOT=$7
    local FLIP=$8  # Add .flip class to alternating cards

    # Parse tech stack JSON array
    local TECH_BADGES=$(echo "$TECH_STACK" | sed 's/\[//; s/\]//; s/"//g' | awk -F',' '{for(i=1;i<=NF;i++) printf "                                <span class=\"tech-badge\">%s</span>\n", $i}')

    # Get domain from URL for display
    local DISPLAY_URL=$(echo "$URL" | sed 's|https://||; s|http://||; s|/$||')

    cat <<EOF
                <!-- Project: $NAME -->
                <article class="portfolio-card${FLIP}">
                    <div class="portfolio-image">
EOF

    if [ -n "$URL" ]; then
        cat <<EOF
                        <a href="$URL" target="_blank">
                            <img src="/img/portfolio/$SCREENSHOT"
                                 alt="Captura de pantalla de $NAME"
                                 width="800"
                                 height="500">
                        </a>
EOF
    else
        cat <<EOF
                        <img src="/img/portfolio/$SCREENSHOT"
                             alt="$NAME dashboard"
                             width="800"
                             height="500">
EOF
    fi

    cat <<EOF
                    </div>
                    <div class="portfolio-content">
                        <h2>$NAME</h2>
EOF

    if [ -n "$URL" ]; then
        cat <<EOF
                        <p class="portfolio-url">
                            <a href="$URL" target="_blank">
                                $DISPLAY_URL
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                                    <polyline points="15 3 21 3 21 9"></polyline>
                                    <line x1="10" y1="14" x2="21" y2="3"></line>
                                </svg>
                            </a>
                        </p>
EOF
    else
        cat <<EOF
                        <p class="portfolio-url" style="color: var(--color-text-secondary); font-size: var(--font-size-sm);">
                            Sistema de automatización
                        </p>
EOF
    fi

    cat <<EOF
                        <p class="portfolio-description">
                            $DESC
                        </p>
                        <div class="portfolio-meta">
                            <div class="tech-stack">
$TECH_BADGES
                            </div>
                            <span class="portfolio-year">$YEAR</span>
                        </div>
                    </div>
                </article>

EOF
}

# Backup original files
cp "$ES_OUTPUT" "$ES_OUTPUT.bak"
cp "$EN_OUTPUT" "$EN_OUTPUT.bak"

# Read everything up to and including <div class="portfolio-grid">
ES_HEADER=$(sed -n '1,/<div class="portfolio-grid">/p' "$ES_OUTPUT")
EN_HEADER=$(sed -n '1,/<div class="portfolio-grid">/p' "$EN_OUTPUT")

# Read everything from the closing </div> of portfolio-grid to end
# Find line number where portfolio-grid div closes (look for divider)
ES_FOOTER_START=$(grep -n "portfolio-divider" "$ES_OUTPUT" | head -1 | cut -d: -f1)
if [ -z "$ES_FOOTER_START" ]; then
    echo "❌ Could not find portfolio-divider marker in Spanish file"
    exit 1
fi
ES_FOOTER=$(tail -n +$((ES_FOOTER_START - 1)) "$ES_OUTPUT")

EN_FOOTER_START=$(grep -n "<hr class=\"portfolio-separator\"" "$EN_OUTPUT" | head -1 | cut -d: -f1)
if [ -z "$EN_FOOTER_START" ]; then
    echo "❌ Could not find portfolio-separator marker in English file"
    exit 1
fi
EN_FOOTER=$(tail -n +$((EN_FOOTER_START - 1)) "$EN_OUTPUT")

# Generate Spanish portfolio
echo "📄 Generating Spanish portfolio..."
ES_TEMP="$SCRIPT_DIR/.portfolio-temp-es.html"
{
    echo "$ES_HEADER"
    echo ""

    # Query projects in order
    sqlite3 -separator "🔹" "$DB_PATH" \
        "SELECT slug, name, url, description_es, tech_stack, year, screenshot_path, sort_order
         FROM projects
         WHERE include_in_portfolio = 1
         ORDER BY sort_order ASC, id ASC" | \
    {
        COUNTER=0
        while IFS='🔹' read -r SLUG NAME URL DESC TECH_STACK YEAR SCREENSHOT SORT_ORDER; do
            # Alternate .flip class
            FLIP=""
            if [ $((COUNTER % 2)) -eq 1 ]; then
                FLIP=" flip"
            fi

            generate_card "$SLUG" "$NAME" "$URL" "$DESC" "$TECH_STACK" "$YEAR" "$SCREENSHOT" "$FLIP"

            ((COUNTER++))
        done
    }

    echo "            </div>"
    echo ""
    echo "$ES_FOOTER"
} > "$ES_TEMP"

mv "$ES_TEMP" "$ES_OUTPUT"
echo "   ✓ Written to: $ES_OUTPUT"

# Generate English portfolio (similar structure)
echo "📄 Generating English portfolio..."
EN_TEMP="$SCRIPT_DIR/.portfolio-temp-en.html"
{
    echo "$EN_HEADER"
    echo ""

    sqlite3 -separator "🔹" "$DB_PATH" \
        "SELECT slug, name, url, COALESCE(description_en, description_es), tech_stack, year, screenshot_path, sort_order
         FROM projects
         WHERE include_in_portfolio = 1
         ORDER BY sort_order ASC, id ASC" | \
    {
        COUNTER=0
        while IFS='🔹' read -r SLUG NAME URL DESC TECH_STACK YEAR SCREENSHOT SORT_ORDER; do
            FLIP=""
            if [ $((COUNTER % 2)) -eq 1 ]; then
                FLIP=" flip"
            fi

            generate_card "$SLUG" "$NAME" "$URL" "$DESC" "$TECH_STACK" "$YEAR" "$SCREENSHOT" "$FLIP"

            ((COUNTER++))
        done
    }

    echo "            </div>"
    echo ""
    echo "$EN_FOOTER"
} > "$EN_TEMP"

mv "$EN_TEMP" "$EN_OUTPUT"
echo "   ✓ Written to: $EN_OUTPUT"

# Count projects
TOTAL=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM projects WHERE include_in_portfolio = 1")

echo ""
echo "✅ Generated portfolio pages with $TOTAL projects!"
echo ""
echo "Next: Deploy changes with ./deploytohostinger.sh"
