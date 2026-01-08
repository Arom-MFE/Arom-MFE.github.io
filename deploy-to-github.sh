#!/bin/bash
# Deploy github folder to GitHub Pages

cd /Users/alexanderrom/Desktop/web/github

echo "🚀 Deploying to GitHub Pages..."
echo "Repository: Arom-MFE/Arom-MFE.github.io"
echo ""

# Initialize git if needed
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
    git branch -M main
fi

# Set remote
if ! git remote get-url origin &>/dev/null; then
    git remote add origin https://github.com/Arom-MFE/Arom-MFE.github.io.git
else
    git remote set-url origin https://github.com/Arom-MFE/Arom-MFE.github.io.git
fi

# Add all files
echo "Adding files..."
git add .

# Commit
echo "Committing changes..."
git commit -m "Deploy site update" || echo "No changes to commit"

# Push to GitHub
echo "Pushing to GitHub (you'll be prompted for credentials)..."
git push -u origin main --force

echo ""
echo "✅ If successful, your site will be live at:"
echo "   https://arom-mfe.github.io/"
echo ""
echo "Note: If prompted for credentials:"
echo "  - Username: Your GitHub username"
echo "  - Password: Use a Personal Access Token"
echo "    Create at: https://github.com/settings/tokens"
