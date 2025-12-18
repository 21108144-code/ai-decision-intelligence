# GitHub Setup Guide

## Recommended Repository Name

```
ai-decision-intelligence
```

**Alternative names:**
- `enterprise-decision-ai`
- `multi-agent-decision-platform`
- `langgraph-decision-intelligence`

---

## Step-by-Step Git Commands

### 1. Initial Setup (First Time Only)

Open PowerShell/Terminal in your project folder:

```powershell
# Navigate to project folder
cd "c:\Langraph project"

# Initialize Git repository
git init

# Configure your identity (use your actual info)
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### 2. Create .gitignore (Already exists, but verify)

Make sure these are ignored:
```
.env
__pycache__/
*.pyc
venv/
node_modules/
*.db
.DS_Store
debug.log
```

### 3. First Commit (Main Branch)

```powershell
# Add all files
git add .

# Create first commit
git commit -m "Initial commit: AI Decision Intelligence Platform with multi-agent architecture"

# Rename branch to 'main' (modern convention)
git branch -M main
```

### 4. Create GitHub Repository

**Option A: Via GitHub Website**
1. Go to [github.com/new](https://github.com/new)
2. Repository name: `ai-decision-intelligence`
3. Description: `Multi-agent AI system for enterprise decision support using LangGraph, FastAPI, and React`
4. Make it **Public** (for portfolio)
5. Do **NOT** initialize with README (we have one)
6. Click "Create repository"

**Option B: Via GitHub CLI (if installed)**
```powershell
gh repo create ai-decision-intelligence --public --description "Multi-agent AI system for enterprise decision support"
```

### 5. Connect Local to GitHub

After creating the repo on GitHub:

```powershell
# Add remote origin (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/ai-decision-intelligence.git

# Push to main branch
git push -u origin main
```

### 6. Create Development/Testing Branch

Following real-world Git workflow (Git Flow):

```powershell
# Create and switch to develop branch
git checkout -b develop

# Push develop branch to GitHub
git push -u origin develop
```

---

## Branch Strategy Explained

### Main Branches

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready code. Always stable. |
| `develop` | Integration branch for features. Testing happens here. |

### Feature Branches (Optional)

When adding new features:

```powershell
# Create feature branch from develop
git checkout develop
git checkout -b feature/add-streaming-responses

# Work on your feature...
# git add .
# git commit -m "Add streaming responses to API"

# Merge back to develop when done
git checkout develop
git merge feature/add-streaming-responses
git push origin develop

# Delete feature branch
git branch -d feature/add-streaming-responses
```

### Hotfix Branches (For urgent fixes)

```powershell
# Create from main
git checkout main
git checkout -b hotfix/fix-critical-bug

# Fix and commit
git add .
git commit -m "Fix critical API error"

# Merge to both main and develop
git checkout main
git merge hotfix/fix-critical-bug
git push origin main

git checkout develop
git merge hotfix/fix-critical-bug
git push origin develop
```

---

## Complete Workflow Summary

```
1. Initialize and push to main
         │
         ▼
    ┌─────────┐
    │  main   │ ← Production (stable)
    └────┬────┘
         │
    git checkout -b develop
         │
         ▼
    ┌─────────┐
    │ develop │ ← Testing/Integration
    └────┬────┘
         │
    git checkout -b feature/xyz
         │
         ▼
    ┌─────────────┐
    │ feature/xyz │ ← New features
    └─────────────┘
```

---

## Quick Reference Commands

```powershell
# Check current branch
git branch

# See all branches (local + remote)
git branch -a

# Switch branches
git checkout main
git checkout develop

# Pull latest changes
git pull origin main
git pull origin develop

# See commit history
git log --oneline -10

# Check status
git status

# Push changes
git push origin main
git push origin develop
```

---

## Run These Commands Now

Copy and paste these commands in order:

```powershell
# 1. Navigate to project
cd "c:\Langraph project"

# 2. Initialize git
git init

# 3. Add all files
git add .

# 4. First commit
git commit -m "Initial commit: AI Decision Intelligence Platform with multi-agent architecture"

# 5. Rename to main
git branch -M main

# 6. Add remote (REPLACE YOUR_USERNAME!)
git remote add origin https://github.com/YOUR_USERNAME/ai-decision-intelligence.git

# 7. Push main
git push -u origin main

# 8. Create develop branch
git checkout -b develop

# 9. Push develop
git push -u origin develop

# 10. Switch back to main
git checkout main
```

---

## After Pushing

Your GitHub repo will have:
- ✅ `main` branch - stable production code
- ✅ `develop` branch - for testing/development
- ✅ Professional README with badges
- ✅ Complete documentation in `/docs`

Share your portfolio link:
```
https://github.com/YOUR_USERNAME/ai-decision-intelligence
```

---

## Troubleshooting

### "Remote origin already exists"
```powershell
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/ai-decision-intelligence.git
```

### "Failed to push - rejected"
```powershell
git pull origin main --allow-unrelated-histories
git push origin main
```

### Check if .env is ignored
```powershell
git status
# .env should NOT appear in the list
```

---

Good luck! 🚀
