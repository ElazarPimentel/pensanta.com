#!/bin/bash
# Scan ~/Documents/work/pensanta/websites for projects and add to database

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_PATH="$SCRIPT_DIR/portfolio.sqlite"
SCAN_ROOT="$HOME/Documents/work/pensanta/websites"

if [ ! -f "$DB_PATH" ]; then
    echo "❌ Database not found. Run ./portfolio-init.sh first"
    exit 1
fi

echo "🔍 Scanning for projects in: $SCAN_ROOT"
echo ""

# Find all directories 2 levels deep
# Level 1: ~/Documents/work/pensanta/websites/*
# Level 2: ~/Documents/work/pensanta/websites/*/subproject
find "$SCAN_ROOT" -mindepth 1 -maxdepth 2 -type d | while read -r PROJECT_DIR; do
    # Skip hidden dirs, node_modules, etc
    BASENAME=$(basename "$PROJECT_DIR")
    if [[ "$BASENAME" == .* ]] || \
       [[ "$BASENAME" == "node_modules" ]] || \
       [[ "$BASENAME" == "scripts" ]] || \
       [[ "$BASENAME" == "docs" ]]; then
        continue
    fi

    # Generate slug from path
    # Example: /home/rob/.../pensanta-com -> pensanta-com
    # Example: /home/rob/.../borisiuk/project1 -> borisiuk-project1
    RELATIVE_PATH="${PROJECT_DIR#$SCAN_ROOT/}"
    SLUG=$(echo "$RELATIVE_PATH" | tr '/' '-')

    # Try to detect project name from directory or package.json
    PROJECT_NAME="$BASENAME"
    if [ -f "$PROJECT_DIR/package.json" ]; then
        PKG_NAME=$(grep -oP '"name"\s*:\s*"\K[^"]+' "$PROJECT_DIR/package.json" 2>/dev/null || echo "")
        [ -n "$PKG_NAME" ] && PROJECT_NAME="$PKG_NAME"
    fi

    # Try to detect URL
    URL=""
    if [ -f "$PROJECT_DIR/.vercel/project.json" ]; then
        # Vercel project
        URL=$(grep -oP '"url"\s*:\s*"\K[^"]+' "$PROJECT_DIR/.vercel/project.json" 2>/dev/null || echo "")
    elif [ -f "$PROJECT_DIR/public_html/index.html" ]; then
        # Traditional website - check canonical URL
        URL=$(grep -oP '<link rel="canonical" href="\K[^"]+' "$PROJECT_DIR/public_html/index.html" 2>/dev/null | head -1 || echo "")
    fi

    # Detect tech stack
    TECH_STACK="[]"
    if [ -f "$PROJECT_DIR/package.json" ]; then
        # Node.js project - detect framework
        if grep -q "next" "$PROJECT_DIR/package.json" 2>/dev/null; then
            TECH_STACK='["NextJS"]'
        elif grep -q "react" "$PROJECT_DIR/package.json" 2>/dev/null; then
            TECH_STACK='["React"]'
        else
            TECH_STACK='["JavaScript"]'
        fi
    elif [ -f "$PROJECT_DIR/public_html/index.html" ]; then
        TECH_STACK='["HTML","CSS"]'
    fi

    # Check if already in database
    EXISTS=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM projects WHERE slug = '$SLUG'")

    if [ "$EXISTS" -gt 0 ]; then
        echo "⏭️  $SLUG (already in database)"
    else
        # Insert new project (not included in portfolio by default)
        sqlite3 "$DB_PATH" <<EOSQL
INSERT INTO projects (slug, name, url, tech_stack, year, include_in_portfolio)
VALUES ('$SLUG', '$PROJECT_NAME', '$URL', '$TECH_STACK', $(date +%Y), 0);
EOSQL
        echo "✅ $SLUG - $PROJECT_NAME"
    fi
done

echo ""
echo "📊 Scan complete!"
sqlite3 "$DB_PATH" "SELECT COUNT(*) || ' total projects' FROM projects;"
echo ""
echo "View all projects:"
echo "  sqlite3 $DB_PATH 'SELECT slug, name, include_in_portfolio FROM projects;'"
echo ""
echo "To include a project in portfolio:"
echo "  sqlite3 $DB_PATH \"UPDATE projects SET include_in_portfolio = 1 WHERE slug = 'project-slug';\""
