#!/bin/bash
# Deploy complete website to GitHub Pages
# This script deploys the entire github folder to https://arom-mfe.github.io/

cd /Users/alexanderrom/Desktop/web/github

echo "🚀 Deploying Website to GitHub Pages"
echo "======================================"
echo "Repository: Arom-MFE/Arom-MFE.github.io"
echo "Branch: main"
echo "Site URL: https://arom-mfe.github.io/"
echo ""

# Initialize git if needed
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    git branch -M main
fi

# Set remote
if ! git remote get-url origin &>/dev/null; then
    echo "🔗 Adding remote repository..."
    git remote add origin https://github.com/Arom-MFE/Arom-MFE.github.io.git
else
    git remote set-url origin https://github.com/Arom-MFE/Arom-MFE.github.io.git
fi

# Add all files
echo "📝 Adding all files..."
git add .

# Check if there are changes
if git diff --staged --quiet && git diff --quiet HEAD; then
    echo "ℹ️  No changes detected. Everything is up to date!"
    exit 0
fi

# Commit
echo "💾 Committing changes..."
git commit -m "Deploy site update - $(date '+%Y-%m-%d %H:%M:%S')"

# Push to GitHub
echo ""
echo "⬆️  Pushing to GitHub (you'll be prompted for credentials if needed)..."
echo ""
git push -u origin main --force

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    echo "Your website will be live at:"
    echo "   https://arom-mfe.github.io/"
    echo ""
    echo "Note: It may take 1-2 minutes for GitHub Pages to update."
else
    echo ""
    echo "❌ Deployment failed. Check your credentials."
    echo ""
    echo "Authentication help:"
    echo "  - Username: Your GitHub username"
    echo "  - Password: Use a Personal Access Token (not password)"
    echo "  - Create token at: https://github.com/settings/tokens"
    echo ""
fi

