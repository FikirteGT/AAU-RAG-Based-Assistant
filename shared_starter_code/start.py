import subprocess
import sys
import os

# Start FastAPI backend
backend = subprocess.Popen([
    sys.executable, "-m", "uvicorn", "app:app",
    "--host", "0.0.0.0", "--port", "8000"
])

# Start Streamlit frontend
frontend = subprocess.Popen([
    sys.executable, "-m", "streamlit", "run", "chat.py",
    "--server.port", "7860",
    "--server.address", "0.0.0.0"
])

backend.wait()
frontend.wait()
