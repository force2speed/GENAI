# Quick Setup Guide for Windows

## Current Status:
✅ Python 3.11.4 detected
✅ BigQuery console open (genai-486310)
⏳ Need to complete setup

## Next Steps (30 minutes total):

### Step 1: Complete GCP Setup in Browser (15 mins)

**In BigQuery Console (already open):**
1. Create dataset `misinfo_logs` 
2. Create table `analysis`
   - Follow instructions in BIGQUERY_SETUP.md

**Then visit these pages:**

1. **Enable APIs** (5 mins)
   - https://console.cloud.google.com/apis/library?project=genai-486310
   - Enable: Cloud Vision, Cloud Speech, Firestore, BigQuery APIs

2. **Create Service Account** (5 mins)
   - https://console.cloud.google.com/iam-admin/serviceaccounts?project=genai-486310
   - Name: misinformation-detector
   - Roles: Vision Admin, Speech Admin, Datastore User, BigQuery Data Editor
   - Download key.json to this folder

3. **Get Gemini API Key** (3 mins)
   - https://aistudio.google.com/app/apikey
   - Create API key → Copy it

### Step 2: Configure Environment (5 mins)

After downloading key.json, create .env file:

```cmd
# In Git Bash, run:
cd "C:\Users\dhruv\Desktop\PERSONAL DATA\PROJECTS\GENAI-combating Misinformation\backend"

# Create .env file
cat > .env << 'EOF'
GOOGLE_APPLICATION_CREDENTIALS=C:/Users/dhruv/Desktop/PERSONAL DATA/PROJECTS/GENAI-combating Misinformation/backend/key.json
GEMINI_API_KEY=paste-your-gemini-api-key-here
GCP_PROJECT_ID=genai-486310
EOF
```

### Step 3: Install Dependencies (10 mins)

```bash
# Install Python packages
py -m pip install -r requirements.txt

# Install Node.js packages
npm install
```

### Step 4: Test Setup (2 mins)

```bash
# Run verification (use 'py' not 'python')
py verify_setup.py

# If all checks pass, start the app:
py app.py
```

## Common Issues:

**Issue: "python command not found"**
Solution: Use `py` instead:
```bash
py script.py         # Instead of: python script.py
py -m pip install    # Instead of: pip install
```

**Issue: "Module not found"**
Solution:
```bash
py -m pip install -r requirements.txt
```

**Issue: "GOOGLE_APPLICATION_CREDENTIALS not found"**
Solution: Make sure .env file exists and key.json is in the backend folder

## Quick Commands Reference:

```bash
# Check Python version
py --version

# Install packages
py -m pip install package-name

# Run scripts
py script_name.py

# Check if key.json exists
ls -l key.json

# Check if .env exists
cat .env
```

## Your Project Details:

- **Project ID:** genai-486310
- **Old Project ID:** solid-future-471019-j5
- **Backend Folder:** C:\Users\dhruv\Desktop\PERSONAL DATA\PROJECTS\GENAI-combating Misinformation\backend
- **Python:** 3.11.4 (use `py` command)

## Files You Need:

1. ✅ requirements.txt - Already present
2. ✅ package.json - Already present  
3. ✅ app.py - Already present
4. ⏳ key.json - Download from GCP Console
5. ⏳ .env - Create after getting API key

## Progress Tracker:

```
[✅] 1. Python installed (3.11.4)
[✅] 2. GCP project created (genai-486310)
[⏳] 3. BigQuery dataset creation (IN PROGRESS)
[ ] 4. APIs enabled
[ ] 5. Service account created
[ ] 6. key.json downloaded
[ ] 7. Gemini API key obtained
[ ] 8. .env file created
[ ] 9. Dependencies installed
[ ] 10. Verification passed
[ ] 11. App running
```

Save this file for reference!
