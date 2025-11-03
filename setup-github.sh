#!/bin/bash
# Quick script to set up GitHub repository for SupplierSync

set -e

echo "🚀 Setting up GitHub repository for SupplierSync"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI not found. Installing..."
    echo "   Install with: brew install gh"
    echo "   Or create repository manually at: https://github.com/new"
    exit 1
fi

# Check if already in a git repo
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: Multi-Agent AI Orchestrator with security, testing, and documentation"
fi

# Get repository name
read -p "Enter GitHub repository name (default: suppliersync): " REPO_NAME
REPO_NAME=${REPO_NAME:-suppliersync}

# Get description
read -p "Enter repository description (default: Multi-Agent AI Orchestrator for E-Commerce): " REPO_DESC
REPO_DESC=${REPO_DESC:-"Multi-Agent AI Orchestrator for E-Commerce"}

# Ask if public
read -p "Make repository public? (y/n, default: y): " IS_PUBLIC
IS_PUBLIC=${IS_PUBLIC:-y}

if [ "$IS_PUBLIC" = "y" ] || [ "$IS_PUBLIC" = "Y" ]; then
    VISIBILITY="--public"
else
    VISIBILITY="--private"
fi

echo ""
echo "📤 Creating GitHub repository..."
echo "   Name: $REPO_NAME"
echo "   Description: $REPO_DESC"
echo "   Visibility: $VISIBILITY"
echo ""

# Check if already has remote
if git remote | grep -q "^origin$"; then
    echo "⚠️  Remote 'origin' already exists. Skipping remote setup."
    echo "   To update: git remote set-url origin https://github.com/$(gh api user --jq .login)/$REPO_NAME.git"
else
    # Create repository
    gh repo create "$REPO_NAME" $VISIBILITY --description "$REPO_DESC" --source=. --remote=origin --push
    
    echo ""
    echo "✅ Repository created successfully!"
    echo ""
    echo "🔗 Repository URL: https://github.com/$(gh api user --jq .login)/$REPO_NAME"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Update README.md with your GitHub username"
    echo "   2. Deploy to Vercel: https://vercel.com/new"
    echo "   3. Deploy API to Railway: https://railway.app"
    echo "   4. Configure Cloudflare DNS"
    echo ""
    echo "   See QUICK_START.md for detailed instructions"
fi

