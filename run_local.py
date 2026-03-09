"""
Run the full RAG chatbot locally for manual testing.
- Loads .env (GROQ_API_KEY).
- Optionally runs full refresh (Phase 1→2→3).
- Checks pipeline ready, then launches Streamlit chat UI.

Usage:
  python run_local.py              # Start chat (use existing data)
  python run_local.py --refresh   # Refresh data then start chat
  python run_local.py --check     # Only check if pipeline is ready
"""
import argparse
import sys
from pathlib import Path

# Project root
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load .env first
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass


def main():
    parser = argparse.ArgumentParser(description="Run ICICI Prudential MF RAG chatbot locally")
    parser.add_argument("--refresh", action="store_true", help="Run full data refresh (Phase 1→2→3) before starting chat")
    parser.add_argument("--check", action="store_true", help="Only check pipeline readiness and exit")
    args = parser.parse_args()

    if args.check:
        from phase7_operations.monitoring import check_pipeline_ready
        info = check_pipeline_ready()
        print("Pipeline readiness:", info)
        sys.exit(0 if info.get("ready") else 1)

    if args.refresh:
        print("Running full refresh (Phase 1 -> 2 -> 3)...")
        from phase7_operations.refresh_pipeline import run_full_refresh
        if not run_full_refresh():
            print("Refresh failed. Fix errors and try again.")
            sys.exit(1)
        print("Refresh done. Starting chat UI...")

    # Check ready
    from phase7_operations.monitoring import check_pipeline_ready
    info = check_pipeline_ready()
    if not info.get("ready"):
        print("Pipeline not ready. Run with --refresh to scrape and index data first.")
        print("Checks:", info.get("checks", {}))
        sys.exit(1)

    # Launch Streamlit
    import subprocess
    app_path = ROOT / "phase6_chatbot" / "app.py"
    if not app_path.exists():
        print("Not found:", app_path)
        sys.exit(1)
    print("Opening chat UI at http://localhost:8501 (press Ctrl+C to stop)")
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path), "--server.headless", "true"], cwd=ROOT)


if __name__ == "__main__":
    main()
