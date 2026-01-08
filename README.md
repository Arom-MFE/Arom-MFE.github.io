# Website Deployment Package

This folder contains the complete, latest version of the website ready for GitHub Pages deployment.

## 📁 Contents

### Root Files
- `index.html` - Main homepage
- `styles.css` - Website stylesheet
- `script.js` - JavaScript functionality
- `IMG_9918.jpg` - Profile picture
- `RESUME (2).pdf` - Resume/CV

### Project Files (Root Directory)
All project pages and related PDFs in the root directory:
- `project-tlt-analysis.html` - TLT Time-Series Analysis project page
- `project-banking-competition.html` - Banking Competition project page
- `project-credit-card-default.html` - Credit Card Delinquency project page
- `TLT.pdf` - TLT project PDF
- `CreditCard_DR.pdf` - Credit Card project PDF
- `Banking_Competition_EU copy.pdf` - Banking Competition project PDF

## 🚀 Deployment

### Quick Deploy

```bash
./deploy-to-github.sh
```

This will:
1. Initialize git repository (if needed)
2. Connect to GitHub repository
3. Add all files
4. Commit changes
5. Push to GitHub Pages

### GitHub Repository
- **Repo**: `Arom-MFE/Arom-MFE.github.io`
- **Branch**: `main`
- **Live URL**: https://arom-mfe.github.io/

## 📝 Authentication

When prompted for credentials:
- **Username**: Your GitHub username
- **Password**: Use a Personal Access Token (create at https://github.com/settings/tokens)
  - Select scope: `repo` (Full control of private repositories)

## 🔄 Update Process

1. Make changes in `/Users/alexanderrom/Desktop/web/`
2. Run sync script: `cd /Users/alexanderrom/Desktop/web && ./sync-to-github-folder.sh`
3. Deploy: `cd github && ./deploy-to-github.sh`

---

**Last updated**: This folder contains the latest version of all website files.

