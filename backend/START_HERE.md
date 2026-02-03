# 🚀 IMMEDIATE ACTION PLAN
## Complete Your GCP Migration in 30 Minutes

**Current Status:**
- ✅ Python 3.11.4 installed (use `py` command)
- ✅ New GCP Project created: `genai-486310`
- ✅ BigQuery console open
- ⏳ Waiting for setup completion

---

## 📋 Complete These 5 Steps NOW:

### **STEP 1: BigQuery Setup (5 mins)** 
**You're already here - finish this first!**

In the BigQuery console:
1. Click the **⋮** next to `genai-486310` project
2. Select **"Create dataset"**
3. Enter:
   - Dataset ID: `misinfo_logs`
   - Location: `US`
4. Click **CREATE DATASET**
5. Click **⋮** next to `misinfo_logs`
6. Select **"Create table"**
7. Enter:
   - Table name: `analysis`
   - Schema: Add these 6 fields:
     - `timestamp` - TIMESTAMP
     - `type` - STRING
     - `file` - STRING
     - `verdict` - STRING
     - `text` - STRING
     - `id` - STRING
8. Click **CREATE TABLE**

✅ **Done? Continue to Step 2**

---

### **STEP 2: Enable APIs (5 mins)**

Open these links in new tabs and click "Enable" for each:

1. **Cloud Vision API**: 
   https://console.cloud.google.com/apis/library/vision.googleapis.com?project=genai-486310

2. **Cloud Speech-to-Text API**:
   https://console.cloud.google.com/apis/library/speech.googleapis.com?project=genai-486310

3. **Firestore API**:
   https://console.cloud.google.com/apis/library/firestore.googleapis.com?project=genai-486310

4. **BigQuery API** (should already be enabled):
   https://console.cloud.google.com/apis/library/bigquery.googleapis.com?project=genai-486310

✅ **Done? Continue to Step 3**

---

### **STEP 3: Initialize Firestore (2 mins)**

1. Go to: https://console.cloud.google.com/firestore?project=genai-486310
2. Click **"Create Database"**
3. Select **"Native Mode"**
4. Choose location: `nam5 (United States)`
5. Click **"Create Database"**

✅ **Done? Continue to Step 4**

---

### **STEP 4: Create Service Account & Download Key (7 mins)**

1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts?project=genai-486310

2. Click **"Create Service Account"**

3. Fill in:
   - Name: `misinformation-detector`
   - Description: `Service account for backend`

4. Click **"Create and Continue"**

5. Add these 4 roles (click "Select a role" for each):
   - `Cloud Vision AI Service Agent`
   - `Cloud Speech Administrator`
   - `Cloud Datastore User`
   - `BigQuery Data Editor`

6. Click **"Continue"** → **"Done"**

7. Click on the **email** of your new service account

8. Go to **"Keys"** tab

9. Click **"Add Key"** → **"Create new key"**

10. Select **JSON** format

11. Click **"Create"**

12. File downloads → **Rename it to `key.json`**

13. **Move `key.json` to:**
    ```
    C:\Users\dhruv\Desktop\PERSONAL DATA\PROJECTS\GENAI-combating Misinformation\backend\key.json
    ```

✅ **Done? Continue to Step 5**

---

### **STEP 5: Get Gemini API Key (3 mins)**

1. Go to: https://aistudio.google.com/app/apikey

2. Click **"Create API Key"**

3. Select your project: `genai-486310`

4. Click **"Create API key in existing project"**

5. **Copy the API key** (starts with `AIzaSy...`)

6. **Save it somewhere** - you'll need it in the next command

✅ **Done? Continue to Local Setup**

---

## 💻 LOCAL SETUP (In Git Bash - 10 mins)

### Run these commands in order:

```bash
# 1. Navigate to backend folder
cd "C:\Users\dhruv\Desktop\PERSONAL DATA\PROJECTS\GENAI-combating Misinformation\backend"

# 2. Verify key.json exists
ls -l key.json
# You should see: key.json with a recent date

# 3. Create .env file with your Gemini API key
cat > .env << 'EOF'
GOOGLE_APPLICATION_CREDENTIALS=C:/Users/dhruv/Desktop/PERSONAL DATA/PROJECTS/GENAI-combating Misinformation/backend/key.json
GEMINI_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
GCP_PROJECT_ID=genai-486310
EOF

# 4. Edit .env to add your actual Gemini API key
nano .env
# OR open in VS Code: code .env
# Replace PASTE_YOUR_ACTUAL_API_KEY_HERE with your actual key

# 5. Run the automated setup script
bash setup.sh
```

The `setup.sh` script will:
- ✅ Verify Python and Node.js
- ✅ Check key.json validity
- ✅ Install all Python dependencies
- ✅ Install all Node.js dependencies
- ✅ Run verification tests
- ✅ Show you next steps

---

## 🎯 VERIFY & RUN

After `setup.sh` completes successfully:

```bash
# Test the setup
py verify_setup.py

# If all checks pass ✅, start the app:
py app.py
```

**Expected output:**
```
Enhanced Fake Information Detection API v2.0
===========================================
 * Running on http://127.0.0.1:5000
```

---

## 📝 Quick Reference

**Your Project:**
- Project ID: `genai-486310`
- Old Project: `solid-future-471019-j5`

**Python Command:**
- ❌ Don't use: `python` or `python3`
- ✅ Use: `py`

**Key Files:**
- `key.json` - Service account credentials
- `.env` - API keys and config
- `setup.sh` - Automated setup script
- `verify_setup.py` - Test your setup

**Documentation:**
- `GCP_MIGRATION_GUIDE.md` - Complete guide
- `WINDOWS_SETUP_GUIDE.md` - Windows-specific
- `BIGQUERY_SETUP.md` - BigQuery details
- `SETUP_CHECKLIST.md` - Track progress

---

## ⚡ TL;DR - Ultra Quick Version

1. **In Browser:** Create BigQuery dataset/table, enable APIs, setup Firestore, create service account, download key.json, get Gemini API key
2. **In Terminal:** Move key.json to backend, create .env with API key, run `bash setup.sh`
3. **Test:** Run `py app.py`

**Time:** ~30 minutes total

---

## 🆘 Having Issues?

**"py command not found"**
→ Install Python from python.org

**"key.json not found"**
→ Download from Step 4, move to backend folder

**"Module not found"**
→ Run: `py -m pip install -r requirements.txt`

**"API not enabled"**
→ Go back to Step 2, enable all APIs

**"Invalid API key"**
→ Check .env file, regenerate key from aistudio.google.com

---

## ✅ Success Checklist

```
[ ] BigQuery dataset & table created
[ ] 4 APIs enabled
[ ] Firestore initialized
[ ] Service account created
[ ] key.json downloaded and in backend folder
[ ] Gemini API key obtained
[ ] .env file created with API key
[ ] Python dependencies installed
[ ] Node.js dependencies installed
[ ] verify_setup.py passes all checks
[ ] app.py starts without errors
```

**When all boxes are checked, you're ready to use your backend!** 🎉
