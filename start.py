"""
FinPilot Application Launcher
Launches both FastAPI backend and Vite frontend development server.
"""

import subprocess
import sys
import time
import os

def run():
    print("=" * 60)
    print("      FinPilot: Personal Finance Decision Support Agent     ")
    print("=" * 60)
    
    root_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(root_dir, "frontend")
    
    print("\n[1/2] Starting FastAPI Backend on http://127.0.0.1:8000...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
        cwd=root_dir
    )
    
    time.sleep(2)
    
    print("\n[2/2] Starting React Vite Frontend on http://localhost:3000...")
    frontend_proc = subprocess.Popen(
        ["npm.cmd" if os.name == "nt" else "npm", "run", "dev"],
        cwd=frontend_dir
    )

    print("\n" + "=" * 60)
    print("  🚀 FinPilot is RUNNING!")
    print("  • Frontend Dashboard: http://localhost:3000")
    print("  • Backend API Docs:   http://127.0.0.1:8000/docs")
    print("=" * 60 + "\n")

    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping FinPilot servers...")
        backend_proc.terminate()
        frontend_proc.terminate()

if __name__ == "__main__":
    run()
