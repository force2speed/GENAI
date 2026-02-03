# 🚀 GCP Migration Setup Guide
## Setting up Misinformation Detection Backend with New Google Account

---

## 📋 Prerequisites Checklist
- [ ] New Google Account ready
- [ ] Credit/Debit card for GCP billing (free tier available)
- [ ] Backend code downloaded
- [ ] Python 3.11 installed
- [ ] Node.js installed (for BigQuery/Firestore JS modules)

---

## 🎯 Quick Overview
Your backend uses these Google Cloud services:
1. **Cloud Vision API** - Extract text from images/videos
2. **Cloud Speech-to-Text API** - Transcribe audio
3. **Firestore** - Store analysis logs
4. **BigQuery** - Analytics data warehouse
5. **Gemini API** - AI-powered misinformation detection

---

## 🔧 Step-by-Step Setup (Web Console Method)

### **Step 1: Create GCP Project** (5 mins)
1. Go to: https://console.cloud.google.com/
2. Sign in with your new Google account
3. Click on the project dropdown (top navigation bar)
4. Click **"New Project"**
5. Enter project name: `misinformation-detector` (or your choice)
6. Click **"Create"**
7. Wait for project creation (30 seconds)
8. **📝 Note down your Project ID** (shown on the dashboard)

### **Step 2: Enable Billing** (5 mins)
1. Go to: https://console.cloud.google.com/billing
2. Click **"Link a billing account"**
3. Follow the prompts to add payment method
4. ✨ Google provides $300 free credits for new accounts!

### **Step 3: Enable Required APIs** (3 mins each)
Go to https://console.cloud.google.com/apis/library and search & enable:

1. **Cloud Vision API**
   - Search: "Cloud Vision API"
   - Click on it
   - Click **"Enable"**

2. **Cloud Speech-to-Text API**
   - Search: "Cloud Speech-to-Text API"
   - Click **"Enable"**

3. **Cloud Firestore API**
   - Search: "Cloud Firestore API"
   - Click **"Enable"**

4. **BigQuery API**
   - Search: "BigQuery API"
   - Click **"Enable"**

### **Step 4: Create Service Account** (7 mins)
1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Click **"Create Service Account"**
3. Fill in:
   - **Name:** `misinformation-detector`
   - **Description:** `Service account for misinformation detection backend`
4. Click **"Create and Continue"**

5. **Grant Roles** - Add these 4 roles one by one:
   - Click "Select a role"
   - Search and add:
     - ✅ `Cloud Vision AI Service Agent`
     - ✅ `Cloud Speech Administrator`
     - ✅ `Cloud Datastore User`
     - ✅ `BigQuery Data Editor`
   - Click **"Continue"**
   - Click **"Done"**

### **Step 5: Download Service Account Key** (2 mins)
1. You should see your service account listed
2. Click on the **email** of the service account (looks like: `misinformation-detector@project-id.iam.gserviceaccount.com`)
3. Go to **"Keys"** tab
4. Click **"Add Key"** → **"Create new key"**
5. Select **JSON** format
6. Click **"Create"**
7. 📥 A file will download (e.g., `project-id-abc123.json`)
8. **Rename it to `key.json`**
9. **Move it to your backend folder:**
   ```
   C:\Users\dhruv\Desktop\PERSONAL DATA\PROJECTS\GENAI-combating Misinformation\backend\key.json
   ```

### **Step 6: Initialize Firestore Database** (3 mins)
1. Go to: https://console.cloud.google.com/firestore
2. Click **"Create Database"**
3. Select **"Firestore Native Mode"**
4. Choose location: **`nam5 (United States)`** or closest to you
5. Click **"Create Database"**
6. Wait for initialization (~1 minute)

### **Step 7: Setup BigQuery Dataset & Table** (5 mins)

**Create Dataset:**
1. Go to: https://console.cloud.google.com/bigquery
2. In the Explorer panel (left side), click on your project name
3. Click the **three dots (⋮)** next to your project
4. Click **"Create dataset"**
5. Fill in:
   - **Dataset ID:** `misinfo_logs`
   - **Location:** `US (multiple regions in United States)`
6. Click **"Create Dataset"**

**Create Table:**
1. Click on your newly created `misinfo_logs` dataset
2. Click the **three dots (⋮)** next to it
3. Click **"Create table"**
4. Fill in:
   - **Source:** Empty table
   - **Table name:** `analysis`
   - **Schema:** Click "Add field" for each:
     
     | Field name | Type | Mode |
     |------------|------|------|
     | timestamp | TIMESTAMP | NULLABLE |
     | type | STRING | NULLABLE |
     | file | STRING | NULLABLE |
     | verdict | STRING | NULLABLE |
     | text | STRING | NULLABLE |
     | id | STRING | NULLABLE |
     
5. Click **"Create Table"**

