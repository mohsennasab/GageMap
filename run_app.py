# run_app.py
import subprocess
import webbrowser
import time

# Start the FastAPI app on port 8502
subprocess.Popen(["uvicorn", "main:app", "--reload", "--host", "127.0.0.1", "--port", "8502"])

# Give the server a moment to start
time.sleep(2)

# Open the browser automatically
webbrowser.open("http://127.0.0.1:8502")
