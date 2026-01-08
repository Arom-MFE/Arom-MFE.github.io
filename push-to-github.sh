#!/bin/bash
# Push website to GitHub Pages

cd /Users/alexanderrom/Desktop/web

echo "🚀 Pushing to GitHub..."
echo "Repository: Arom-MFE/Arom-MFE.github.io"
echo "Branch: main"
echo ""

# Check if remote exists
if ! git remote get-url origin &>/dev/null; then
    echo "Setting up remote..."
    git remote add origin https://github.com/Arom-MFE/Arom-MFE.github.io.git
fi

# Ensure we're on main branch
git branch -M main

# Push to GitHub
echo "Pushing to GitHub (you'll be prompted for credentials)..."
git push -u origin main

echo ""
echo "✅ If successful, your site will be live at:"
echo "   https://arom-mfe.github.io/"
echo ""
echo "Note: If prompted for credentials:"
echo "  - Username: Your GitHub username"
echo "  - Password: Use a Personal Access Token (not your GitHub password)"
echo "    Create one at: https://github.com/
settings/tokens"
