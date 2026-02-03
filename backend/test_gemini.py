#!/usr/bin/env python3
"""Test Gemini API directly to diagnose the issue"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY not found in environment")
    sys.exit(1)

print(f"✅ API Key found: {GEMINI_API_KEY[:10]}...")

try:
    # Configure Gemini
    print("\n🔧 Configuring Gemini API...")
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Try the updated model
    print("🤖 Testing gemini-2.5-flash model...")
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    # Simple test
    prompt = """Extract factual claims from this text:
    
    "The earth is flat and NASA is lying to us"
    
    Return a JSON array like: ["claim 1", "claim 2"]"""
    
    print("\n📤 Sending test request...")
    response = model.generate_content(prompt)
    
    print("\n✅ Response received!")
    print(f"\n📝 Response text:\n{response.text}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
