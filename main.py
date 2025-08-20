# main.py
import subprocess
import sys

# Start app.py (Flask/Django/FastAPI server)
flask_process = subprocess.Popen([sys.executable, "app.py"])

# Start bot_host.py (Telegram bot)
bot_process = subprocess.Popen([sys.executable, "bot_host.py"])

# Wait so both processes stay alive
flask_process.wait()
bot_process.wait()
