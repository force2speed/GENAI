#!/bin/bash
# Deploy Backend to Cloud Run on New GCP Project

echo "============================================"
echo "  Deploy to Cloud Run (genai-486310)"
echo "============================================"
echo ""

PROJECT_ID="genai-486310"
SERVICE_NAME="misinfo-backend"
REGION="asia-south1"  # Same region as your old deployment

echo "Project ID: $PROJECT_ID"
echo "Service Name: $SERVICE_NAME"
echo "Region: $REGION"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found!"
    echo ""
    echo "You have 2 options:"
    echo ""
    echo "Option A: Install gcloud CLI"
    echo "  Download from: https://cloud.google.com/sdk/docs/install"
    echo ""
    echo "Option B: Use Cloud Shell in GCP Console"
    echo "  1. Go to: https://console.cloud.google.com"
    echo "  2. Click the Cloud Shell icon (>_) in top right"
    echo "  3. Upload your code and run this script"
    exit 1
fi

echo "Step 1: Set project..."
gcloud config set project $PROJECT_ID

echo ""
echo "Step 2: Enable Cloud Run API..."
gcloud services enable run.googleapis.com

echo ""
echo "Step 3: Building and deploying..."
gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars="GEMINI_API_KEY=$GEMINI_API_KEY" \
  --set-env-vars="GOOGLE_APPLICATION_CREDENTIALS=/app/key.json" \
  --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID"

echo ""
echo "============================================"
echo "  Deployment Complete!"
echo "============================================"
echo ""
echo "Your new Cloud Run URL will be displayed above."
echo "Update your frontend to use the new URL."