### **Step 8: Get Gemini API Key** (3 mins)
1. Go to: https://aistudio.google.com/app/apikey
2. Sign in with the same Google account
3. Click **"Create API Key"**
4. Select your GCP project from dropdown
5. Click **"Create API key in existing project"**
6. 📋 **Copy the API key** - it looks like: `AIzaSyC-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
7. ⚠️ **Save it securely** - you won't see it again!

### **Step 9: Configure Environment Variables** (5 mins)

**Option A: Using .env file (Recommended for Development)**

1. Create a file named `.env` in your backend folder:
   ```
   C:\Users\dhruv\Desktop\PERSONAL DATA\PROJECTS\GENAI-combating Misinformation\backend\.env
   ```

2. Add these lines (replace with your actual values):
   ```env
   GOOGLE_APPLICATION_CREDENTIALS=C:/Users/dhruv/Desktop/PERSONAL DATA/PROJECTS/GENAI-combating Misinformation/backend/key.json
   GEMINI_API_KEY=AIzaSyC-your-actual-gemini-api-key-here
   GCP_PROJECT_ID=your-project-id-here
   ```

3. Install python-dotenv:
   ```bash
   pip install python-dotenv
   ```

**Option B: System Environment Variables (Windows)**

1. Search for "Environment Variables" in Windows Start menu
2. Click "Edit the system environment variables"
3. Click "Environment Variables" button
4. Under "User variables", click "New" for each:
   - **Variable name:** `GOOGLE_APPLICATION_CREDENTIALS`
     **Value:** `C:\Users\dhruv\Desktop\PERSONAL DATA\PROJECTS\GENAI-combating Misinformation\backend\key.json`
   
   - **Variable name:** `GEMINI_API_KEY`
     **Value:** Your Gemini API key
   
   - **Variable name:** `GCP_PROJECT_ID`
     **Value:** Your project ID

5. Click OK and **restart your terminal/IDE**

### **Step 10: Install Dependencies** (5 mins)

```bash
cd "C:\Users\dhruv\Desktop\PERSONAL DATA\PROJECTS\GENAI-combating Misinformation\backend"

# Install Python packages
pip install -r requirements.txt

# Install Node.js packages (for Firestore/BigQuery)
npm install
```

### **Step 11: Verify Setup** (2 mins)

Run the verification script:
```bash
python verify_setup.py
```

This will check:
- ✅ Service account key file
- ✅ Environment variables
- ✅ Python dependencies
- ✅ GCP service connections

### **Step 12: Test the Application** (2 mins)

```bash
python app.py
```

Expected output:
```
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
```

Test with curl or Postman:
```bash
curl http://localhost:5000/
```

---

## 🔐 Security Best Practices

1. **Never commit `key.json` to Git**
   - Already in `.gitignore`? Check with: `cat .gitignore`
   - If not, add it: `echo "key.json" >> .gitignore`

2. **Rotate keys regularly**
   - Delete old service account keys
   - Create new ones every 90 days

3. **Use environment variables**
   - Never hardcode credentials in code
   - Use Secret Manager for production

4. **Limit service account permissions**
   - Only grant necessary roles
   - Follow principle of least privilege

---

## 🐛 Troubleshooting

### Issue: "API not enabled"
**Solution:** Go back to Step 3 and ensure all APIs are enabled

### Issue: "Permission denied"
**Solution:** Check service account roles in Step 4, add missing roles

### Issue: "Quota exceeded"
**Solution:** Check your GCP billing and quotas: https://console.cloud.google.com/iam-admin/quotas

### Issue: "Module not found"
**Solution:** 
```bash
pip install -r requirements.txt
npm install
```

### Issue: "Invalid API key" (Gemini)
**Solution:** Regenerate key at https://aistudio.google.com/app/apikey

---

## 📊 Monitor Usage & Costs

1. **APIs & Services Dashboard:**
   https://console.cloud.google.com/apis/dashboard

2. **Billing Dashboard:**
   https://console.cloud.google.com/billing

3. **Free Tier Limits:**
   - Vision API: 1,000 requests/month
   - Speech-to-Text: 60 minutes/month
   - Firestore: 1GB storage, 50K reads/day
   - BigQuery: 1TB queries/month

---

## 📚 Additional Resources

- [GCP Free Tier](https://cloud.google.com/free)
- [Cloud Vision API Docs](https://cloud.google.com/vision/docs)
- [Cloud Speech-to-Text Docs](https://cloud.google.com/speech-to-text/docs)
- [Firestore Docs](https://firebase.google.com/docs/firestore)
- [BigQuery Docs](https://cloud.google.com/bigquery/docs)
- [Gemini API Docs](https://ai.google.dev/docs)

---

## ✅ Final Checklist

- [ ] GCP project created
- [ ] Billing enabled
- [ ] All 4 APIs enabled
- [ ] Service account created with 4 roles
- [ ] Service account key downloaded as `key.json`
- [ ] Firestore database initialized
- [ ] BigQuery dataset & table created
- [ ] Gemini API key obtained
- [ ] Environment variables configured
- [ ] Python dependencies installed
- [ ] Node.js dependencies installed
- [ ] Setup verification passed
- [ ] Application running successfully

---

**🎉 Congratulations! Your backend is now set up with the new GCP account!**

For questions or issues, refer to the troubleshooting section or GCP documentation.
