# 🚀 PUSH YOUR DATA TO GITHUB - DO THIS NOW

**5-Minute Quick Start**

---

## STEP 1: Create GitHub Repo (2 min)

1. Go to https://github.com/new
2. **Repository name**: `supply-chain`  
3. **Description**: Supply chain control tower
4. **Public** (so Databricks can access it)
5. Click **Create Repository**

📌 **Copy this URL:**
```
https://github.com/YOUR_USERNAME/supply-chain.git
```

---

## STEP 2: Push Your Project (3 min)

Open **PowerShell** and run these commands:

```powershell
# Navigate to your project
cd "C:\Users\vthek\OneDrive\Documents\supply chain"

# Initialize git
git init

# Configure git (one-time)
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# Add all files
git add .

# Create commit
git commit -m "Initial commit: Supply chain control tower with data"

# Add GitHub remote (REPLACE YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/supply-chain.git

# Push to GitHub (this will ask for credentials)
git branch -M main
git push -u origin main
```

**If asked for password:**
- Use your GitHub Personal Access Token (not your password)
- Or setup SSH key (easier for future)

---

## STEP 3: Verify on GitHub (0.5 min)

Visit:
```
https://github.com/YOUR_USERNAME/supply-chain/tree/main/data/raw
```

You should see all 10 CSV files! ✅

---

## ✨ WHAT DATABRICKS WILL READ

Once files are on GitHub, Databricks will use these URLs:

```
https://raw.githubusercontent.com/YOUR_USERNAME/supply-chain/main/data/raw/production_2026_04_07.csv
https://raw.githubusercontent.com/YOUR_USERNAME/supply-chain/main/data/raw/shipments_2026_04_07.csv
https://raw.githubusercontent.com/YOUR_USERNAME/supply-chain/main/data/raw/quality_2026_04_07.csv
https://raw.githubusercontent.com/YOUR_USERNAME/supply-chain/main/data/raw/inventory_2026_04_07.csv
https://raw.githubusercontent.com/YOUR_USERNAME/supply-chain/main/data/raw/suppliers_2026_04_07.csv
```

---

## 🔄 DAILY UPDATES (Automated)

Each day, just do:

```powershell
cd "C:\Users\vthek\OneDrive\Documents\supply chain"

# Generate today's data
python scripts/generate_daily_data.py

# Push to GitHub
git add data/raw/
git commit -m "Data: $(Get-Date -Format 'yyyy-MM-dd')"
git push origin main
```

Or use GitHub Actions (see GITHUB_AUTOMATION.md)

---

## 📝 THEN IN DATABRICKS

1. Update Bronze notebook with your GitHub username:
   ```python
   GITHUB_USERNAME = "YOUR_USERNAME"  # ← Change this
   ```

2. Paste the updated Bronze notebook code from earlier

3. Run it - it will:
   - Read from your GitHub URLs
   - Parse CSV files
   - Write to Databricks Delta tables

---

## 🆘 TROUBLESHOOTING

### "fatal: not a git repository"
```
You need to: cd "C:\Users\vthek\OneDrive\Documents\supply chain" first
```

### "Permission denied" or authentication error
```
Use GitHub Personal Access Token:
1. Go to github.com → Settings → Developer settings → Personal access tokens
2. Generate new token (select: repo, workflow)
3. Copy token
4. When git asks for password, paste this token
```

### "fatal: could not read Username"
```
Setup SSH key (1-time):
ssh-keygen -t ed25519 -C "your@email.com"
# Add ~/.ssh/id_ed25519.pub to GitHub SSH Keys
# Then use SSH URL instead:
git remote add origin git@github.com:YOUR_USERNAME/supply-chain.git
```

### Files don't appear on GitHub
```
1. Check: git remote -v (should show your repo URL)
2. Check: git status (should show nothing to commit)
3. Check: https://github.com/YOUR_USERNAME/supply-chain/tree/main/data/raw
```

---

## ✅ CHECKLIST

```
☐ Created GitHub repository (supply-chain)
☐ Copied repo URL
☐ Ran: git init
☐ Ran: git config (user name/email)
☐ Ran: git add .
☐ Ran: git commit -m "Initial commit..."
☐ Ran: git remote add origin https://github.com/YOUR_USERNAME/supply-chain.git
☐ Ran: git push -u origin main
☐ Verified files on GitHub (browse tree/main/data/raw)
☐ Updated Bronze notebook with your GitHub username
```

---

## 🎯 NEXT STEPS

1. **Do this**: Push to GitHub (5 min)
2. **Then**: Go to GITHUB_TO_DATABRICKS.md
3. **Then**: Setup Databricks Bronze notebook
4. **Then**: Run Bronze notebook (reads from GitHub URLs)

---

**Your GitHub data URL will be:**
```
https://raw.githubusercontent.com/YOUR_USERNAME/supply-chain/main/data/raw/
```

**Remember to replace** `YOUR_USERNAME` **with your actual GitHub username!**

---

Time to do this: **5 minutes** ⏱️

Let's go! 🚀
