#!/bin/bash
# Script to set up git and push to existing GitHub repository

set -e

echo "🚀 Setting up SupplierSync for GitHub"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "⚠️  GitHub CLI not found. Continuing with manual setup..."
    USE_GH=false
else
    USE_GH=true
fi

# Get repository URL
read -p "Enter your GitHub repository URL (e.g., https://github.com/username/suppliersync): " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "❌ Repository URL is required"
    exit 1
fi

# Clean up URL - remove trailing .git, whitespace, and fix common typos
REPO_URL=$(echo "$REPO_URL" | sed 's/\.git$//' | sed 's/^h*https/http/' | sed 's/^h*http/https/' | xargs)

# Extract username and repo name from URL
if [[ $REPO_URL =~ github\.com/([^/]+)/([^/]+) ]]; then
    GITHUB_USER="${BASH_REMATCH[1]}"
    REPO_NAME="${BASH_REMATCH[2]}"
    REPO_NAME="${REPO_NAME%.git}"  # Remove .git if present
else
    echo "❌ Invalid GitHub URL format. Expected: https://github.com/username/repo"
    echo "   You entered: $REPO_URL"
    exit 1
fi

echo ""
echo "📦 Repository: $GITHUB_USER/$REPO_NAME"
echo ""

# Check if already in a git repo
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git branch -M main
else
    echo "✅ Git repository already initialized"
fi

# Check current remote
if git remote | grep -q "^origin$"; then
    CURRENT_REMOTE=$(git remote get-url origin 2>/dev/null || echo "none")
    echo "⚠️  Remote 'origin' already exists: $CURRENT_REMOTE"
    
    # Check if URL is malformed (has hhttps or similar)
    if echo "$CURRENT_REMOTE" | grep -q "^h"; then
        echo "🔧 Detected malformed URL (starts with 'h'). Fixing automatically..."
        git remote set-url origin "$REPO_URL"
        echo "✅ Fixed and updated remote URL"
    else
        read -p "Update remote URL? (y/n): " UPDATE_REMOTE
        if [ "$UPDATE_REMOTE" = "y" ] || [ "$UPDATE_REMOTE" = "Y" ]; then
            git remote set-url origin "$REPO_URL"
            echo "✅ Updated remote URL"
        else
            echo "ℹ️  Keeping existing remote"
        fi
    fi
else
    echo "🔗 Adding remote repository..."
    git remote add origin "$REPO_URL"
    echo "✅ Remote added"
fi

# Verify remote was set correctly
echo ""
echo "🔍 Verifying remote configuration..."
git remote -v
echo ""

# Check if there are uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo ""
    echo "📝 Staging and committing changes..."
    git add .
    
    # Check if this is the first commit
    if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
        COMMIT_MSG="Initial commit: Multi-Agent AI Orchestrator with security, testing, and documentation"
    else
        read -p "Enter commit message (or press Enter for default): " COMMIT_MSG
        COMMIT_MSG=${COMMIT_MSG:-"Update: Multi-Agent AI Orchestrator"}
    fi
    
    git commit -m "$COMMIT_MSG"
    echo "✅ Changes committed"
else
    echo "✅ No uncommitted changes"
fi

# Push to GitHub
echo ""
echo "📤 Pushing to GitHub..."
read -p "Push to GitHub now? (y/n, default: y): " PUSH_NOW
PUSH_NOW=${PUSH_NOW:-y}

if [ "$PUSH_NOW" = "y" ] || [ "$PUSH_NOW" = "Y" ]; then
    # Check if main branch exists on remote
    if git ls-remote --heads origin main >/dev/null 2>&1; then
        echo "⚠️  Remote 'main' branch already exists"
        read -p "Pull and merge first? (y/n): " PULL_FIRST
        if [ "$PULL_FIRST" = "y" ] || [ "$PULL_FIRST" = "Y" ]; then
            git pull origin main --allow-unrelated-histories || true
        fi
        echo "📤 Pushing to main..."
        git push -u origin main
    else
        echo "📤 Pushing to main (first push)..."
        git push -u origin main
    fi
    echo ""
    echo "✅ Successfully pushed to GitHub!"
else
    echo "ℹ️  Skipping push. Run 'git push -u origin main' when ready."
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "🔗 Repository URL: https://github.com/$GITHUB_USER/$REPO_NAME"
echo ""
echo "📝 Next steps:"
echo "   1. Update README.md with your GitHub username (replace YOUR_USERNAME)"
echo "   2. Deploy dashboard to Vercel: https://vercel.com/new"
echo "   3. Deploy API to Railway: https://railway.app"
echo "   4. Configure Cloudflare DNS"
echo ""
echo "   See QUICK_START.md for detailed deployment instructions"
