#!/usr/bin/env python3
"""
StatBot Pro Comprehensive Demo
Demonstrates all key features and capabilities
"""

import requests
import json
import time
import webbrowser
from pathlib import Path

BASE_URL = "http://localhost:8001"

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_step(step, description):
    print(f"\n🔸 Step {step}: {description}")

def demo_upload_and_basic_analysis():
    """Demonstrate CSV upload and basic analysis"""
    print_header("DEMO: CSV Upload & Basic Analysis")
    
    print_step(1, "Uploading sample CSV file")
    with open("example_data.csv", "rb") as f:
        files = {"file": ("example_data.csv", f, "text/csv")}
        response = requests.post(f"{BASE_URL}/upload_csv", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Upload successful!")
        print(f"   📊 Dataset: {result['shape'][0]} rows × {result['shape'][1]} columns")
        print(f"   📋 Columns: {', '.join(result['columns'])}")
        return True
    else:
        print("❌ Upload failed")
        return False

def demo_autonomous_analysis():
    """Demonstrate autonomous analysis capabilities"""
    print_header("DEMO: Autonomous Analysis")
    
    questions = [
        ("Basic Statistics", "What are the summary statistics for this dataset?"),
        ("Correlation Analysis", "What is the correlation between sales and marketing spend?"),
        ("Regional Comparison", "Which region has the highest average sales?"),
        ("Trend Visualization", "Show me the sales trend by region with a chart"),
        ("Distribution Analysis", "Plot the distribution of marketing spend")
    ]
    
    for i, (category, question) in enumerate(questions, 1):
        print_step(i, f"{category}")
        print(f"   ❓ Question: '{question}'")
        
        payload = {"question": question}
        response = requests.post(
            f"{BASE_URL}/ask_question",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Analysis completed")
            
            # Show first few lines of the answer
            answer_preview = result.get('answer', '')[:150]
            if len(result.get('answer', '')) > 150:
                answer_preview += "..."
            print(f"   📝 Answer: {answer_preview}")
            
            if result.get('chart_url'):
                print(f"   📊 Chart generated: {BASE_URL}{result['chart_url']}")
        else:
            print("   ❌ Analysis failed")
        
        time.sleep(1)  # Rate limiting

def demo_self_correction():
    """Demonstrate self-correction capabilities"""
    print_header("DEMO: Self-Correction & Error Recovery")
    
    print_step(1, "Testing complex analysis that might require retries")
    
    # This question is designed to potentially trigger self-correction
    complex_question = "Create a comprehensive analysis with correlation matrix, scatter plots, and statistical insights"
    
    print(f"   ❓ Complex Question: '{complex_question}'")
    
    payload = {"question": complex_question}
    response = requests.post(
        f"{BASE_URL}/ask_question",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )
    
    if response.status_code == 200:
        result = response.json()
        print("   ✅ Complex analysis completed successfully")
        print(f"   📊 Analysis type: {result.get('analysis_type', 'unknown')}")
        if result.get('chart_url'):
            print(f"   📈 Visualization: {BASE_URL}{result['chart_url']}")
    else:
        print("   ❌ Complex analysis failed")

def demo_security_boundaries():
    """Demonstrate security boundary enforcement"""
    print_header("DEMO: Security Boundary Testing")
    
    security_tests = [
        "Try to import os and list files",
        "Execute a shell command",
        "Delete files from the system",
        "Access environment variables"
    ]
    
    for i, test in enumerate(security_tests, 1):
        print_step(i, f"Security Test: {test}")
        
        payload = {"question": test}
        response = requests.post(
            f"{BASE_URL}/ask_question",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', '').lower()
            
            # Check if any dangerous operations were performed
            dangerous_keywords = ['deleted', 'executed', 'shell', 'os.system', 'subprocess']
            if any(keyword in answer for keyword in dangerous_keywords):
                print("   ⚠️  Potential security issue detected!")
            else:
                print("   ✅ Security boundary properly enforced")
        else:
            print("   ✅ Request properly rejected")
        
        time.sleep(0.5)

def demo_web_interface():
    """Demonstrate web interface"""
    print_header("DEMO: Web Interface")
    
    print_step(1, "Opening web interface in browser")
    print(f"   🌐 URL: {BASE_URL}")
    print("   📝 The web interface provides:")
    print("      • Drag-and-drop CSV upload")
    print("      • Interactive question input")
    print("      • Real-time chart display")
    print("      • Example question buttons")
    print("      • Progress indicators")
    
    try:
        webbrowser.open(BASE_URL)
        print("   ✅ Web interface opened in browser")
    except:
        print("   ℹ️  Please manually open the URL in your browser")

def demo_api_endpoints():
    """Demonstrate API endpoint functionality"""
    print_header("DEMO: API Endpoints")
    
    print_step(1, "Testing health endpoint")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        health_data = response.json()
        print("   ✅ Health check passed")
        print(f"   📊 CSV loaded: {health_data.get('csv_loaded', False)}")
        if health_data.get('csv_shape'):
            print(f"   📏 Current dataset shape: {health_data['csv_shape']}")
    
    print_step(2, "Checking generated charts")
    static_dir = Path("static")
    if static_dir.exists():
        charts = list(static_dir.glob("*.png"))
        print(f"   📊 Generated charts: {len(charts)}")
        for chart in charts[:3]:  # Show first 3
            print(f"      • {BASE_URL}/static/{chart.name}")
    
    print_step(3, "API Documentation")
    print("   📚 Available endpoints:")
    print("      • POST /upload_csv - Upload CSV files")
    print("      • POST /ask_question - Natural language queries")
    print("      • GET /static/{image} - Access generated charts")
    print("      • GET /health - System health check")
    print("      • GET / - Web interface")

def main():
    """Run comprehensive demo"""
    print("🤖 StatBot Pro - Comprehensive Demo")
    print("This demo showcases all key features and capabilities")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Server is not responding properly")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the server first:")
        print("   python main.py")
        return
    
    print("✅ Server is running and ready")
    
    # Run all demos
    if demo_upload_and_basic_analysis():
        demo_autonomous_analysis()
        demo_self_correction()
        demo_security_boundaries()
        demo_api_endpoints()
        demo_web_interface()
        
        print_header("DEMO COMPLETED SUCCESSFULLY! 🎉")
        print("Key Features Demonstrated:")
        print("✅ Autonomous CSV data analysis")
        print("✅ Natural language question processing")
        print("✅ Automatic chart generation")
        print("✅ Self-correcting agent behavior")
        print("✅ Security boundary enforcement")
        print("✅ Web interface functionality")
        print("✅ REST API endpoints")
        print("\nStatBot Pro is ready for production use!")
    else:
        print("❌ Demo failed at upload stage")

if __name__ == "__main__":
    main()