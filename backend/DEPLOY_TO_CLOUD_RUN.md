# 🚀 Deploy Backend to Cloud Run (genai-486310)

## Quick Deploy from Cloud Console

You're currently in: https://console.cloud.google.com/run?project=genai-486310

### **Option 1: Deploy from GitHub (Recommended)**

1. **Click "Deploy a web service"**

2. **Select "Continuously deploy from a repository"**

3. **Set up with Cloud Build:**
   - Click "SET UP WITH CLOUD BUILD"
   - Select source: **GitHub**
   - Authenticate GitHub
   - Repository: `force2speed/GENAI`
   - Branch: `main`
   - Build Type: **Dockerfile**
   - Source location: `backend/dockerfile`

4. **Configure Service:**
   ```
   Service name: misinfo-backend
   Region: asia-south1
   
   CPU allocation: CPU is only allocated during request processing
   Min instances: 0
   Max instances: 10
   
   Authentication: ☑️ Allow unauthenticated invocations
   ```

5. **Add Environment Variables** (Click "Container, Networking, Security"):
   - Click "Variables & Secrets" tab
   - Add these environment variables:
     ```
     GCP_PROJECT_ID = genai-486310
     ```

6. **Add Secrets** (Important!):
   - First, create secrets in Secret Manager:
     - Go to: https://console.cloud.google.com/security/secret-manager?project=genai-486310
     - Create secret: `GEMINI_API_KEY` with value: `AIzaSyAs1ZkWm-f49GDXarb-oBx5ued5vr-tYSk`
     - Create secret: `SERVICE_ACCOUNT_KEY` - upload your `key.json` file
   
   - Then in Cloud Run deployment:
     - Reference as environment variable:
       ```
       GEMINI_API_KEY → Reference secret: GEMINI_API_KEY:latest
       GOOGLE_APPLICATION_CREDENTIALS → /secrets/SERVICE_ACCOUNT_KEY
       ```

7. **Click "CREATE"**

---

### **Option 2: Deploy from Local (Using gcloud CLI)**

If you have gcloud CLI installed:

```bash
# 1. Set project
gcloud config set project genai-486310

# 2. Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com

# 3. Create secrets (one-time setup)
echo "AIzaSyAs1ZkWm-f49GDXarb-oBx5ued5vr-tYSk" | gcloud secrets create GEMINI_API_KEY --data-file=-
gcloud secrets create SERVICE_ACCOUNT_KEY --data-file=key.json

# 4. Deploy from source
cd "C:\Users\dhruv\Desktop\PERSONAL DATA\PROJECTS\GENAI-combating Misinformation\backend"

gcloud run deploy misinfo-backend \
  --source . \
  --platform managed \
  --region asia-south1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=genai-486310 \
  --update-secrets GEMINI_API_KEY=GEMINI_API_KEY:latest \
  --update-secrets GOOGLE_APPLICATION_CREDENTIALS=SERVICE_ACCOUNT_KEY:latest
```

---

### **Option 3: Quick Manual Deploy (No Secrets Yet)**

If you just want to test deployment quickly:

```bash
cd "C:\Users\dhruv\Desktop\PERSONAL DATA\PROJECTS\GENAI-combating Misinformation\backend"

gcloud run deploy misinfo-backend \
  --source . \
  --platform managed \
  --region asia-south1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=genai-486310 \
  --set-env-vars GEMINI_API_KEY=AIzaSyAs1ZkWm-f49GDXarb-oBx5ued5vr-tYSk
```

⚠️ **Note**: This puts the API key in environment variable (less secure). Use Option 1 or 2 with Secret Manager for production.

---

## 🎯 After Deployment

You'll get a URL like:
```
https://misinfo-backend-<hash>-uc.a.run.app
```

### Update Your Frontend

Update your frontend code to use the new URL instead of:
```
https://misinfo-backend-622658282319.asia-south1.run.app
```

---

## 🔧 Troubleshooting

### "Permission denied" errors
```bash
# Grant Cloud Run Admin role
gcloud projects add-iam-policy-binding genai-486310 \
  --member="user:YOUR_EMAIL@gmail.com" \
  --role="roles/run.admin"
```

### Build fails
- Check dockerfile is correct
- Verify requirements.txt exists
- Check .gcloudignore doesn't exclude necessary files

### Runtime errors
- Check logs: https://console.cloud.google.com/run/detail/asia-south1/misinfo-backend/logs?project=genai-486310
- Verify environment variables are set
- Check Secret Manager permissions

---

## 📊 Monitor Your Service

- **Logs**: https://console.cloud.google.com/run/detail/asia-south1/misinfo-backend/logs?project=genai-486310
- **Metrics**: https://console.cloud.google.com/run/detail/asia-south1/misinfo-backend/metrics?project=genai-486310
- **Revisions**: See deployment history and rollback if needed

---

## ✅ Quick Checklist

- [ ] Secret Manager has GEMINI_API_KEY
- [ ] Secret Manager has SERVICE_ACCOUNT_KEY
- [ ] Cloud Run API enabled
- [ ] Cloud Build API enabled
- [ ] Service deployed successfully
- [ ] Service URL tested (returns 200 OK)
- [ ] Frontend updated with new URL
- [ ] CORS headers working
- [ ] Test misinformation detection endpoint

---

**Choose the option that works best for you!** Option 1 (GitHub) is recommended for production use.
