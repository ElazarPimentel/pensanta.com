#!/bin/bash
# AIQL Deployment Script
# Safely copies only public files to clean git repository
# This prevents accidentally committing sensitive database files

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Directories
WORK_DIR="/home/rob/Documents/work/pensanta/websites/ayudem/aiql"
GIT_DIR="/home/rob/Documents/work/pensanta/projects/aiql"

# Files to deploy (ONLY these files go to GitHub)
FILES=(
    "aiql.py"
    "README.md"
    "cc-db-discovery-protocol.yaml"
    ".gitignore"
)

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}AIQL Safe Deployment to GitHub${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo -e "Working directory: ${YELLOW}${WORK_DIR}${NC}"
echo -e "Git directory:     ${YELLOW}${GIT_DIR}${NC}"
echo ""

# Create git directory if it doesn't exist
if [ ! -d "$GIT_DIR" ]; then
    echo -e "${YELLOW}Creating git directory...${NC}"
    mkdir -p "$GIT_DIR"
fi

# Copy files (only if newer)
echo -e "${BLUE}Copying files...${NC}"
COPIED=0
SKIPPED=0

for file in "${FILES[@]}"; do
    SOURCE="$WORK_DIR/$file"
    DEST="$GIT_DIR/$file"

    if [ ! -f "$SOURCE" ]; then
        echo -e "${RED}✗ Source file not found: $file${NC}"
        continue
    fi

    # Copy if destination doesn't exist or source is newer
    if [ ! -f "$DEST" ] || [ "$SOURCE" -nt "$DEST" ]; then
        cp "$SOURCE" "$DEST"
        echo -e "${GREEN}✓ Copied: $file${NC}"
        ((COPIED++))
    else
        echo -e "  Skipped: $file (unchanged)"
        ((SKIPPED++))
    fi
done

echo ""
echo -e "${GREEN}Files copied: $COPIED${NC}"
echo -e "Files skipped: $SKIPPED (unchanged)"
echo ""

# Check if git is initialized
cd "$GIT_DIR"

if [ ! -d ".git" ]; then
    echo -e "${YELLOW}Git repository not initialized in $GIT_DIR${NC}"
    echo -e "${YELLOW}Initializing...${NC}"
    git init
    git remote add origin https://github.com/ElazarPimentel/aiql.git
    echo -e "${GREEN}✓ Git initialized${NC}"
    echo ""
fi

# Show git status
echo -e "${BLUE}Git status in clean directory:${NC}"
git status --short

echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}Deployment complete!${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo -e "Next steps:"
echo -e "  cd $GIT_DIR"
echo -e "  git add ."
echo -e "  git commit -m \"your message\""
echo -e "  git push origin main"
echo ""
echo -e "${YELLOW}✅ Safe: Only these files can be committed:${NC}"
for file in "${FILES[@]}"; do
    echo -e "   - $file"
done
echo ""
