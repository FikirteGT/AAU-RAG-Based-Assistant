import subprocess
import sys
import threading

def run_backend():
    subprocess.run([
        sys.executable, "-m", "uvicorn", "app:app",
        "--host", "0.0.0.0", "--port", "8000"
    ])

def run_frontend():
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "chat.py",
        "--server.port", "7860",
        "--server.address", "0.0.0.0"
    ])

if __name__ == "__main__":
    t1 = threading.Thread(target=run_backend)
    t2 = threading.Thread(target=run_frontend)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
