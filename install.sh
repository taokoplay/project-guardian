#!/bin/bash
# Project Guardian Installation Script

set -e

echo "🚀 Project Guardian Installation"
echo "================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION detected"

# Get project directory
if [ -z "$1" ]; then
    PROJECT_DIR="."
else
    PROJECT_DIR="$1"
fi

PROJECT_DIR=$(cd "$PROJECT_DIR" && pwd)
echo "📁 Project directory: $PROJECT_DIR"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Run scanner
echo "🔍 Scanning project..."
python3 "$SCRIPT_DIR/scripts/scan_project.py" "$PROJECT_DIR"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Installation complete!"
    echo ""
    echo "📚 Next steps:"
    echo "  1. Review the knowledge base at: $PROJECT_DIR/.project-ai/"
    echo "  2. Record your first bug: python3 $SCRIPT_DIR/scripts/update_knowledge.py $PROJECT_DIR --type bug --data bug.json"
    echo "  3. Search for issues: python3 $SCRIPT_DIR/scripts/search_similar.py $PROJECT_DIR \"keyword\""
    echo ""
    echo "📖 Documentation: $SCRIPT_DIR/README.md"
else
    echo ""
    echo "❌ Installation failed. Please check the error messages above."
    exit 1
fi
