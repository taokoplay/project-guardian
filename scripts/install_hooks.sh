#!/bin/bash
# Project Guardian - Git Hooks Installation Script
#
# Quick installation script for Project Guardian Git hooks
# Usage: ./install_hooks.sh [project_path]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get project path
if [ -z "$1" ]; then
    PROJECT_PATH="$(pwd)"
else
    PROJECT_PATH="$1"
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Project Guardian - Git Hooks Installer            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if project path exists
if [ ! -d "$PROJECT_PATH" ]; then
    echo -e "${RED}❌ Error: Project path does not exist: $PROJECT_PATH${NC}"
    exit 1
fi

# Check if it's a Git repository
if [ ! -d "$PROJECT_PATH/.git" ]; then
    echo -e "${RED}❌ Error: Not a Git repository: $PROJECT_PATH${NC}"
    echo -e "${YELLOW}   Initialize Git first: git init${NC}"
    exit 1
fi

# Check if knowledge base exists
if [ ! -d "$PROJECT_PATH/.project-ai" ]; then
    echo -e "${YELLOW}⚠️  Warning: Knowledge base not found at $PROJECT_PATH/.project-ai${NC}"
    echo -e "${YELLOW}   Run scan_project.py first to initialize.${NC}"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ Installation cancelled${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}📂 Project path: $PROJECT_PATH${NC}"
echo ""

# Show menu
echo "Select installation option:"
echo ""
echo "  1) Install all hooks (recommended)"
echo "  2) Install post-commit hook only"
echo "  3) Install pre-push hook only"
echo "  4) Install post-merge hook only"
echo "  5) Install commit-msg hook only"
echo "  6) List current hooks"
echo "  7) Test hooks"
echo "  8) Uninstall all hooks"
echo "  9) Exit"
echo ""
read -p "Enter your choice (1-9): " choice

case $choice in
    1)
        echo ""
        echo -e "${BLUE}🔧 Installing all hooks...${NC}"
        python3 "$SCRIPT_DIR/auto_hooks.py" "$PROJECT_PATH" --install
        ;;
    2)
        echo ""
        echo -e "${BLUE}🔧 Installing post-commit hook...${NC}"
        python3 "$SCRIPT_DIR/auto_hooks.py" "$PROJECT_PATH" --install-post-commit
        ;;
    3)
        echo ""
        echo -e "${BLUE}🔧 Installing pre-push hook...${NC}"
        python3 "$SCRIPT_DIR/auto_hooks.py" "$PROJECT_PATH" --install-pre-push
        ;;
    4)
        echo ""
        echo -e "${BLUE}🔧 Installing post-merge hook...${NC}"
        python3 "$SCRIPT_DIR/auto_hooks.py" "$PROJECT_PATH" --install-post-merge
        ;;
    5)
        echo ""
        echo -e "${BLUE}🔧 Installing commit-msg hook...${NC}"
        python3 "$SCRIPT_DIR/auto_hooks.py" "$PROJECT_PATH" --install-commit-msg
        ;;
    6)
        echo ""
        python3 "$SCRIPT_DIR/auto_hooks.py" "$PROJECT_PATH" --list
        ;;
    7)
        echo ""
        python3 "$SCRIPT_DIR/auto_hooks.py" "$PROJECT_PATH" --test
        ;;
    8)
        echo ""
        echo -e "${YELLOW}⚠️  This will remove all Project Guardian hooks${NC}"
        read -p "Are you sure? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            python3 "$SCRIPT_DIR/auto_hooks.py" "$PROJECT_PATH" --uninstall
        else
            echo -e "${BLUE}Cancelled${NC}"
        fi
        ;;
    9)
        echo ""
        echo -e "${BLUE}Goodbye!${NC}"
        exit 0
        ;;
    *)
        echo ""
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    Installation Complete                  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📚 What's next?${NC}"
echo ""
echo "  • Hooks will run automatically on Git events"
echo "  • post-commit: Records version after each commit"
echo "  • pre-push: Validates health before push"
echo "  • post-merge: Updates knowledge base after merge"
echo "  • commit-msg: Extracts bug fixes from commit messages"
echo ""
echo -e "${BLUE}💡 Tips:${NC}"
echo ""
echo "  • Test hooks: ./install_hooks.sh $PROJECT_PATH (choose option 7)"
echo "  • List hooks: ./install_hooks.sh $PROJECT_PATH (choose option 6)"
echo "  • Uninstall:  ./install_hooks.sh $PROJECT_PATH (choose option 8)"
echo ""
echo -e "${GREEN}✨ Happy coding with Project Guardian!${NC}"
echo ""
