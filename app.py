"""
Root entry point for Hugging Face Spaces deployment.
Deploy with: streamlit run app.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# Load and run Phase 6 chat UI (executes streamlit code)
import phase6_chatbot.app  # noqa: F401
