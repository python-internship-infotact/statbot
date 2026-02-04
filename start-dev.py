#!/usr/bin/env python3
"""
Development startup script for StatBot Pro
Starts both backend and frontend servers concurrently
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def check_env_file():
    """Check if .env file exists and create from example if not"""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from .env.example...")
        env_file.write_text(env_example.read_text())
        print("✅ .env file created. You can edit it to customize settings.")
    elif not env_file.exists():
        print("⚠️  No .env file found. Using default environment variables.")
    else:
        print("✅ .env file found.")

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting backend server...")
    env = os.environ.copy()
    env['ENVIRONMENT'] = 'development'
    return subprocess.Popen([
        sys.executable, 'main.py'
    ], env=env)

def start_frontend():
    """Start the React frontend development server"""
    print("🎨 Starting frontend server...")
    frontend_dir = Path('frontend')
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        return None
    
    # Check if node_modules exists
    if not (frontend_dir / 'node_modules').exists():
        print("📦 Installing frontend dependencies...")
        subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
    
    return subprocess.Popen([
        'npm', 'run', 'dev'
    ], cwd=frontend_dir)

def main():
    """Main function to start both servers"""
    print("🔥 Starting StatBot Pro Development Environment")
    print("=" * 50)
    
    # Check and setup .env file
    check_env_file()
    
    processes = []
    
    try:
        # Start backend
        backend_process = start_backend()
        if backend_process:
            processes.append(backend_process)
            time.sleep(2)  # Give backend time to start
        
        # Start frontend
        frontend_process = start_frontend()
        if frontend_process:
            processes.append(frontend_process)
        
        print("\n✅ Both servers started successfully!")
        print("🔗 Backend API: http://localhost:8001")
        print("🌐 Frontend UI: http://localhost:8080")
        print("\nPress Ctrl+C to stop both servers")
        
        # Wait for processes
        for process in processes:
            process.wait()
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        print("✅ Servers stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        for process in processes:
            try:
                process.terminate()
            except:
                pass
        sys.exit(1)

if __name__ == "__main__":
    main()