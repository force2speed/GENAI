# 📋 GCP Migration Checklist

Copy this checklist and check items off as you complete them!

## 🎯 Phase 1: GCP Project Setup (15 mins)

```
[ ] 1.1 - Logged into console.cloud.google.com with new Google account
[ ] 1.2 - Created new GCP project
[ ] 1.3 - Written down Project ID: _______________________________
[ ] 1.4 - Enabled billing for the project
[ ] 1.5 - Confirmed $300 free credits are active (for new accounts)
```

## 🔌 Phase 2: Enable APIs (15 mins)

```
[ ] 2.1 - Enabled Cloud Vision API
[ ] 2.2 - Enabled Cloud Speech-to-Text API  
[ ] 2.3 - Enabled Cloud Firestore API
[ ] 2.4 - Enabled BigQuery API
[ ] 2.5 - Verified all APIs show "Enabled" status
```

## 👤 Phase 3: Service Account Setup (10 mins)

```
[ ] 3.1 - Created service account: "misinformation-detector"
[ ] 3.2 - Granted role: Cloud Vision AI Service Agent
[ ] 3.3 - Granted role: Cloud Speech Administrator
[ ] 3.4 - Granted role: Cloud Datastore User
[ ] 3.5 - Granted role: BigQuery Data Editor
[ ] 3.6 - Downloaded service account key as JSON
[ ] 3.7 - Renamed file to: key.json
[ ] 3.8 - Moved key.json to backend folder
[ ] 3.9 - Verified key.json contains valid JSON data
```

## 🗄️ Phase 4: Database Setup (10 mins)

### Firestore
```
[ ] 4.1 - Created Firestore database in Native Mode
[ ] 4.2 - Selected region: _______________________________
[ ] 4.3 - Database initialization completed
```

### BigQuery
```
[ ] 4.4 - Created dataset: "misinfo_logs"
[ ] 4.5 - Created table: "analysis"
[ ] 4.6 - Added field: timestamp (TIMESTAMP)
[ ] 4.7 - Added field: type (STRING)
[ ] 4.8 - Added field: file (STRING)
[ ] 4.9 - Added field: verdict (STRING)
[ ] 4.10 - Added field: text (STRING)
[ ] 4.11 - Table created successfully
```

## 🤖 Phase 5: Gemini API Setup (5 mins)

```
[ ] 5.1 - Visited aistudio.google.com/app/apikey
[ ] 5.2 - Created API key in existing project
[ ] 5.3 - Copied API key safely
[ ] 5.4 - API key saved in secure location
```

## ⚙️ Phase 6: Local Environment Setup (10 mins)

```
[ ] 6.1 - Created .env file in backend folder
[ ] 6.2 - Set GOOGLE_APPLICATION_CREDENTIALS in .env
[ ] 6.3 - Set GEMINI_API_KEY in .env
[ ] 6.4 - Set GCP_PROJECT_ID in .env
[ ] 6.5 - Verified .env file is in .gitignore
```

## 📦 Phase 7: Install Dependencies (10 mins)

```
[ ] 7.1 - Ran: pip install -r requirements.txt
[ ] 7.2 - All Python packages installed successfully
[ ] 7.3 - Ran: npm install
[ ] 7.4 - All Node.js packages installed successfully
```

## ✅ Phase 8: Verification (5 mins)

```
[ ] 8.1 - Ran: python verify_setup.py
[ ] 8.2 - key.json check passed ✅
[ ] 8.3 - Environment variables check passed ✅
[ ] 8.4 - Dependencies check passed ✅
[ ] 8.5 - Cloud Vision API connection test passed ✅
[ ] 8.6 - Cloud Speech API connection test passed ✅
[ ] 8.7 - Firestore connection test passed ✅
[ ] 8.8 - BigQuery connection test passed ✅
[ ] 8.9 - Gemini API configuration test passed ✅
```

## 🚀 Phase 9: Application Testing (5 mins)

```
[ ] 9.1 - Ran: python app.py
[ ] 9.2 - Server started without errors
[ ] 9.3 - Server running on port 5000 or 8080
[ ] 9.4 - Can access http://localhost:5000 or 8080
[ ] 9.5 - Tested /analyze-document endpoint
[ ] 9.6 - Tested /analyze-image endpoint
[ ] 9.7 - Application working correctly
```

## 🔐 Phase 10: Security Checklist (5 mins)

```
[ ] 10.1 - key.json is in .gitignore
[ ] 10.2 - .env is in .gitignore
[ ] 10.3 - No credentials hardcoded in any files
[ ] 10.4 - Service account has minimum required permissions
[ ] 10.5 - API keys stored securely
```

---

## 📊 Quick Reference

**Old Project ID:** `solid-future-471019-j5`
**New Project ID:** _______________________________

**Service Account Email:** 
`misinformation-detector@___PROJECT_ID___.iam.gserviceaccount.com`

**Gemini API Key (last 5 chars):** _ _ _ _ _

**APIs Enabled:**
- ✅ Cloud Vision API
- ✅ Cloud Speech-to-Text API
- ✅ Firestore API
- ✅ BigQuery API

**Database Resources:**
- Firestore Database: Native Mode
- BigQuery Dataset: `misinfo_logs`
- BigQuery Table: `analysis`

---

## 🎉 Completion Status

```
Total Steps: 50
Completed: [ ] / 50
Progress: ____%

Status: [ ] Not Started  [ ] In Progress  [ ] Completed
```

---

## 📝 Notes & Issues

Use this section to track any issues or important notes:

```
Issue 1: 
_________________________________________________________________________

Resolution: 
_________________________________________________________________________


Issue 2:
_________________________________________________________________________

Resolution:
_________________________________________________________________________
```

---

## 🔗 Important Links

- GCP Console: https://console.cloud.google.com
- IAM & Service Accounts: https://console.cloud.google.com/iam-admin
- API Library: https://console.cloud.google.com/apis/library
- Firestore: https://console.cloud.google.com/firestore
- BigQuery: https://console.cloud.google.com/bigquery
- Gemini AI Studio: https://aistudio.google.com/app/apikey
- Billing: https://console.cloud.google.com/billing

---

**Last Updated:** [Add date when you complete setup]
**Setup Time:** [Add total time taken]
