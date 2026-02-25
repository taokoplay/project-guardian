#!/bin/bash
# Project Guardian Release Script
# Usage: ./release.sh <version> [token]
# Example: ./release.sh 1.1.0 ghp_xxxxx

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check parameters
if [ -z "$1" ]; then
    echo -e "${RED}❌ Error: Version number required${NC}"
    echo "Usage: ./release.sh <version> [token]"
    echo "Example: ./release.sh 1.1.0"
    echo "         ./release.sh 1.1.0 ghp_xxxxx"
    exit 1
fi

VERSION=$1
TAG="v$VERSION"
TOKEN=$2

echo -e "${BLUE}🚀 Releasing Project Guardian $TAG${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 1. Check working directory
echo -e "${YELLOW}📋 Checking working directory...${NC}"
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${RED}❌ Working directory is not clean${NC}"
    echo "Uncommitted changes:"
    git status --short
    echo ""
    echo "Please commit or stash changes first"
    exit 1
fi
echo -e "${GREEN}✅ Working directory is clean${NC}"
echo ""

# 2. Confirm CHANGELOG update
echo -e "${YELLOW}📝 Checking CHANGELOG.md...${NC}"
if ! grep -q "\[$VERSION\]" CHANGELOG.md; then
    echo -e "${RED}❌ Version $VERSION not found in CHANGELOG.md${NC}"
    echo "Please update CHANGELOG.md first"
    exit 1
fi
echo -e "${GREEN}✅ CHANGELOG.md contains version $VERSION${NC}"
echo ""

# 3. Show what will be released
echo -e "${BLUE}📦 Changes in this release:${NC}"
echo ""
sed -n "/## \[$VERSION\]/,/## \[/p" CHANGELOG.md | head -n -1
echo ""

# 4. Confirm release
echo -e "${YELLOW}Continue with release? (y/n)${NC}"
read -r response
if [ "$response" != "y" ]; then
    echo -e "${RED}❌ Release cancelled${NC}"
    exit 1
fi
echo ""

# 5. Create tag
echo -e "${YELLOW}🏷️  Creating tag $TAG...${NC}"
RELEASE_NOTES=$(sed -n "/## \[$VERSION\]/,/## \[/p" CHANGELOG.md | head -n -1)
git tag -a "$TAG" -m "Release version $VERSION

$RELEASE_NOTES"
echo -e "${GREEN}✅ Tag $TAG created${NC}"
echo ""

# 6. Push to GitHub
echo -e "${YELLOW}📤 Pushing to GitHub...${NC}"

if [ -n "$TOKEN" ]; then
    # Use token if provided
    git remote set-url origin "https://${TOKEN}@github.com/taokoplay/project-guardian.git"
    git push origin main
    git push origin "$TAG"
    # Clean up token
    git remote set-url origin "https://github.com/taokoplay/project-guardian.git"
else
    # Use default authentication
    git push origin main
    git push origin "$TAG"
fi

echo -e "${GREEN}✅ Pushed to GitHub${NC}"
echo ""

# 7. Update local skill (if exists)
SKILL_DIR="/Users/xutaoyu/.craft-agent/workspaces/my-workspace/skills/project-guardian"
if [ -d "$SKILL_DIR" ]; then
    echo -e "${YELLOW}📦 Updating local skill...${NC}"

    # Copy files
    cp -r "$SCRIPT_DIR"/* "$SKILL_DIR/"

    # Repackage
    cd /Users/xutaoyu/.craft-agent/workspaces/my-workspace/skills
    python skill-creator/scripts/package_skill.py project-guardian > /dev/null 2>&1

    echo -e "${GREEN}✅ Local skill updated and repackaged${NC}"
    echo ""
else
    echo -e "${YELLOW}⚠️  Local skill directory not found, skipping update${NC}"
    echo ""
fi

# 8. Summary
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Release $TAG completed successfully!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo ""
echo "1. Create GitHub Release:"
echo -e "   ${BLUE}https://github.com/taokoplay/project-guardian/releases/new${NC}"
echo ""
echo "2. Select tag: $TAG"
echo ""
echo "3. Release title: Project Guardian $TAG"
echo ""
echo "4. Copy release notes from CHANGELOG.md"
echo ""
echo "5. Publish release"
echo ""
echo -e "${BLUE}📊 Version info:${NC}"
echo "   Repository: https://github.com/taokoplay/project-guardian"
echo "   Tag: $TAG"
echo "   Commit: $(git rev-parse --short HEAD)"
echo ""
echo -e "${BLUE}🔄 Users can update with:${NC}"
echo "   cd ~/tools/project-guardian && git pull origin main"
echo ""
