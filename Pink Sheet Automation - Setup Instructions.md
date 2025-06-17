# Pink Sheet Automation - Setup Instructions

## 🚀 **4-Week Simulation Deployment**

### **Step 1: GitHub Repository Setup**

1. **Create new GitHub repository**:
   - Go to GitHub.com
   - Click "New repository"
   - Name: `pink-sheet-automation`
   - Make it **Public** (required for GitHub Actions)
   - Don't initialize with README

2. **Push this code to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/pink-sheet-automation.git
   git branch -M main
   git push -u origin main
   ```

### **Step 2: Netlify Setup**

1. **Get Netlify tokens**:
   - Go to [Netlify.com](https://netlify.com)
   - Sign up/login
   - Go to User Settings → Applications → Personal Access Tokens
   - Generate new token, copy it

2. **Create new Netlify site**:
   - Go to Sites → Add new site → Import from Git
   - Connect to your GitHub repo
   - Get the Site ID from Site Settings → General

### **Step 3: GitHub Secrets Setup**

1. **Go to your GitHub repo**:
   - Settings → Secrets and variables → Actions
   - Click "New repository secret"

2. **Add these secrets**:
   ```
   NETLIFY_AUTH_TOKEN: [your netlify token]
   NETLIFY_SITE_ID: [your netlify site id]
   ```

### **Step 4: Enable GitHub Actions**

1. **In your GitHub repo**:
   - Go to Actions tab
   - Click "I understand my workflows, enable them"
   - The automation will start running daily at 6:00 AM EST

### **Step 5: Manual Test Run**

1. **Trigger first run**:
   - Go to Actions → Pink Sheet Daily Automation
   - Click "Run workflow" → "Run workflow"
   - Watch it execute the first analysis

## 🎯 **What Happens Next**

### **Daily Automation (6:00 AM EST)**:
- ✅ Analyzes 55+ pink sheet stocks
- ✅ Executes $20 trades in top 3 picks  
- ✅ Updates website with results
- ✅ Manages stop-loss/take-profit

### **Weekly Reports (Fridays)**:
- ✅ Comprehensive performance analysis
- ✅ Best/worst trades summary
- ✅ Sector breakdown
- ✅ Recommendations for next week

### **4-Week Results**:
- ✅ Complete simulation data
- ✅ Total return calculations
- ✅ Risk analysis
- ✅ Strategy effectiveness

## 📊 **Monitoring Your Simulation**

- **Live Website**: Updates daily with real results
- **GitHub Actions**: View automation logs
- **Weekly Reports**: Generated in `data/reports/`
- **Performance Data**: Tracked in `data/pink_performance.json`

## ⚠️ **Important Notes**

- **Educational Only**: This is a simulation system
- **No Real Money**: All trades are hypothetical
- **High Risk**: Pink sheets are extremely volatile
- **4-Week Test**: Evaluate before real money

---

**Ready to start your 4-week pink sheet simulation!** 🚀

