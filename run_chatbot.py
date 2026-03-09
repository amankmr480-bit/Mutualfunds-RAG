"""
Launch Phase 6 Streamlit chatbot from project root.
Usage: python run_chatbot.py
       or: streamlit run phase6_chatbot/app.py
"""
import subprocess
import sys
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent
    app = root / "phase6_chatbot" / "app.py"
    if not app.exists():
        print("Not found:", app)
        sys.exit(1)
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app), "--server.headless", "true"], cwd=root)

if __name__ == "__main__":
    main()
