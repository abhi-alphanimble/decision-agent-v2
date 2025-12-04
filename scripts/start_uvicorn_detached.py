import subprocess
import sys
import time

proc = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'])
print(proc.pid)
sys.stdout.flush()
# Give server a moment to start
for _ in range(10):
    time.sleep(0.5)

# Keep the script running while the server runs; parent will manage process.
# This script will exit immediately after printing PID; server remains.
