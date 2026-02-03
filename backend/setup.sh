#!/bin/bash
# Quick Setup Script for Git Bash on Windows
# Run this after completing GCP console setup

echo "============================================================"
echo "  GCP Backend Setup - Windows Quick Start"
echo "============================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo "Checking Python installation..."
if command -v py &> /dev/null; then
    echo -e "${GREEN}✓${NC} Python found: $(py --version)"
else
    echo -e "${RED}✗${NC} Python not found!"
    echo "Please install Python from https://www.python.org/downloads/"
    exit 1
fi

# Check Node.js
echo ""
echo "Checking Node.js installation..."
if command -v node &> /dev/null; then
    echo -e "${GREEN}✓${NC} Node.js found: $(node --version)"
else
    echo -e "${RED}✗${NC} Node.js not found!"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if key.json exists
echo ""
echo "Checking for service account key..."
if [ -f "key.json" ]; then
    echo -e "${GREEN}✓${NC} key.json found"
    # Check if it's valid JSON
    if py -c "import json; json.load(open('key.json'))" 2>/dev/null; then
        PROJECT_ID=$(py -c "import json; print(json.load(open('key.json'))['project_id'])")
        echo -e "  Project ID: ${GREEN}${PROJECT_ID}${NC}"
    else
        echo -e "${RED}✗${NC} key.json is not valid JSON"
        exit 1
    fi
else
    echo -e "${RED}✗${NC} key.json NOT found!"
    echo ""
    echo "Please download your service account key:"
    echo "1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts?project=genai-486310"
    echo "2. Create service account or select existing one"
    echo "3. Create key (JSON format)"
    echo "4. Save as key.json in this directory"
    exit 1
fi

# Check if .env exists
echo ""
echo "Checking environment configuration..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file found"
    if grep -q "GEMINI_API_KEY=" .env && ! grep -q "GEMINI_API_KEY=your-" .env; then
        echo -e "${GREEN}✓${NC} GEMINI_API_KEY is set"
    else
        echo -e "${YELLOW}⚠${NC} GEMINI_API_KEY needs to be configured"
        echo "  Get your API key from: https://aistudio.google.com/app/apikey"
    fi
else
    echo -e "${YELLOW}⚠${NC} .env file not found"
    echo "Creating .env template..."
    cat > .env << EOF
GOOGLE_APPLICATION_CREDENTIALS=C:/Users/dhruv/Desktop/PERSONAL DATA/PROJECTS/GENAI-combating Misinformation/backend/key.json
GEMINI_API_KEY=your-gemini-api-key-here
GCP_PROJECT_ID=${PROJECT_ID}
EOF
    echo -e "${GREEN}✓${NC} .env file created"
    echo -e "${YELLOW}⚠${NC} Please edit .env and add your GEMINI_API_KEY"
    echo "  Get it from: https://aistudio.google.com/app/apikey"
fi

# Install Python dependencies
echo ""
echo "============================================================"
echo "  Installing Python Dependencies"
echo "============================================================"
echo ""
py -m pip install --upgrade pip
py -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Python packages installed successfully"
else
    echo -e "${RED}✗${NC} Failed to install Python packages"
    exit 1
fi

# Install Node.js dependencies
echo ""
echo "============================================================"
echo "  Installing Node.js Dependencies"
echo "============================================================"
echo ""
npm install

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Node.js packages installed successfully"
else
    echo -e "${RED}✗${NC} Failed to install Node.js packages"
    exit 1
fi

# Run verification
echo ""
echo "============================================================"
echo "  Running Setup Verification"
echo "============================================================"
echo ""
py verify_setup.py

# Final message
echo ""
echo "============================================================"
echo "  Setup Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Make sure your .env file has the correct GEMINI_API_KEY"
echo "2. Verify all GCP services are enabled:"
echo "   - Cloud Vision API"
echo "   - Cloud Speech-to-Text API"
echo "   - Firestore"
echo "   - BigQuery"
echo "3. Run the application:"
echo "   ${GREEN}py app.py${NC}"
echo ""
echo "For detailed setup instructions, see:"
echo "  - GCP_MIGRATION_GUIDE.md (complete guide)"
echo "  - WINDOWS_SETUP_GUIDE.md (Windows-specific)"
echo "  - BIGQUERY_SETUP.md (BigQuery setup)"
echo ""
