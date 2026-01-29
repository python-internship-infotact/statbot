#!/usr/bin/env python3
"""
Integration test for StatBot Pro frontend-backend communication
"""

import requests
import time
import subprocess
import sys
import os
from pathlib import Path

def test_backend_health():
    """Test if backend is running and healthy"""
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_frontend_build():
    """Test if frontend builds successfully"""
    try:
        # Try different npm commands for Windows
        npm_commands = ["npm", "npm.cmd", "npm.exe"]
        
        for npm_cmd in npm_commands:
            try:
                result = subprocess.run(
                    [npm_cmd, "run", "build"], 
                    cwd="frontend", 
                    capture_output=True, 
                    text=True,
                    timeout=120,
                    shell=True  # Use shell on Windows
                )
                if result.returncode == 0:
                    return True
                else:
                    print(f"   Build failed with {npm_cmd}: {result.stderr}")
            except FileNotFoundError:
                continue
            except Exception as e:
                print(f"   Exception with {npm_cmd}: {e}")
                continue
        
        return False
    except Exception as e:
        print(f"   Build exception: {e}")
        return False

def test_api_endpoints():
    """Test basic API endpoints"""
    base_url = "http://localhost:8001"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code != 200:
            return False, "Health endpoint failed"
    except Exception as e:
        return False, f"Health endpoint error: {e}"
    
    # Test CSV upload with sample data
    try:
        # Create a simple test CSV
        test_csv = "name,age,city\nJohn,25,NYC\nJane,30,LA\nBob,35,Chicago"
        files = {'file': ('test.csv', test_csv, 'text/csv')}
        
        response = requests.post(f"{base_url}/upload_csv", files=files)
        if response.status_code != 200:
            return False, f"Upload failed: {response.status_code}"
        
        upload_data = response.json()
        session_id = upload_data.get('session_id')
        
        if not session_id:
            return False, "No session ID returned"
        
        # Test question endpoint
        question_data = {
            "question": "What is the average age?",
            "session_id": session_id
        }
        
        response = requests.post(f"{base_url}/ask_question", json=question_data)
        if response.status_code != 200:
            return False, f"Question failed: {response.status_code}"
        
        return True, "All API tests passed"
        
    except Exception as e:
        return False, f"API test error: {e}"

def main():
    """Run integration tests"""
    print("🧪 StatBot Pro Integration Tests")
    print("=" * 40)
    
    # Test 1: Frontend build
    print("1. Testing frontend build...")
    if test_frontend_build():
        print("   ✅ Frontend builds successfully")
    else:
        print("   ❌ Frontend build failed")
        return False
    
    # Test 2: Backend health (if running)
    print("2. Testing backend health...")
    if test_backend_health():
        print("   ✅ Backend is running and healthy")
        
        # Test 3: API endpoints
        print("3. Testing API endpoints...")
        success, message = test_api_endpoints()
        if success:
            print(f"   ✅ {message}")
        else:
            print(f"   ❌ {message}")
            return False
    else:
        print("   ⚠️  Backend not running (start with 'python main.py')")
        print("   ℹ️  Skipping API tests")
    
    print("\n🎉 Integration tests completed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)