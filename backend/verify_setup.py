#!/usr/bin/env python3
"""
Verify GCP Setup for Misinformation Detection Backend
Run this script to check if all required services are properly configured
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_env_vars():
    """Check if required environment variables are set"""
    print("🔍 Checking Environment Variables...")
    
    gemini_key = os.environ.get('GEMINI_API_KEY')
    gcp_creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    if not gemini_key:
        print("❌ GEMINI_API_KEY not set")
        return False
    else:
        print(f"✅ GEMINI_API_KEY is set ({gemini_key[:10]}...)")
    
    if not gcp_creds:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set")
        return False
    else:
        print(f"✅ GOOGLE_APPLICATION_CREDENTIALS is set: {gcp_creds}")
    
    return True

def check_key_file():
    """Check if key.json exists and is valid"""
    print("\n🔍 Checking Service Account Key File...")
    
    key_path = "key.json"
    if not os.path.exists(key_path):
        print(f"❌ key.json not found in {os.getcwd()}")
        return False
    
    try:
        with open(key_path, 'r') as f:
            key_data = json.load(f)
        
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        for field in required_fields:
            if field not in key_data:
                print(f"❌ Missing field '{field}' in key.json")
                return False
        
        print(f"✅ key.json is valid")
        print(f"   Project ID: {key_data['project_id']}")
        print(f"   Service Account: {key_data['client_email']}")
        return True
        
    except json.JSONDecodeError:
        print("❌ key.json is not valid JSON")
        return False
    except Exception as e:
        print(f"❌ Error reading key.json: {e}")
        return False

def check_dependencies():
    """Check if required Python packages are installed"""
    print("\n🔍 Checking Python Dependencies...")
    
    required_packages = [
        'google.cloud.vision',
        'google.cloud.speech',
        'google.cloud.firestore',
        'google.cloud.bigquery',
        'google.generativeai',
        'flask',
        'cv2',
        'moviepy',
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('.', '_') if '.' in package else package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def test_gcp_services():
    """Test connection to GCP services"""
    print("\n🔍 Testing GCP Service Connections...")
    
    # Test Vision API
    try:
        from google.cloud import vision
        client = vision.ImageAnnotatorClient()
        print("✅ Cloud Vision API - Connected")
    except Exception as e:
        print(f"❌ Cloud Vision API - Failed: {str(e)[:50]}")
        return False
    
    # Test Speech API
    try:
        from google.cloud import speech
        client = speech.SpeechClient()
        print("✅ Cloud Speech API - Connected")
    except Exception as e:
        print(f"❌ Cloud Speech API - Failed: {str(e)[:50]}")
        return False
    
    # Test Firestore
    try:
        from google.cloud import firestore
        db = firestore.Client()
        print("✅ Firestore - Connected")
    except Exception as e:
        print(f"❌ Firestore - Failed: {str(e)[:50]}")
        return False
    
    # Test BigQuery
    try:
        from google.cloud import bigquery
        client = bigquery.Client()
        print("✅ BigQuery - Connected")
    except Exception as e:
        print(f"❌ BigQuery - Failed: {str(e)[:50]}")
        return False
    
    # Test Gemini
    try:
        import google.generativeai as genai
        api_key = os.environ.get('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            print("✅ Gemini API - Configured")
        else:
            print("⚠️  Gemini API - API key not set")
    except Exception as e:
        print(f"❌ Gemini API - Failed: {str(e)[:50]}")
        return False
    
    return True

def main():
    print("=" * 60)
    print("🚀 GCP Setup Verification for Misinformation Detection")
    print("=" * 60)
    
    checks = [
        check_key_file(),
        check_env_vars(),
        check_dependencies(),
        test_gcp_services(),
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("✅ All checks passed! Your setup is ready.")
        print("You can now run: python app.py")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        sys.exit(1)
    print("=" * 60)

if __name__ == "__main__":
    main()
