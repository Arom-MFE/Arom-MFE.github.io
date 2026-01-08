# Deploying to GitHub Pages

## Step 1: Initialize Git Repository (if not already done)

```bash
cd /Users/alexanderrom/Desktop/web
git init
```

## Step 2: Create .gitignore file

Create a `.gitignore` file to exclude unnecessary files:

```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
.venv/
venv/
.DS_Store
```

## Step 3: Add all files and commit

```bash
git add .
git commit -m "Initial commit - portfolio website"
```

## Step 4: Create GitHub Repository

1. Go to https://github.com and log in
2. Click the "+" icon in the top right → "New repository"
3. Name it (e.g., `portfolio` or `website`)
4. **Don't** initialize with README, .gitignore, or license (you already have files)
5. Click "Create repository"

## Step 5: Add GitHub as Remote and Push

```bash
# Replace YOUR_USERNAME and YOUR_REPO_NAME with your actual GitHub username and repo name
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## Step 6: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** (top menu)
3. Scroll down to **Pages** in the left sidebar
4. Under **Source**, select:
   - Branch: `main` (or `master`)
   - Folder: `/ (root)`
5. Click **Save**
6. Your site will be available at: `https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/`

## Step 7: Update after changes

After making changes, push them:

```bash
git add .
git commit -m "Description of your changes"
git push
```

GitHub Pages will automatically update within a few minutes.

