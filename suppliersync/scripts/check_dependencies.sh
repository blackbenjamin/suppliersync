#!/bin/bash
# Dependency security check script
# Checks for known vulnerabilities in Python and Node.js dependencies

set -e

echo "🔍 Checking dependency vulnerabilities..."
echo ""

# Check Python dependencies
if command -v safety &> /dev/null; then
    echo "📦 Checking Python dependencies with safety..."
    cd suppliersync
    safety check --json || safety check
    cd ..
else
    echo "⚠️  safety not installed. Install with: pip install safety"
    echo "   Skipping Python dependency check..."
fi

echo ""
echo "📦 Checking Node.js dependencies with npm audit..."
cd dashboard
if [ -f "package-lock.json" ]; then
    npm audit --audit-level=moderate || echo "⚠️  Some vulnerabilities found. Review with: npm audit"
else
    echo "⚠️  package-lock.json not found. Run: npm install"
fi
cd ..

echo ""
echo "✅ Dependency check complete!"
echo ""
echo "💡 Tips:"
echo "   - Update dependencies regularly: pip install --upgrade && npm update"
echo "   - Review and fix vulnerabilities promptly"
echo "   - Use automated dependency scanning in CI/CD"

