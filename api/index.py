import sys
import os

# Ensure backend directory is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app

# Export app for Vercel Serverless Execution
handler = app
