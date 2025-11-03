#!/bin/bash
# Dependency update script
# Updates Python and Node.js dependencies to latest compatible versions

set -e

echo "🔄 Updating dependencies..."
echo ""

# Update Python dependencies
echo "📦 Updating Python dependencies..."
cd suppliersync
if [ -f "requirements.txt" ]; then
    echo "   Checking for outdated packages..."
    pip list --outdated || echo "   All packages up to date"
    echo ""
    echo "   To update all packages: pip install --upgrade -r requirements.txt"
fi
cd ..

# Update Node.js dependencies
echo "📦 Updating Node.js dependencies..."
cd dashboard
if [ -f "package.json" ]; then
    echo "   Checking for outdated packages..."
    npm outdated || echo "   All packages up to date"
    echo ""
    echo "   To update all packages: npm update"
    echo "   To update to latest versions: npm install package@latest"
fi
cd ..

echo ""
echo "✅ Dependency check complete!"
echo ""
echo "⚠️  Important:"
echo "   - Test thoroughly after updating dependencies"
echo "   - Review changelogs for breaking changes"
echo "   - Update requirements.txt and package.json after updates"
echo "   - Run tests: pytest tests/ && npm test"

